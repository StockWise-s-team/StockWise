from abc import ABC, abstractmethod
from typing import Any, List, Optional

class BaseCrawler(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str: ...

    @abstractmethod
    async def crawl(self, tracked_symbols: Optional[list[str]] = None) -> List[Any]: ...
