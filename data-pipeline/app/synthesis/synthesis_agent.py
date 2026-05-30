import logging
from typing import List

from app.synthesis.merger import Merger
from app.synthesis.wiki_repository import WikiRepository

logger = logging.getLogger(__name__)


class SynthesisAgent:
    def __init__(self):
        self.wiki_repo = WikiRepository()
        self.merger = Merger()

    async def synthesize(self, symbols: List[str]) -> None:
        if not symbols:
            logger.warning("[SynthesisAgent] No symbols provided, skipping")
            return

        logger.info("[SynthesisAgent] Starting synthesis for %d symbols", len(symbols))

        for symbol in symbols:
            try:
                old_wiki = self.wiki_repo.get_wiki(symbol)
                new_articles = self.wiki_repo.get_recent_articles(symbol, limit=20)
                new_price_data = self.wiki_repo.get_recent_prices(symbol, limit=5)

                merged = await self.merger.merge(
                    old_wiki=old_wiki,
                    new_articles=new_articles,
                    new_price_data=new_price_data,
                    symbol=symbol,
                )
                self.wiki_repo.upsert_wiki(symbol, merged)
                logger.info(
                    "[SynthesisAgent] Completed synthesis for %s (v%d)",
                    symbol,
                    merged.get("version", 0),
                )
            except Exception as exc:
                logger.error(
                    "[SynthesisAgent] Failed to synthesize %s: %s: %s",
                    symbol,
                    type(exc).__name__,
                    exc,
                )
