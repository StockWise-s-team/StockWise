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

SITEMAP_URL = "https://vietstock.vn/sitemap.xml"
TIMEOUT_SECONDS = 15
REQUEST_DELAY_SECONDS = 1.0
MAX_ARTICLES = 50

RELATIVE_TIME_RE = re.compile(
    r"(\d+)\s*(giờ|phút|ngày|tuần|tháng)\s*(trước)?"
)

NOW_VN = datetime.now(timezone.utc)


def _parse_relative_date(text: str) -> datetime | None:
    m = RELATIVE_TIME_RE.search(text)
    if not m:
        return None
    value = int(m.group(1))
    unit = m.group(2)
    if unit == "phút":
        return NOW_VN - timedelta(minutes=value)
    if unit == "giờ":
        return NOW_VN - timedelta(hours=value)
    if unit == "ngày":
        return NOW_VN - timedelta(days=value)
    if unit == "tuần":
        return NOW_VN - timedelta(weeks=value)
    if unit == "tháng":
        return NOW_VN - timedelta(days=value * 30)
    return None


class VietstockCrawler(BaseCrawler):
    def __init__(self, max_articles: int = MAX_ARTICLES):
        self.max_articles = max_articles

    @property
    def source_name(self) -> str:
        return "vietstock"

    async def crawl(self) -> list[dict[str, Any]]:
        try:
            urls = await self._fetch_article_urls()
        except Exception as exc:
            logger.warning("[VietstockCrawler] Failed to fetch sitemap: %s", exc)
            return []

        results: list[dict[str, Any]] = []
        seen_urls: set[str] = set()

        for url in urls:
            if url in seen_urls or len(results) >= self.max_articles:
                continue
            seen_urls.add(url)

            try:
                article = await self._fetch_article(url)
                if article:
                    results.append(article)
                await asyncio.sleep(REQUEST_DELAY_SECONDS)
            except Exception as exc:
                logger.warning(
                    "[VietstockCrawler] Skipping article %s: %s", url, exc
                )
                continue

        return results

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, asyncio.TimeoutError)),
    )
    async def _fetch_article_urls(self) -> list[str]:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/xml, text/xml, */*",
        }
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, headers=headers) as client:
            response = await client.get(SITEMAP_URL)
            response.raise_for_status()
            return self._parse_sitemap(response.text)

    @staticmethod
    def _parse_sitemap(xml_text: str) -> list[str]:
        urls: list[str] = []
        try:
            root = ET.fromstring(xml_text.encode("utf-8"))
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            for loc in root.findall("sm:url/sm:loc", ns):
                if loc.text:
                    urls.append(loc.text.strip())
        except ET.ParseError:
            pass
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
            soup.select_one("h1.title-detail")
            or soup.select_one("h1[itemprop='headline']")
            or soup.select_one("h1")
        )
        title = title_el.get_text(strip=True) if title_el else ""

        content_el = (
            soup.select_one(".detail-content")
            or soup.select_one("#content-detail")
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
            or soup.select_one("[itemprop='description']")
        )
        excerpt = excerpt_el.get_text(strip=True) if excerpt_el else ""

        time_el = (
            soup.select_one(".date-time")
            or soup.select_one("time")
            or soup.select_one("meta[property='article:published_time']")
        )
        published_at = None
        if time_el:
            if time_el.name == "meta":
                published_at = time_el.get("content", "")
            else:
                time_text = time_el.get_text(strip=True)
                parsed = _parse_relative_date(time_text)
                published_at = parsed.isoformat() if parsed else time_text

        symbol_tags: list[str] = []
        for tag in soup.select(".tag-list a, .tags a, .tag a"):
            tag_text = tag.get_text(strip=True).upper()
            if re.fullmatch(r"[A-Z]{3,4}", tag_text):
                symbol_tags.append(tag_text)
        symbol_tags = list(dict.fromkeys(symbol_tags))

        if not title or not content:
            return None

        return {
            "title": title,
            "content": content,
            "excerpt": excerpt,
            "url": url,
            "published_at": published_at,
            "symbols": symbol_tags,
            "source_name": "vietstock",
        }
