import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Generator

from core.datastore.schemas import create_tables
from core.scheduler.models.url import Url


@dataclass
class Database:
    path: Path

    def __post_init__(self):
        self.path.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(create_tables())

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.path.as_posix())
        try:
            yield conn
        finally:
            conn.commit()
            conn.close()

    def insert_url(self, url: Url) -> None:
        pass
