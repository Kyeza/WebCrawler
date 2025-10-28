import logging
from typing import Optional

from bs4 import BeautifulSoup

from core.extractor.content_parser.content_parser import ContentParser
from core.extractor.content_parser.parser_result import ParserResult

logger = logging.getLogger(__name__)


class TextualParser(ContentParser):

    @staticmethod
    def parse(html_doc: str) -> Optional[ParserResult]:
        soup = BeautifulSoup(html_doc, 'html.parser')
        hrefs = [link.get("href") for link in soup.find_all('a')]
        return ParserResult(
            title=soup.title.string.rstrip().lower().replace(" ", "_"),
            content=soup.get_text(),
            extracted_urls=hrefs
        )
