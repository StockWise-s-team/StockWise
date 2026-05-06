from app.stream_b.crawlers.base_crawler import BaseCrawler
from typing import Any, List

class CafeFCrawler(BaseCrawler):
    @property
    def source_name(self) -> str:
        return "cafef"

    async def crawl(self) -> List[Any]:
        return []
