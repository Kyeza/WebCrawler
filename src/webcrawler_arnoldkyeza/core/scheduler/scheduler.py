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
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Optional, Tuple, List

from webcrawler_arnoldkyeza.core.datastore.databasemanager import DatabaseManager
from webcrawler_arnoldkyeza.core.duplicate_eliminator.duplicate_eliminator import DuplicateEliminator
from webcrawler_arnoldkyeza.core.scheduler.models.url import Url
from webcrawler_arnoldkyeza.core.scheduler.models.url_frontier import UrlFrontier
from webcrawler_arnoldkyeza.core.utils import normalize_url, is_same_subdomain

logger = logging.getLogger(__name__)

MAX_FETCH_COUNT = 10000


@dataclass
class Scheduler:
    url_frontier: UrlFrontier
    database_manager: DatabaseManager
    duplicate_eliminator: DuplicateEliminator
    seed_url: str = field(init=False)
    _max_depth: int = field(init=False, default=50)
    _current_depth: int = field(init=False, default=0)

    async def initialize(self, seed_url: str, max_depth: Optional[int] = None) -> None:
        try:
            self.seed_url = seed_url
            self._max_depth = int(max_depth) if max_depth is not None else self._max_depth
            pending_urls: List[Url] = self.database_manager.get_pending_urls(limit=MAX_FETCH_COUNT)
            await self.enqueue_url(seed_url)
            for url_entry in pending_urls:
                await self.url_frontier.queue.put((url_entry.priority, url_entry.normalized_url))
        except ValueError as e:
            logger.error(f"Invalid max_depth value: {e}")
            raise e

    async def enqueue_url(self, url: str, depth: int = 0) -> None:
        normalized_url = normalize_url(url)
        if normalized_url is None:
            return

        if not is_same_subdomain(self.seed_url, normalized_url):
            return

        if depth > self._max_depth:
            return

        if self.is_url_duplicate(normalized_url):
            return

        url_entry = Url(
            url=url,
            normalized_url=normalized_url,
            depth=depth,
        )

        self.database_manager.insert_url(url_entry)
        await self.url_frontier.queue.put((url_entry.depth, url_entry.normalized_url))
        logger.debug(f"Added URL to queue: {url}")

    def is_url_duplicate(self, normalized_url: str) -> bool:
        return self.duplicate_eliminator.is_duplicate_url(normalized_url)

    async def get_next_url(self) -> Tuple[Optional[int], Optional[str]]:
        if self.finished():
            return None, None

        try:
            depth, url = await asyncio.wait_for(self.url_frontier.queue.get(), timeout=1.0)
            if depth > self._current_depth:
                self.update_depth(depth)
            return depth, url
        except asyncio.TimeoutError as e:
            if self.url_frontier.queue.empty():
                logger.debug("Queue is empty")
            else:
                logger.error(f"Error getting next url: {e}")
            return None, None

    async def enqueue_many(self, filtered_urls: List[Url]):
        for url in filtered_urls:
            # only enqueue urls from the same subdomain
            if not is_same_subdomain(self.seed_url, url.normalized_url):
                continue
            if url.depth > self._max_depth:
                continue
            self.database_manager.insert_url(url)
            await self.url_frontier.queue.put((url.depth, url.normalized_url))
            logger.debug(f"Added URL to queue: {url.normalized_url}")

    def update_depth(self, depth: int) -> None:
        self._current_depth = depth

    def finished(self):
        is_max_depth_reached = self._current_depth >= self._max_depth
        is_queue_empty = self.url_frontier.queue.empty()
        return is_max_depth_reached and is_queue_empty

    def queue_task_done(self) -> None:
        self.url_frontier.queue.task_done()

    async def completing_in_progress_crawling(self) -> None:
        await self.url_frontier.queue.join()