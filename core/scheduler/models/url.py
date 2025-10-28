import datetime
import sqlite3
from dataclasses import dataclass, field
from typing import Optional

from core.enums.url_status_type import UrlStatusType


@dataclass(order=True)
class Url:
    url: str
    normalized_url: str
    priority: int = field(default=1)  # ideally, this should be based on the importance of the website
    update_frequency: int = field(
        default=1)  # ideally, this should be based on how often the content on the URL is expected to change
    last_crawled_at: Optional[datetime.datetime] = field(default=None)
    status: UrlStatusType = field(default=UrlStatusType.PENDING)
    parent_url_id: Optional[int] = field(default=None)
    error_message: Optional[str] = field(default=None)
    depth: Optional[int] = field(default=0)
    created_at: Optional[datetime.datetime] = field(default=None)
    url_id: Optional[int] = field(default=None)

