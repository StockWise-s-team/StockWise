from abc import ABC, abstractmethod
from typing import Any

class BaseTransformer(ABC):
    @abstractmethod
    def transform(self, raw_data: Any) -> Any: ...
