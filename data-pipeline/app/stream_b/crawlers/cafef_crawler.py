import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from app.stream_b.crawlers.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)

API_BASE = "https://apiweb.cafef.vn/api/v1/StockPrice/AnalysisReport/smallsreach"
TIMEOUT_SECONDS = 15
REQUEST_DELAY_SECONDS = 0.5
PAGE_SIZE = 20
MAX_ARTICLES_PER_SYMBOL = 20

HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "vi,en-US;q=0.9,en;q=0.8",
    "Origin": "https://cafef.vn",
    "Referer": "https://cafef.vn/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/147.0.0.0 Safari/537.36"
    ),
}


class CafeFCrawler(BaseCrawler):
    def __init__(self, max_articles: int = MAX_ARTICLES_PER_SYMBOL):
        self.max_articles = max_articles

    @property
    def source_name(self) -> str:
        return "cafef"

    async def crawl(
        self, tracked_symbols: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """
        Crawl Cafef analyst reports using the per-symbol API.
        Returns articles where symbols are extracted from linkStocks field.
        Falls back to sitemap crawl if the API is unavailable.
        """
        if not tracked_symbols:
            logger.warning("[CafeFCrawler] No tracked symbols -- skipping")
            return []

        symbols = [s.upper().strip() for s in tracked_symbols if s.strip()]

        semaphore = asyncio.Semaphore(3)

        async def search_symbol(symbol: str) -> list[dict[str, Any]]:
            async with semaphore:
                await asyncio.sleep(REQUEST_DELAY_SECONDS)
                try:
                    return await self._fetch_symbol_reports(symbol)
                except Exception as exc:
                    logger.warning(
                        "[CafeFCrawler] API failed for %s: %s -- trying sitemap",
                        symbol,
                        exc,
                    )
                    try:
                        return await self._fallback_sitemap(symbol)
                    except Exception as exc2:
                        logger.warning(
                            "[CafeFCrawler] Sitemap fallback also failed for %s: %s",
                            symbol,
                            exc2,
                        )
                        return []

        results_per_symbol = await asyncio.gather(
            *[search_symbol(s) for s in symbols],
            return_exceptions=True,
        )

        all_articles: list[dict[str, Any]] = []
        seen_urls: set[str] = set()
        seen_ids: set[str] = set()

        for result in results_per_symbol:
            if isinstance(result, Exception):
                logger.warning(
                    "[CafeFCrawler] Exception for symbol: %s", result
                )
                continue
            for article in result:
                article_id = article.get("article_id", "")
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
            "[CafeFCrawler] Total unique articles: %d (from %d symbols)",
            len(all_articles),
            len(symbols),
        )
        return all_articles

    async def _fetch_symbol_reports(
        self, symbol: str
    ) -> list[dict[str, Any]]:
        """Fetch analyst reports for a single symbol via the API."""
        articles: list[dict[str, Any]] = []
        page_index = 1

        async with httpx.AsyncClient(
            timeout=TIMEOUT_SECONDS, follow_redirects=True
        ) as client:
            while len(articles) < self.max_articles:
                url = (
                    f"{API_BASE}?symbol={symbol}&resourceCode=0"
                    f"&type=latest&reportType=0&pageIndex={page_index}"
                    f"&pageSize={PAGE_SIZE}"
                )
                resp = await client.get(url, headers=HEADERS)
                resp.raise_for_status()
                result = resp.json()

                items = result.get("value", {}).get("items", [])
                if not items:
                    break

                for item in items:
                    article = self._transform_item(item)
                    if article:
                        articles.append(article)
                        if len(articles) >= self.max_articles:
                            break

                if len(items) < PAGE_SIZE:
                    break
                page_index += 1

        logger.info(
            "[CafeFCrawler] %s: got %d articles (API)", symbol, len(articles)
        )
        return articles

    def _transform_item(self, item: dict[str, Any]) -> dict[str, Any] | None:
        """Transform an API item into a normalized article dict."""
        article_id = item.get("id") or ""
        link_stocks = item.get("linkStocks") or {}
        symbols = list(link_stocks.keys())

        if not symbols:
            logger.debug(
                "[CafeFCrawler] Skipping item with no linkStocks: %s",
                item.get("title", "")[:60],
            )
            return None

        title = (item.get("title") or "").strip()
        if not title:
            return None

        detail_link = item.get("linkDetail") or ""
        base_url = "https://cafef.vn"
        url = f"{base_url}{detail_link}" if detail_link.startswith("/") else detail_link

        body = item.get("body") or ""
        content = body.replace("\n", " ").strip()

        date_str = item.get("dateDeploy") or ""
        published_at = date_str

        resource_name = item.get("resourceName") or ""
        report_type = item.get("reportType") or ""

        return {
            "article_id": article_id,
            "title": title,
            "content": content,
            "excerpt": content[:300] if content else "",
            "url": url,
            "published_at": published_at,
            "symbols": symbols,
            "source_name": "cafef",
            "_meta": {
                "report_type": report_type,
                "analyst_company": resource_name,
                "is_hot": item.get("isHot"),
                "source_id": item.get("sourceID"),
            },
        }

    async def _fallback_sitemap(self, symbol: str) -> list[dict[str, Any]]:
        """
        Fallback: crawl the sitemap and re-tag with the searched symbol.
        Only used when the API is unavailable.
        """
        from app.stream_b.crawlers.cafef_crawler_sitemap import (
            CafeFSitemapCrawler,
        )

        sitemap_crawler = CafeFSitemapCrawler(max_articles=self.max_articles)
        articles = await sitemap_crawler.crawl(tracked_symbols=[symbol])
        for article in articles:
            article["symbols"] = [symbol]
        return articles
