from dataclasses import dataclass
from typing import Any

from webcrawler_arnoldkyeza.core.html_fetcher.protocol_handlers.protocol_handler import ProtocolHandler


@dataclass
class HTMLFetcher:
    handler: ProtocolHandler

    async def fetch(self, data: Any) -> Any:
        return await self.handler.get_content(data)
