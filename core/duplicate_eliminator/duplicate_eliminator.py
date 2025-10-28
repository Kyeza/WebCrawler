from dataclasses import dataclass, field
from typing import List

import fakeredis

from core.scheduler.models.url import Url
from core.utils import normalize_url, calculate_text_checksum


@dataclass
class DuplicateEliminator:
    redis: fakeredis.FakeStrictRedis
    _redis_url_set_key: str = field(default="crawler:visited_urls", init=False)
    _redis_content_set_key: str = field(default="crawler:seen_content", init=False)

    def _is_duplicate(self, checksum: str, key: str) -> bool:
        is_duplicate =  bool(self.redis.sismember(key, checksum))
        if not is_duplicate:
            self.redis.sadd(key, checksum)

        return is_duplicate

    def is_duplicate_url(self, normalized_url) -> bool:
        url_checksum = calculate_text_checksum(normalized_url)
        return self._is_duplicate(url_checksum, self._redis_url_set_key)

    def is_duplicate_content(self, content: str) -> bool:
        content_checksum = calculate_text_checksum(content)
        return self._is_duplicate(content_checksum, self._redis_content_set_key)

    def filter_extracted_urls(self, extracted_urls: List[str], parent_url_id: int, depth: int)  -> List[Url]:
        filtered_urls: List[Url] = []
        for url in extracted_urls:
            normalized_url = normalize_url(url)
            if normalized_url is None:
                continue
            if self.is_duplicate_url(normalized_url):
                continue

            filtered_urls.append(Url(url=url, normalized_url=normalized_url, parent_url_id=parent_url_id, depth=depth))

        return filtered_urls