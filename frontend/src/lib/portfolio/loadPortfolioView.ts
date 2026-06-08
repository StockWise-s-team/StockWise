import type { PortfolioView } from "@/lib/types";
import type { MarketPriceProvider, PortfolioGateway } from "./ports";
import { buildPortfolioView } from "./valuation";

export interface PortfolioDataSource {
  gateway: PortfolioGateway;
  prices: MarketPriceProvider;
}

// Orchestrates the data needed for a PortfolioView. The snapshot is fetched first
// because it creates the portfolio on first visit (getOrCreate); the realized-PnL
// endpoint requires an existing portfolio (getRequired → 404), so fetching it
// concurrently would race on a brand-new account.
export async function loadPortfolioView(
  userId: string,
  { gateway, prices }: PortfolioDataSource
): Promise<PortfolioView> {
  const snapshot = await gateway.getSnapshot(userId);

  const symbols = Array.from(new Set(snapshot.holdings.map((h) => h.symbol)));
  const [realizedPnl, priceEntries] = await Promise.all([
    gateway.getRealizedPnl(userId),
    Promise.all(
      symbols.map(async (symbol) => [symbol, await prices.getLatestPrice(symbol)] as const)
    ),
  ]);

  return buildPortfolioView(snapshot, new Map(priceEntries), realizedPnl);
}
