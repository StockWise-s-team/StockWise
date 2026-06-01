import asyncio
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app.stream_b.crawlers.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)

SEARCH_API = "https://dc.vietstock.vn/api/Search/SearchArticleNewAsync"
TIMEOUT_SECONDS = 15
MAX_ARTICLES_PER_SYMBOL = 20
PAGE_SIZE = 20
REQUEST_DELAY_SECONDS = 0.5

HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "vi,en-US;q=0.9,en;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://vietstock.vn",
    "Referer": "https://vietstock.vn/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def _is_real_stock_article(item: dict, symbol: str) -> bool:
    """Keep articles that are real news (not SYSTEM exchange announcements)."""
    author = (item.get("By") or "").strip()
    word_count = item.get("WordCount") or 0
    title = (item.get("Title") or "").lower()
    source = (item.get("Source") or "").strip()

    # Reject SYSTEM-generated exchange announcements
    if author == "SYSTEM" or not author:
        return False

    # Reject warrant/certificate listings (chứng quyền)
    title_lower = title.lower()
    if "chứng quyền" in title_lower or "quyết định" in title_lower and "niêm yết" in title_lower:
        return False

    # Reject articles with no real content
    if word_count < 50:
        return False

    return True


class VietstockCrawler(BaseCrawler):
    def __init__(self, max_articles: int = MAX_ARTICLES_PER_SYMBOL):
        self.max_articles = max_articles

    @property
    def source_name(self) -> str:
        return "vietstock"

    async def crawl(
        self, tracked_symbols: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """
        Crawl Vietstock news using the per-symbol search API.
        For each symbol, fetches up to max_articles real news articles
        (excluding SYSTEM exchange announcements and warrant listings).
        Falls back to sitemap crawl if API fails.
        """
        if not tracked_symbols:
            logger.warning("[VietstockCrawler] No tracked symbols — skipping")
            return []

        symbols = [s.upper().strip() for s in tracked_symbols if s.strip()]

        # Run all symbol searches concurrently with rate limiting
        semaphore = asyncio.Semaphore(3)

        async def search_symbol(symbol: str) -> list[dict[str, Any]]:
            async with semaphore:
                await asyncio.sleep(REQUEST_DELAY_SECONDS)
                try:
                    return await self._search_symbol(symbol)
                except Exception as exc:
                    logger.warning("[VietstockCrawler] API failed for %s: %s — trying sitemap", symbol, exc)
                    try:
                        return await self._fallback_sitemap(symbol)
                    except Exception as exc2:
                        logger.warning("[VietstockCrawler] Sitemap fallback also failed for %s: %s", symbol, exc2)
                        return []

        results_per_symbol = await asyncio.gather(
            *[search_symbol(s) for s in symbols], return_exceptions=True
        )

        # Flatten results
        all_articles: list[dict[str, Any]] = []
        seen_urls: set[str] = set()
        seen_ids: set[int] = set()

        for result in results_per_symbol:
            if isinstance(result, Exception):
                logger.warning("[VietstockCrawler] Exception for symbol: %s", result)
                continue
            for article in result:
                article_id = article.get("article_id")
                url = article.get("url", "")
                if article_id and article_id in seen_ids:
                    continue
                if url and url in seen_urls:
                    continue
                if article_id:
                    seen_ids.add(article_id)
                if url:
                    seen_urls.add(url)
                all_articles.append(article)

        logger.info(
            "[VietstockCrawler] Total unique articles: %d (from %d symbols)",
            len(all_articles), len(symbols)
        )
        return all_articles

    async def _search_symbol(self, symbol: str) -> list[dict[str, Any]]:
        """Fetch articles for a single symbol via the search API."""
        articles: list[dict[str, Any]] = []

        # Fetch up to max_articles (1 page = 20, which equals our limit)
        params, body = self._make_payload(symbol, page=1)
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, follow_redirects=True) as client:
            resp = await client.post(SEARCH_API, params=params, content=body, headers=HEADERS)
            resp.raise_for_status()
            result = resp.json()

        total = result.get("totalCount", 0)
        data = result.get("data", [])

        if total == 0:
            logger.info("[VietstockCrawler] No results for symbol %s", symbol)
            return []

        logger.info(
            "[VietstockCrawler] Symbol %s: total=%d, fetching up to %d",
            symbol, total, self.max_articles
        )

        # Filter and transform
        for item in data:
            if not _is_real_stock_article(item, symbol):
                continue

            title = (item.get("Title") or "").strip()
            url = f"https://vietstock.vn{item.get('URL', '')}"
            content = self._extract_content(item)
            publish_time = item.get("PublishTime", "") or ""

            articles.append({
                "title": title,
                "content": content,
                "excerpt": (item.get("Head") or "").strip(),
                "url": url,
                "published_at": publish_time,
                "symbols": [symbol],
                "source_name": "vietstock",
            })

            if len(articles) >= self.max_articles:
                break

        logger.info("[VietstockCrawler] %s: got %d real articles", symbol, len(articles))
        return articles

    @staticmethod
    def _make_payload(symbol: str, page: int) -> tuple[dict, str]:
        skip = (page - 1) * PAGE_SIZE
        params = {
            "keySearch": symbol,
            "currentPage": page,
            "pageSize": PAGE_SIZE,
            "skip": skip,
            "filterTime": "all",
        }
        body = (
            f"keySearch={symbol}&currentPage={page}"
            f"&pageSize={PAGE_SIZE}&skip={skip}&filterTime=all"
        )
        return params, body

    @staticmethod
    def _extract_content(item: dict) -> str:
        """Extract readable content from the API item, fall back to Head if no full content."""
        content = item.get("Content") or ""
        if content:
            # Clean HTML from content
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, "lxml")
            for tag in soup.find_all(["script", "style", "table"]):
                tag.decompose()
            return soup.get_text(separator=" ", strip=True)
        # Fallback: use Head (summary) if no full content
        return (item.get("Head") or "").strip()

    async def _fallback_sitemap(self, symbol: str) -> list[dict[str, Any]]:
        """
        Fallback: use sitemap crawl (original approach).
        Only used when the search API is unavailable.
        """
        from app.stream_b.crawlers.vietstock_sitemap_crawler import VietstockSitemapCrawler

        sitemap_crawler = VietstockSitemapCrawler(max_articles=self.max_articles)
        articles = await sitemap_crawler.crawl(tracked_symbols=[symbol])
        # Re-tag with the searched symbol
        for article in articles:
            article["symbols"] = [symbol]
        return articles
