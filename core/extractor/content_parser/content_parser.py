from abc import abstractmethod, ABC
from typing import Optional, Any
from urllib.parse import ParseResult


class AbstractContentParser(ABC):

    @abstractmethod
    def parse(self, *args, **kwargs) -> Optional[ParseResult]:
        pass


class ContentParser(AbstractContentParser):

    def parse(self, *args, **kwargs) -> Optional[ParseResult]:
        pass