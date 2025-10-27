from dataclasses import dataclass, field

from core.commandline_options import CrawlerConfig
from core.datastore.databasemanager import DatabaseManager
from core.dns_resolver.dns_resolver import DNSResolver
from core.scheduler.scheduler import Scheduler


@dataclass
class ServiceHost:
    scheduler: Scheduler
    dsn_resolver: DNSResolver
    database: DatabaseManager


    async def crawl(self, config: CrawlerConfig) -> None:
        await self.scheduler.initialize(config.start_url)


