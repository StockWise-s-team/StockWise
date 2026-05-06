from app.stream_b.transformers.base_transformer import BaseTransformer
from typing import Any

class NewsTransformer(BaseTransformer):
    def transform(self, raw_data: Any) -> Any:
        return raw_data
