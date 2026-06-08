import type { OrderResult, PlaceOrderRequest, PortfolioSnapshot } from "@/lib/types";

export interface PortfolioGateway {
  getSnapshot(): Promise<PortfolioSnapshot>;
  getRealizedPnl(): Promise<number>;
  placeOrder(request: PlaceOrderRequest): Promise<OrderResult>;
  cancelOrder(orderId: string): Promise<OrderResult>;
}

export interface MarketPriceProvider {
  getLatestPrice(symbol: string): Promise<number | null>;
}
