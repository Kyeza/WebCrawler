import datetime
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Generator, Optional

from webcrawler_arnoldkyeza.core.datastore.schemas import create_tables
from webcrawler_arnoldkyeza.core.enums.url_status_type import UrlStatusType
from webcrawler_arnoldkyeza.core.scheduler.models.url import Url


@dataclass
class DatabaseManager:
    path: Path

    def __post_init__(self):
        try:
            self.path.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            pass

        with self._connect() as conn:
            conn.executescript(create_tables())

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(
            self.path.as_posix(),
        )
        conn.row_factory = self.dict_factory
        try:
            yield conn
        finally:
            conn.commit()
            conn.close()

    def insert_url(self, url: Url) -> None:
        """
        Insert a new URL row. If the URL (by normalized URL checksum/unique constraint) already exists,
        ignore the insertion.
        """
        last_crawled_at = getattr(url, "last_crawled_at", None)
        last_crawled_at_str = last_crawled_at.isoformat() if isinstance(last_crawled_at, datetime.datetime) else None
        status_obj = getattr(url, "status", UrlStatusType.PENDING)
        status_str = status_obj.value if isinstance(status_obj, UrlStatusType) else str(status_obj)
        parent_url_id = getattr(url, "parent_url_id", None)
        error_message = getattr(url, "error_message", None)

        insertion_query = """
                INSERT OR IGNORE INTO urls (url, normalized_url, priority, update_frequency, last_crawled_at,
                                            status, parent_url_id,
                                            error_message, depth)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

        with self._connect() as conn:
            conn.execute(
                insertion_query,
                (
                    url.url,
                    url.normalized_url,
                    url.priority,
                    url.update_frequency,
                    last_crawled_at_str,
                    status_str,
                    parent_url_id,
                    error_message,
                    url.depth,
                ),
            )

    def get_pending_urls(self, limit: int) -> list[Url]:
        results: list[Url] = []
        fetch_pending_query = """
                SELECT url_id,
                       url,
                       normalized_url,
                       priority,
                       update_frequency,
                       last_crawled_at,
                       status,
                       parent_url_id,
                       error_message,
                       depth,
                       created_at
                FROM urls
                WHERE status = ?
                ORDER BY priority, created_at
                LIMIT ?
                """

        with self._connect() as conn:
            cur = conn.execute(fetch_pending_query, (UrlStatusType.PENDING.value, limit))
            rows = cur.fetchall()

            for row in rows:
                results.append(
                    Url(**row)
                )

        return results

    def get_url(self, normalized_url: str) -> Optional[Url]:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT * FROM urls WHERE normalized_url = ? LIMIT 1",
                (normalized_url,),
            )
            row = cur.fetchone()
            if row is None:
                return None

            return Url(**row)

    def url_exists(self, url: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT 1 FROM urls WHERE normalized_url = ? LIMIT 1",
                (url,),
            )
            return cur.fetchone() is not None

    def update_url_status(self, normalized_url: str, status: UrlStatusType):
        with self._connect() as conn:
            conn.execute(
                "UPDATE urls SET status = ? WHERE normalized_url = ?",
                (status.value, normalized_url),
            )

    def mark_url_as_crawled(self, normalized_url, last_crawled_at: datetime.datetime):
        with self._connect() as conn:
            conn.execute(
                "UPDATE urls SET last_crawled_at = ?, status = ? WHERE normalized_url = ?",
                (last_crawled_at.isoformat(), UrlStatusType.COMPLETED.value, normalized_url),
            )

    @staticmethod
    def dict_factory(cursor, row):
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

    def update_url_on_failed(self, normalized_url: str, error_message: str):
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE urls
                SET status = ?, error_message = ?
                WHERE normalized_url = ?
                """,
                (UrlStatusType.FAILED.value, error_message, normalized_url),
            )

