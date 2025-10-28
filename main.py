import asyncio
import logging
import sys

import fakeredis

from core.commandline_options import parse_command_line_options, CrawlerConfig
from core.crawler_logging import setup_logging
from core.datastore.blob_storage import BlobStorage
from core.datastore.databasemanager import DatabaseManager
from core.duplicate_eliminator.duplicate_eliminator import DuplicateEliminator
from core.scheduler.models.url_frontier import UrlFrontier
from core.scheduler.scheduler import Scheduler
from core.service_host.service_host import ServiceHost


def build_components(options: CrawlerConfig) -> ServiceHost:
    logging.info("Building Service Host")

    database_backend = DatabaseManager(path=options.database)  # placeholder for actual DB connection
    logging.info("Database backend initialized at %s", options.database)

    redis_backend = fakeredis.FakeStrictRedis()  # placeholder for actual Redis connection
    logging.info("Redis backend initialized")

    blob_storage = BlobStorage(root_path=options.blob_storage_path)
    logging.info("Blob Storage initialized at %s", options.blob_storage_path)

    deduplicator = DuplicateEliminator(redis=redis_backend)
    logging.info("Duplicate Eliminator initialized")

    scheduler = Scheduler(
        url_frontier=UrlFrontier(),
        database_manager=database_backend,
        duplicate_eliminator=deduplicator
    )

    return ServiceHost(
        scheduler=scheduler,
        deduplicator=deduplicator,
        database=database_backend,
        blob_storage=blob_storage
    )


def main(argv: list[str]) -> None:
    options = parse_command_line_options(argv)
    setup_logging(options.log_level)
    crawler = build_components(options)
    asyncio.run(crawler.crawl(options))


if __name__ == "__main__":
    main(sys.argv[1:])
