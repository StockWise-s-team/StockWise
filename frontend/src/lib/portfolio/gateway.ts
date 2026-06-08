import api from "@/lib/api";
import type {
  OrderResult,
  PlaceOrderRequest,
  PortfolioSnapshot,
  StockPrice,
} from "@/lib/types";
import type { MarketPriceProvider, PortfolioGateway } from "./ports";

export class HttpPortfolioGateway implements PortfolioGateway {
  getSnapshot(): Promise<PortfolioSnapshot> {
    return api.get<PortfolioSnapshot>("/portfolio").then((r) => r.data);
  }

  getRealizedPnl(): Promise<number> {
    return api.get<{ totalPnl: number }>("/portfolio/pnl").then((r) => r.data.totalPnl);
  }

  placeOrder(request: PlaceOrderRequest): Promise<OrderResult> {
    return api.post<OrderResult>("/portfolio/order", request).then((r) => r.data);
  }

  cancelOrder(orderId: string): Promise<OrderResult> {
    return api.delete<OrderResult>(`/portfolio/order/${orderId}`).then((r) => r.data);
  }
}

export class HttpMarketPriceProvider implements MarketPriceProvider {
  async getLatestPrice(symbol: string): Promise<number | null> {
    try {
      const { data } = await api.get<StockPrice>(`/market/price/${symbol}`);
      return data.close ?? null;
    } catch {
      return null;
    }
  }
}

export const portfolioGateway: PortfolioGateway = new HttpPortfolioGateway();
export const marketPriceProvider: MarketPriceProvider = new HttpMarketPriceProvider();
