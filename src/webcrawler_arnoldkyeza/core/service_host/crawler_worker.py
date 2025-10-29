import asyncio
import datetime
import logging
from dataclasses import dataclass
from typing import List, Optional

from webcrawler_arnoldkyeza.core.datastore.blob_storage import BlobStorage
from webcrawler_arnoldkyeza.core.datastore.databasemanager import DatabaseManager
from webcrawler_arnoldkyeza.core.duplicate_eliminator.duplicate_eliminator import DuplicateEliminator
from webcrawler_arnoldkyeza.core.enums.url_status_type import UrlStatusType
from webcrawler_arnoldkyeza.core.extractor.content_parser.textual_parser import TextualParser
from webcrawler_arnoldkyeza.core.extractor.extractor import Extractor
from webcrawler_arnoldkyeza.core.html_fetcher.protocol_handlers.http_handler import HTTPProtocolHandler
from webcrawler_arnoldkyeza.core.scheduler.models.url import Url
from webcrawler_arnoldkyeza.core.scheduler.scheduler import Scheduler
from webcrawler_arnoldkyeza.core.html_fetcher.html_fetcher import HTMLFetcher
from webcrawler_arnoldkyeza.core.utils import calculate_text_checksum

logger = logging.getLogger(__name__)


@dataclass
class CrawlerWorker:
    worker_id: int
    scheduler: Scheduler
    duplicate_eliminator: DuplicateEliminator
    database_manager: DatabaseManager
    blob_storage: BlobStorage

    async def run(self) -> None:
        while not self.scheduler.finished():
            depth, url = await self.scheduler.get_next_url()
            if url is None:
                await asyncio.sleep(0.01)  # wait for 10 milliseconds
                continue

            try:
                logger.debug(f"Worker {self.worker_id}: processing URL: {url}")
                self.database_manager.update_url_status(url, UrlStatusType.IN_PROGRESS)

                content = await HTMLFetcher(HTTPProtocolHandler()).fetch(url)
                result = Extractor(TextualParser()).extract(content)
                logger.debug(f"Worker {self.worker_id}: successfully extracted content from {url}")

                if not self.duplicate_eliminator.is_duplicate_content(result.content):
                    file_name = f"{calculate_text_checksum(url)}.txt"
                    self.blob_storage.upload(container="text_html", blob_name=file_name,
                                             data=result.content.encode('utf-8'))

                next_depth = depth + 1
                parent: Optional[Url] = self.database_manager.get_url(url)
                if parent is None:
                    continue
                filtered_urls: List[Url] = self.duplicate_eliminator.filter_extracted_urls(
                    result.extracted_urls,
                    parent_url_id=parent.url_id,
                    depth=next_depth
                )
                await self.scheduler.enqueue_many(filtered_urls)

                last_crawled_at = datetime.datetime.now()
                self.database_manager.mark_url_as_crawled(url, last_crawled_at)

            except Exception as e:
                logger.error(f"Worker {self.worker_id}: error crawling url: {url} - {e}")
                self.database_manager.update_url_on_failed(url, str(e))
            finally:
                self.scheduler.queue_task_done()
