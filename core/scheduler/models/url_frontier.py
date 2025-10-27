import asyncio
from dataclasses import dataclass
from typing import Tuple


@dataclass
class UrlFrontier:
    queue: asyncio.PriorityQueue[Tuple[int, str]] = asyncio.PriorityQueue(maxsize=1000)