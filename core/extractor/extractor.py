import logging
from dataclasses import dataclass
from typing import Optional, Any

from core.extractor.content_parser.content_parser import ContentParser

logger = logging.getLogger(__name__)

@dataclass
class Extractor:
    parser: ContentParser

    def extract(self, content: Any) -> Optional[Any]:
        return self.parser.parse(content)
