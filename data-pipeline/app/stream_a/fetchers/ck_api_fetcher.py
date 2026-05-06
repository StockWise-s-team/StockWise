from app.stream_a.fetchers.base_fetcher import BaseFetcher
from typing import Any, List

class CkApiFetcher(BaseFetcher):
    @property
    def source_name(self) -> str:
        return "ck_api"

    async def fetch(self, symbols: List[str]) -> Any:
        return [{"symbol": s, "ratios": {}} for s in symbols]
