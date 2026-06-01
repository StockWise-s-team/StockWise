import asyncio
import sys
sys.path.insert(0, ".")

from app.stream_b.crawlers.vietstock_crawler import VietstockCrawler


async def main():
    crawler = VietstockCrawler(max_articles=10)
    articles = await crawler.crawl(tracked_symbols=["FPT", "VIC"])

    print(f"Total articles: {len(articles)}")
    for a in articles:
        print(f"\n  Title: {a['title'][:80]}")
        print(f"  URL: {a['url']}")
        print(f"  Symbols: {a['symbols']}")
        print(f"  Published: {a['published_at']}")
        print(f"  Content preview: {a['content'][:100]}...")


if __name__ == "__main__":
    asyncio.run(main())
