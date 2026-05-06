from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        ...
