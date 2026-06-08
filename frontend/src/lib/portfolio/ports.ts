import type { OrderResult, PlaceOrderRequest, PortfolioSnapshot } from "@/lib/types";

// Abstractions (DIP): higher-level modules — the loader and the React hook —
// depend on these interfaces, not on axios or any concrete HTTP client.

export interface PortfolioGateway {
  getSnapshot(userId: string): Promise<PortfolioSnapshot>;
  getRealizedPnl(userId: string): Promise<number>;
  placeOrder(request: PlaceOrderRequest): Promise<OrderResult>;
  cancelOrder(orderId: string, userId: string): Promise<OrderResult>;
}

export interface MarketPriceProvider {
  // Latest market price for a symbol, or null when it is unavailable.
  getLatestPrice(symbol: string): Promise<number | null>;
}
