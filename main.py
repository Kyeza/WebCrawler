import asyncio
import logging

import fakeredis

from core.commandline_options import parse_command_line_options, CrawlerConfig
from core.crawler_logging import setup_logging
from core.datastore.databasemanager import DatabaseManager
from core.dns_resolver.dns_resolver import DNSResolver
from core.duplicate_eliminator.duplicate_eliminator import DuplicateEliminator
from core.scheduler.models.url_frontier import UrlFrontier
from core.scheduler.scheduler import Scheduler
from core.service_host.service_host import ServiceHost


def build_components(options: CrawlerConfig) -> ServiceHost:
    logging.info("Building Service Host")

    database_backend = DatabaseManager(path=options.database) # placeholder for actual DB connection
    logging.info("Database backend initialized at %s", options.database)

    redis_backend = fakeredis.FakeStrictRedis() # placeholder for actual Redis connection
    logging.info("Redis backend initialized")

    deduplicator = DuplicateEliminator(redis_backend=redis_backend)
    logging.info("Duplicate Eliminator initialized")

    scheduler = Scheduler(
        url_frontier=UrlFrontier(),
        database_manager=database_backend,
        duplicate_eliminator=deduplicator
    )
    logging.info("Scheduler initialized with seed URL: %s", options.start_url)

    return ServiceHost(
        scheduler=scheduler,
        dsn_resolver=DNSResolver(),
        database=DatabaseManager()
    )


def main(argv: list[str]) -> None:
    options = parse_command_line_options(argv)
    setup_logging(options.log_level)


    crawler = build_components(options)
    asyncio.run(crawler.crawl(options))


if __name__ == "__main__":
    main()
