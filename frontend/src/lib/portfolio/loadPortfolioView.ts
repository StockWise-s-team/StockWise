import type { PortfolioView } from "@/lib/types";
import type { MarketPriceProvider, PortfolioGateway } from "./ports";
import { buildPortfolioView } from "./valuation";

export interface PortfolioDataSource {
  gateway: PortfolioGateway;
  prices: MarketPriceProvider;
}

export async function loadPortfolioView({
  gateway,
  prices,
}: PortfolioDataSource): Promise<PortfolioView> {
  const snapshot = await gateway.getSnapshot();

  const symbols = Array.from(new Set(snapshot.holdings.map((h) => h.symbol)));
  const [realizedPnl, priceEntries] = await Promise.all([
    gateway.getRealizedPnl(),
    Promise.all(
      symbols.map(async (symbol) => [symbol, await prices.getLatestPrice(symbol)] as const)
    ),
  ]);

  return buildPortfolioView(snapshot, new Map(priceEntries), realizedPnl);
}
