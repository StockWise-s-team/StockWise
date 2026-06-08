import axios from "axios";
import type {
  OrderResult,
  PlaceOrderRequest,
  PortfolioSnapshot,
  StockPrice,
} from "@/lib/types";
import type { MarketPriceProvider, PortfolioGateway } from "./ports";

// The api-gateway only proxies /auth/**, so the portfolio and market services are
// called directly (both run permitAll + CORS *). userId is supplied per the
// portfolio-service contract; no JWT is required on these endpoints yet.
const portfolioClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_PORTFOLIO_SERVICE_URL || "http://localhost:18083",
  headers: { "Content-Type": "application/json" },
});

const marketClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_MARKET_SERVICE_URL || "http://localhost:18082",
  headers: { "Content-Type": "application/json" },
});

export class HttpPortfolioGateway implements PortfolioGateway {
  getSnapshot(userId: string): Promise<PortfolioSnapshot> {
    return portfolioClient
      .get<PortfolioSnapshot>("/portfolio", { params: { userId } })
      .then((r) => r.data);
  }

  getRealizedPnl(userId: string): Promise<number> {
    return portfolioClient
      .get<{ totalPnl: number }>("/portfolio/pnl", { params: { userId } })
      .then((r) => r.data.totalPnl);
  }

  placeOrder(request: PlaceOrderRequest): Promise<OrderResult> {
    return portfolioClient.post<OrderResult>("/portfolio/order", request).then((r) => r.data);
  }

  cancelOrder(orderId: string, userId: string): Promise<OrderResult> {
    return portfolioClient
      .delete<OrderResult>(`/portfolio/order/${orderId}`, { params: { userId } })
      .then((r) => r.data);
  }
}

export class HttpMarketPriceProvider implements MarketPriceProvider {
  async getLatestPrice(symbol: string): Promise<number | null> {
    try {
      const { data } = await marketClient.get<StockPrice>(`/market/price/${symbol}`);
      return data.close ?? null;
    } catch {
      // No price for this symbol yet — the contract allows null (valuation degrades).
      return null;
    }
  }
}

// Default singleton instances wired to the live HTTP backends.
export const portfolioGateway: PortfolioGateway = new HttpPortfolioGateway();
export const marketPriceProvider: MarketPriceProvider = new HttpMarketPriceProvider();
