import asyncio
import logging
from dataclasses import dataclass
from typing import List

from webcrawler_arnoldkyeza.core.commandline_options import CrawlerConfig
from webcrawler_arnoldkyeza.core.datastore.blob_storage import BlobStorage
from webcrawler_arnoldkyeza.core.datastore.databasemanager import DatabaseManager
from webcrawler_arnoldkyeza.core.duplicate_eliminator.duplicate_eliminator import DuplicateEliminator
from webcrawler_arnoldkyeza.core.scheduler.scheduler import Scheduler
from webcrawler_arnoldkyeza.core.service_host.crawler_worker import CrawlerWorker

logger = logging.getLogger(__name__)


@dataclass
class ServiceHost:
    scheduler: Scheduler
    deduplicator: DuplicateEliminator
    database: DatabaseManager
    blob_storage: BlobStorage

    async def crawl(self, config: CrawlerConfig) -> None:
        try:
            await self.scheduler.initialize(config.start_url, config.max_depth)
            logging.info(f"Scheduler initialized with seed URL: {config.start_url} and max depth: {config.max_depth}")

            workers: List[asyncio.Task] = []
            for worker_id in range(config.number_of_workers):
                worker = CrawlerWorker(worker_id + 1, self.scheduler, self.deduplicator, self.database,
                                       self.blob_storage)
                workers.append(asyncio.create_task(worker.run()))

            try:
                while not self.scheduler.finished():
                    await asyncio.sleep(0.01)
            finally:

                await self.scheduler.completing_in_progress_crawling()
                logging.info("All crawling workers are completed")

                for worker in workers:
                    worker.cancel()
                await asyncio.gather(*workers, return_exceptions=True)
                logging.info("All workers stopped")
                logger.info(f"Finished crawling with max depth: {config.max_depth}")
        except Exception as e:
            logger.error(f"Error during crawling: {e}")
