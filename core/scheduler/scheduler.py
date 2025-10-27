"""
Scheduler:
    This responsible to queuing urls to be crawled on a priority basis

Requires:
    - URL Frontier: a priority queue to host URLs that are made ready for crawling based on two properties associated
                    with each entry:
                    - Priority: this can be based on factors such as s the importance of the website, domain authority
                                or user-defined preferences. For example: URLs, from popular or frequently updated
                                websites may get a higher priority.
                    - Updates Frequency: this depends on how often the content on the URL is expected to change.

    - RDB: stores all the URLs along with the two associated properties mentioned above.
                    Database inputs sources include:
                    - User added URLs
                    - Crawler extracted URLs

Implementation work-flow:
- receive a URL from a source
- normalize the URL
- pass it through the Duplicate Eliminator Component, which performs checksum comparisons against existing URLs
- Discard if it's duplicate
- Add to RDB with URL metadata, priority and update frequency
- Enqueue the URL to the URL Frontier
"""
from dataclasses import dataclass, field

from core.commandline_options import CrawlerConfig
from core.datastore.databasemanager import DatabaseManager
from core.duplicate_eliminator.duplicate_eliminator import DuplicateEliminator
from core.enums.url_status_type import UrlStatusType
from core.scheduler.models.url import Url
from core.scheduler.models.url_frontier import UrlFrontier
from core.utils import normalize_url, is_same_subdomain

MAX_FETCH_COUNT = 10000


@dataclass
class Scheduler:
    url_frontier: UrlFrontier
    database_manager: DatabaseManager
    duplicate_eliminator: DuplicateEliminator
    seed_url: str = field(init=False)

    async def initialize(self, seed_url: str) -> None:
        self.seed_url = seed_url
        pending_urls = self.database_manager.get_pending_urls(limit=MAX_FETCH_COUNT)
        await self.enqueue_url(seed_url)
        for url_entry in pending_urls:
            await self.url_frontier.queue.put((url_entry.priority, url_entry.normalized_url))

    async def enqueue_url(self, url: str):
        normalized_url = normalize_url(url)
        if normalized_url is None:
            return

        if not is_same_subdomain(self.seed_url, normalized_url):
            return

        if self.is_url_duplicate(normalized_url):
            return

        new_url_entry = Url(
            url=url,
            normalized_url=normalized_url,
            checksum=DuplicateEliminator.calculate_checksum(normalized_url),
            priority=1,  # ideally, this should be based on the importance of the website
            update_frequency=1, # ideally, this should be based on how often the content on the URL is expected to change
        )

        self.database_manager.insert_url(new_url_entry)
        await self.url_frontier.queue.put((new_url_entry.priority, new_url_entry.normalized_url))

    def is_url_duplicate(self, normalized_url: str) -> bool:
        return self.duplicate_eliminator.is_duplicate_url(normalized_url)
