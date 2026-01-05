from abc import abstractmethod, ABC
from typing import Optional

from webcrawler_arnoldkyeza.core.extractor.content_parser.parser_result import ParserResult


class AbstractContentParser(ABC):

    @abstractmethod
    def parse(self, *args, **kwargs) -> Optional[ParserResult]:
        pass


class ContentParser(AbstractContentParser):

    def parse(self, *args, **kwargs) -> Optional[ParserResult]:
        pass