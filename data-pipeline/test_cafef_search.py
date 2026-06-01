import asyncio
import httpx
from bs4 import BeautifulSoup

# Get fresh cookies by first visiting the main page
async def get_cafef_cookies():
    """Visit main page first to get session cookies, then use for search."""
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        # Step 1: Get cookies from main page
        resp1 = await client.get(
            "https://cafef.vn/",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
            }
        )
        cookies = resp1.cookies
        print(f"Cookies from main page: {dict(cookies)}")

        # Step 2: Use those cookies for search
        resp2 = await client.get(
            "https://cafef.vn/tim-kiem.chn?keywords=FPT",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
                "Referer": "https://cafef.vn/",
            },
            cookies=cookies,
        )
        print(f"Search page status: {resp2.status_code}")

        soup = BeautifulSoup(resp2.text, "lxml")

        # Check for search results
        items = soup.select("div.search-item, div.item-search, div.search-result-item, tr.search-item, td.search-item")
        print(f"Search items found: {len(items)}")

        # Check for any div with id containing "search"
        search_divs = soup.select("[id*=search]")
        print(f"Divs with 'search' in id: {len(search_divs)}")
        for d in search_divs[:5]:
            print(f"  #{d.get('id')}: {d.get_text(strip=True)[:100]}")

        # Check if data is in a script tag
        scripts = soup.find_all("script")
        print(f"\nScript tags: {len(scripts)}")
        for s in scripts:
            text = s.get_text()
            if "FPT" in text or "data" in text.lower()[:200]:
                print(f"  Script with data: {text[:300]}")

        # Print the raw response length
        print(f"\nResponse length: {len(resp2.text)} chars")
        # Show some of the HTML
        print(f"\nHTML snippet:\n{resp2.text[5000:7000]}")

        return resp2


async def try_ajax_api():
    """Try common CafeF AJAX endpoints."""
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        # Get cookies first
        await client.get("https://cafef.vn/", headers={"User-Agent": "Mozilla/5.0 Chrome/147"})
        cookies = client.cookies

        apis = [
            ("GET", "https://cafef.vn/Ajax/PageNew/DataHistory/NewsSearch.ashx?symbol=FPT&page=1&size=20"),
            ("GET", "https://cafef.vn/Ajax/PageNew/SearchNews.ashx?keyword=FPT&page=1"),
            ("GET", "https://cafef.vn/api/search?keywords=FPT"),
            ("POST", "https://cafef.vn/tim-kiem.chn"),
        ]

        for method, url in apis:
            try:
                if method == "GET":
                    resp = await client.get(url, cookies=cookies, headers={"User-Agent": "Mozilla/5.0 Chrome/147", "Accept": "application/json"})
                else:
                    resp = await client.post(url, cookies=cookies, headers={"User-Agent": "Mozilla/5.0 Chrome/147", "Accept": "application/json"})
                print(f"{method} {url}: {resp.status_code} | {resp.text[:200]}")
            except Exception as e:
                print(f"{method} {url}: ERROR - {e}")


async def main():
    print("=== Test 1: Fetch search page ===")
    await get_cafef_cookies()

    print("\n\n=== Test 2: Try AJAX APIs ===")
    await try_ajax_api()


if __name__ == "__main__":
    asyncio.run(main())
