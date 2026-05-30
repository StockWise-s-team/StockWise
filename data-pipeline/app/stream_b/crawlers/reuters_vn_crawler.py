import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import Any

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.stream_b.crawlers.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)

LISTING_URL = "https://www.reuters.com/world/asia-pacific"
TIMEOUT_SECONDS = 20
REQUEST_DELAY_SECONDS = 1.5
MAX_ARTICLES = 30

VN_INDICATORS = {
    "vietnam", "viet nam", "vietnamese",
    "hanoi", "ho chi minh city", "saigon",
    "vn-index", "vnindex",
}

STOCK_TICKER_RE = re.compile(
    r"\b([A-Z]{2,4})(?:(?:\.|:)[A-Z]{2})?\b"
)


class ReutersVNCrawler(BaseCrawler):
    @property
    def source_name(self) -> str:
        return "reuters_vn"

    async def crawl(self) -> list[dict[str, Any]]:
        try:
            page_data = await self._fetch_listing()
        except Exception as exc:
            logger.warning("[ReutersVNCrawler] Failed to fetch listing: %s", exc)
            return []
        return page_data

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, asyncio.TimeoutError)),
    )
    async def _fetch_listing(self) -> list[dict[str, Any]]:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,*/*",
            "Accept-Language": "en-US,en;q=0.9",
        }
        async with httpx.AsyncClient(
            timeout=TIMEOUT_SECONDS, headers=headers,
            follow_redirects=True,
        ) as client:
            response = await client.get(LISTING_URL)
            response.raise_for_status()
            return self._parse_listing(response.text)

    def _parse_listing(self, html: str) -> list[dict[str, Any]]:
        soup = BeautifulSoup(html, "lxml")
        results: list[dict[str, Any]] = []
        seen_urls: set[str] = set()

        for article in soup.select("article"):
            link_el = (
                article.select_one("a[data-testid='Link']")
                or article.select_one("a.story-link")
                or article.select_one("a")
            )
            if not link_el or not link_el.get("href"):
                continue

            href = link_el["href"]
            if href.startswith("/"):
                url = f"https://www.reuters.com{href}"
            else:
                url = href

            title_el = (
                article.select_one("h2, h3")
                or article.select_one("[data-testid='Heading']")
            )
            title = title_el.get_text(strip=True) if title_el else ""

            excerpt_el = (
                article.select_one("p")
                or article.select_one("[data-testid='Summary']")
            )
            excerpt = excerpt_el.get_text(strip=True) if excerpt_el else ""

            time_el = article.select_one("time")
            published_at = None
            if time_el:
                published_at = time_el.get("datetime") or time_el.get_text(strip=True)

            if not title or not url or url in seen_urls:
                continue
            seen_urls.add(url)

            if not self._is_vn_related(title, excerpt):
                continue

            results.append({
                "title": title,
                "content": "",
                "excerpt": excerpt,
                "url": url,
                "published_at": published_at,
                "symbols": [],
                "source_name": "reuters_vn",
            })

        return results

    @staticmethod
    def _is_vn_related(title: str, excerpt: str) -> bool:
        combined = f"{title} {excerpt}".lower()
        return any(kw in combined for kw in VN_INDICATORS)

    async def fetch_full_content(self, url: str) -> dict[str, Any] | None:
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,*/*",
            }
            async with httpx.AsyncClient(
                timeout=TIMEOUT_SECONDS, headers=headers, follow_redirects=True
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                return self._parse_article(response.text, url)
        except Exception as exc:
            logger.warning(
                "[ReutersVNCrawler] Failed to fetch article %s: %s", url, exc
            )
            return None

    def _parse_article(
        self, html: str, url: str
    ) -> dict[str, Any] | None:
        soup = BeautifulSoup(html, "lxml")

        title_el = (
            soup.select_one("h1")
            or soup.select_one("[data-testid='Heading']")
        )
        title = title_el.get_text(strip=True) if title_el else ""

        body_el = (
            soup.select_one("[data-testid='Body']")
            or soup.select_one(".article-body")
            or soup.select_one("article")
        )
        content = body_el.decode_contents() if body_el else ""

        date_el = soup.select_one("time")
        published_at = None
        if date_el:
            published_at = date_el.get("datetime") or date_el.get_text(strip=True)

        text_for_symbols = f"{title} {content}"
        symbols = self._extract_symbols(text_for_symbols)

        if not title:
            return None

        return {
            "title": title,
            "content": content,
            "excerpt": "",
            "url": url,
            "published_at": published_at,
            "symbols": symbols,
            "source_name": "reuters_vn",
        }

    @staticmethod
    def _extract_symbols(text: str) -> list[str]:
        candidates = STOCK_TICKER_RE.findall(text)
        seen: set[str] = set()
        symbols: list[str] = []
        for sym in candidates:
            sym = sym.strip(":.").upper()
            if len(sym) < 2 or sym in seen:
                continue
            if any(
                kw in sym for kw in ("THE", "AND", "FOR", "WITH", "NEWS",
                                     "REUTERS", "WORLD", "ASIA", "HTTP",
                                     "THIS", "THAT", "HAVE", "FROM")
            ):
                continue
            seen.add(sym)
            symbols.append(sym)
        return symbols
