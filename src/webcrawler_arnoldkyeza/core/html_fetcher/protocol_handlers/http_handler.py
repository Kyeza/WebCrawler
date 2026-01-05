import asyncio
import logging
from dataclasses import dataclass
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse

import requests

from webcrawler_arnoldkyeza.core.html_fetcher.protocol_handlers.protocol_handler import ProtocolHandler
from webcrawler_arnoldkyeza.core.html_fetcher.protocol_handlers.errors import UnsupportedContentTypeError

logger = logging.getLogger(__name__)


@dataclass
class HTTPProtocolHandler(ProtocolHandler):

    async def get_content(self, url) -> Optional[str]:
        schema = urlparse(url).scheme
        if not schema in ["http", "https"]:
            return None

        try:
            return await asyncio.to_thread(self._fetch_content, url)
        except HTTPError as e:
            raise ValueError(f"Error fetching content from {url}: {e}")
        except URLError as e:
            raise ValueError(f"Network error while fetching content from {url}: {e}")
        except Exception as e:
            raise e

    @staticmethod
    def _fetch_content(url) -> str:
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()  # Raise error for bad status codes
            content_type = response.headers.get('Content-Type', '')

            if 'text/html' not in content_type:
                raise UnsupportedContentTypeError(content_type)

            logger.debug(f"Fetched content from {url}")

            return response.text  # For textual content like HTML
        except requests.RequestException as e:
            raise ValueError(f"Error fetching content from {url}: {e}")


