from abc import ABC, abstractmethod
from typing import Any, List

class BaseCrawler(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str: ...

    @abstractmethod
    async def crawl(self) -> List[Any]: ...
