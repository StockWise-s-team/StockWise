import google.generativeai as genai
from app.config import settings
from typing import Dict, Any, List

class Merger:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def merge(self, old_wiki: Dict[str, Any], new_articles: List[str], new_price_data: Dict[str, Any]) -> Dict[str, Any]:
        if old_wiki is None:
            old_wiki = {
                "symbol": "STUB",
                "company_name": "Stub Company",
                "sector": "Unknown",
                "business_summary": "...",
                "recent_performance": {"trend": "neutral", "notable": ""},
                "key_risks": [],
                "sentiment": "neutral",
                "last_news_summary": "",
                "financials_snapshot": {"pe": 0, "pb": 0, "roe": 0},
                "version": 1
            }
        return old_wiki
