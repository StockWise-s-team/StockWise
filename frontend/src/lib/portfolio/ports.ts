import type { OrderResult, PlaceOrderRequest, PortfolioOrder, PortfolioSnapshot } from "@/lib/types";

export interface PortfolioGateway {
  getSnapshot(): Promise<PortfolioSnapshot>;
  getRealizedPnl(): Promise<number>;
  getOrders(): Promise<PortfolioOrder[]>;
  placeOrder(request: PlaceOrderRequest): Promise<OrderResult>;
  cancelOrder(orderId: string): Promise<OrderResult>;
}

export interface MarketPriceProvider {
  getLatestPrice(symbol: string): Promise<number | null>;
}
