import type { Holding, HoldingView, PortfolioSnapshot, PortfolioView } from "@/lib/types";

// Pure valuation logic — no IO, no React. This is the correctness-critical money
// math for the module and is trivially unit-testable in isolation.

export function buildHoldingView(holding: Holding, currentPrice: number | null): HoldingView {
  const costBasis = holding.quantity * holding.avgPrice;
  const marketValue = currentPrice !== null ? holding.quantity * currentPrice : null;
  const unrealizedPnl =
    currentPrice !== null ? (currentPrice - holding.avgPrice) * holding.quantity : null;
  return { ...holding, currentPrice, costBasis, marketValue, unrealizedPnl };
}

export function buildPortfolioView(
  snapshot: PortfolioSnapshot,
  priceBySymbol: ReadonlyMap<string, number | null>,
  realizedPnl: number
): PortfolioView {
  const holdings = snapshot.holdings.map((h) =>
    buildHoldingView(h, priceBySymbol.get(h.symbol) ?? null)
  );

  // Holdings without a current price are valued at cost so the total stays meaningful.
  const holdingsValue = holdings.reduce((sum, h) => sum + (h.marketValue ?? h.costBasis), 0);
  const unrealizedPnl = holdings.reduce((sum, h) => sum + (h.unrealizedPnl ?? 0), 0);
  const hasMissingPrices = holdings.some((h) => h.currentPrice === null);

  return {
    account: snapshot.portfolio,
    holdings,
    transactions: snapshot.transactions,
    holdingsValue,
    totalValue: snapshot.portfolio.virtualCash + holdingsValue,
    unrealizedPnl,
    realizedPnl,
    hasMissingPrices,
  };
}
