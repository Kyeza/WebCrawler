import datetime
from dataclasses import dataclass, field
from typing import Optional

from core.enums.url_status_type import UrlStatusType


@dataclass
class Url:
    url: str
    normalized_url: str
    checksum: str
    priority: int
    update_frequency: int # number of seconds to next crawl
    last_crawled_at: Optional[datetime.datetime] = field(default=None)
    status: UrlStatusType = field(default=UrlStatusType.PENDING)
    parent_url_id: Optional[int] = field(default=None)
    children_url_ids: Optional[list[int]] = field(default_factory=list)
    error_message: Optional[str] = field(default=None)
    depth: Optional[int] = field(default=0)
    created_at: Optional[datetime.datetime] = field(default=None)
    url_id: Optional[int] = field(default=None)

