import hashlib
from dataclasses import dataclass, field

import fakeredis


@dataclass
class DuplicateEliminator:
    redis: fakeredis.FakeStrictRedis
    _redis_set_key: str = field(default="crawler:visited_urls", init=False)

    def is_duplicate_url(self, normalized_url) -> bool:
        url_checksum = self.calculate_checksum(normalized_url)
        is_duplicate = bool(self.redis.sismember(self._redis_set_key, url_checksum))
        if not is_duplicate:
            self.redis.sadd(self._redis_set_key, url_checksum)
            return True
        return False

    def is_duplicate_content(self, content) -> bool:
        pass

    @staticmethod
    def calculate_checksum(url) -> str:
        sha256_hash = hashlib.sha256()
        sha256_hash.update(url.encode('utf-8'))
        return sha256_hash.hexdigest()