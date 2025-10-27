from dataclasses import dataclass, field

from core.datastore.database import Database
from core.dns_resolver.dns_resolver import DNSResolver
from core.scheduler.scheduler import Scheduler


@dataclass
class Crawler:
    seed_url: str
    scheduler: Scheduler
    dsn_resolver: DNSResolver
    database: Database
    max_depth: int = field(default=3)


    async def crawl(self):
        await self.scheduler.enqueue_url(self.seed_url)
        workers = []
        for worker_id in range(4):

