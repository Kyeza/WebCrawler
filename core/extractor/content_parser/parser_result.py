from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class ParserResult:
    title: str
    content: str
    extracted_urls: List[str] = field(default_factory=list)