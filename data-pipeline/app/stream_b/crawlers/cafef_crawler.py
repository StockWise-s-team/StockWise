import asyncio
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Any
from xml.etree import ElementTree as ET

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings
from app.stream_b.crawlers.base_crawler import BaseCrawler
from app.stream_b.exceptions import CrawlError

logger = logging.getLogger(__name__)

SITEMAP_URL = "https://cafef.vn/latest-news-sitemap.xml"
TIMEOUT_SECONDS = 15
REQUEST_DELAY_SECONDS = 1.0
MAX_ARTICLES = 20
CUTOFF_DAYS = 30

NOW_VN = datetime.now(timezone.utc)
CUTOFF_DATE = NOW_VN - timedelta(days=CUTOFF_DAYS)


class CafeFCrawler(BaseCrawler):
    def __init__(self, max_articles: int = MAX_ARTICLES):
        self.max_articles = max_articles

    @property
    def source_name(self) -> str:
        return "cafef"

    async def crawl(
        self, tracked_symbols: list[str] | None = None
    ) -> list[dict[str, Any]]:
        try:
            urls_with_dates = await self._fetch_article_urls()
        except Exception as exc:
            logger.warning("[CafeFCrawler] Failed to fetch sitemap: %s", exc)
            return []

        urls_with_dates.sort(key=lambda x: x[1] or datetime.min, reverse=True)

        results: list[dict[str, Any]] = []
        seen_urls: set[str] = set()

        for url, lastmod in urls_with_dates:
            if url in seen_urls or len(results) >= self.max_articles:
                continue
            seen_urls.add(url)

            if lastmod and lastmod < CUTOFF_DATE:
                continue

            try:
                article = await self._fetch_article(url)
                if article:
                    results.append(article)
                await asyncio.sleep(REQUEST_DELAY_SECONDS)
            except Exception as exc:
                logger.warning(
                    "[CafeFCrawler] Skipping article %s: %s", url, exc
                )
                continue

        if tracked_symbols:
            tracked_set = {s.upper() for s in tracked_symbols}
            results.sort(
                key=lambda a: not bool(
                    tracked_set & {s.upper() for s in a.get("symbols", [])}
                )
            )

        return results

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, asyncio.TimeoutError)),
    )
    async def _fetch_article_urls(self) -> list[tuple[str, datetime | None]]:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/xml, text/xml, application/xhtml+xml, */*",
        }
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, headers=headers) as client:
            response = await client.get(SITEMAP_URL)
            response.raise_for_status()
            urls = self._parse_sitemap(response.text)
            logger.info("[CafeFCrawler] Sitemap parsed %d URLs", len(urls))
            return urls

    @staticmethod
    def _parse_sitemap(xml_text: str) -> list[tuple[str, datetime | None]]:
        urls: list[tuple[str, datetime | None]] = []
        try:
            root = ET.fromstring(xml_text.encode("utf-8"))
        except ET.ParseError as e:
            logger.warning("[CafeFCrawler] Sitemap XML parse error: %s", e)
            return []
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        for url_el in root.findall("sm:url", ns):
            loc = url_el.find("sm:loc", ns)
            # Use itertext() — handles CDATA and mixed content
            loc_text = "".join(loc.itertext()).strip() if loc is not None else ""
            if not loc_text:
                continue
            lastmod_str = url_el.find("sm:lastmod", ns)
            lastmod: datetime | None = None
            if lastmod_str is not None:
                lastmod_text = "".join(lastmod_str.itertext()).strip()
                if lastmod_text:
                    try:
                        lastmod = datetime.fromisoformat(lastmod_text.replace("+07:00", "+07:00").rstrip("Z"))
                        if lastmod.tzinfo is None:
                            lastmod = lastmod.replace(tzinfo=timezone.utc)
                    except ValueError:
                        lastmod = None
            urls.append((loc_text, lastmod))
        return urls

    async def _fetch_article(self, url: str) -> dict[str, Any] | None:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,*/*",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
        }
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, headers=headers) as client:
            response = await client.get(url)
            if response.status_code == 403:
                return None
            response.raise_for_status()
            return self._parse_article(response.text, url)

    def _parse_article(
        self, html: str, url: str
    ) -> dict[str, Any] | None:
        soup = BeautifulSoup(html, "lxml")

        title_el = (
            soup.select_one("h1.title[data-role='title']")
            or soup.select_one("h1.title_news_detail")
            or soup.select_one("h1.detail-title")
            or soup.select_one("h1[itemprop='headline']")
            or soup.select_one("h1")
        )
        title = title_el.get_text(strip=True) if title_el else ""

        content_el = (
            soup.select_one(".detail-content")
            or soup.select_one("#content_detail")
            or soup.select_one(".content_detail")
            or soup.select_one("article")
        )
        if content_el:
            for tag in content_el.find_all(["script", "style", "iframe", "noscript"]):
                tag.decompose()
            content = content_el.decode_contents()
        else:
            content = ""

        excerpt_el = (
            soup.select_one(".sapo")
            or soup.select_one(".sapo_detail")
            or soup.select_one("[itemprop='description']")
        )
        excerpt = excerpt_el.get_text(strip=True) if excerpt_el else ""

        date_el = (
            soup.select_one("span.time")
            or soup.select_one("time[itemprop='datePublished']")
            or soup.select_one("meta[property='article:published_time']")
            or soup.select_one("meta[name='publishdate']")
        )
        published_at = None
        if date_el:
            if date_el.name == "meta":
                published_at = date_el.get("content", "")
            else:
                published_at = date_el.get_text(strip=True)

        symbol_tags: list[str] = []
        tag_section = soup.select(".tag_cryptocurrency a, .tag_stock a, .tag a")
        for tag in tag_section:
            tag_text = tag.get_text(strip=True).upper()
            if re.fullmatch(r"[A-Z]{3,4}", tag_text):
                symbol_tags.append(tag_text)
        symbol_tags = list(dict.fromkeys(symbol_tags))

        if not title or not content:
            logger.debug("[CafeFCrawler] Skipping article (no title or content): %s", url)
            return None

        return {
            "title": title,
            "content": content,
            "excerpt": excerpt,
            "url": url,
            "published_at": published_at,
            "symbols": symbol_tags,
            "source_name": "cafef",
        }
