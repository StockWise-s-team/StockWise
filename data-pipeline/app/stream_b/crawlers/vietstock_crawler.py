from app.stream_b.crawlers.base_crawler import BaseCrawler
from typing import Any, List

class VietstockCrawler(BaseCrawler):
    @property
    def source_name(self) -> str:
        return "vietstock"

    async def crawl(self) -> List[Any]:
        return []
