export interface User {
  id: string;
  email: string;
  role: string;
}

export interface AuthResponse {
  accessToken: string;
  refreshToken: string;
}

export interface StockPrice {
  symbol: string;
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface OHLCV extends StockPrice {}

export interface Holding {
  symbol: string;
  quantity: number;
  avgPrice: number;
}

export interface Portfolio {
  userId: string;
  virtualCash: number;
  holdings: Holding[];
}

export interface SSEEvent {
  type: "thought" | "answer" | "error";
  content: string;
}
