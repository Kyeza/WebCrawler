import asyncio
from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class UrlFrontier:
    queue: asyncio.PriorityQueue[Tuple[int, str]] = field(
        default_factory=lambda: asyncio.PriorityQueue(maxsize=1000)
    )