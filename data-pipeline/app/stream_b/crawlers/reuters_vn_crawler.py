from app.stream_b.crawlers.base_crawler import BaseCrawler
from typing import Any, List

class ReutersVNCrawler(BaseCrawler):
    @property
    def source_name(self) -> str:
        return "reuters_vn"

    async def crawl(self) -> List[Any]:
        return []
