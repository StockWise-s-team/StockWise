from app.stream_a.transformers.base_transformer import BaseTransformer
from typing import Any

class PriceTransformer(BaseTransformer):
    def transform(self, raw_data: Any) -> Any:
        return raw_data
