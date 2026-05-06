from app.synthesis.wiki_repository import WikiRepository
from app.synthesis.merger import Merger
from typing import List

class SynthesisAgent:
    def __init__(self):
        self.wiki_repo = WikiRepository()
        self.merger = Merger()

    async def synthesize(self, symbols: List[str]):
        for symbol in symbols:
            old_wiki = self.wiki_repo.get_wiki(symbol)
            new_articles = []
            new_price_data = {}
            merged = await self.merger.merge(old_wiki, new_articles, new_price_data)
            self.wiki_repo.upsert_wiki(symbol, merged)
