from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any


class AbstractProtocolHandler(ABC):

    @abstractmethod
    async def get_content(self, *args, **kwargs) -> Optional[Any]:
        pass


@dataclass
class ProtocolHandler(AbstractProtocolHandler):

    async def get_content(self, *args, **kwargs) -> Optional[Any]:
        pass
