from app.stream_a.fetchers.base_fetcher import BaseFetcher
from typing import Any, List

class VnStockFetcher(BaseFetcher):
    @property
    def source_name(self) -> str:
        return "vnstock"

    async def fetch(self, symbols: List[str]) -> Any:
        return [{"symbol": s, "prices": []} for s in symbols]
