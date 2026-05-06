from abc import ABC, abstractmethod
from typing import Any, List

class BaseFetcher(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str: ...

    @abstractmethod
    async def fetch(self, symbols: List[str]) -> Any: ...
