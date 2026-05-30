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

// ─── Admin / Pipeline ───────────────────────────────────────────────────────────

export interface NewsSource {
  id: string;
  name: string;
  baseUrl: string;
  crawlerType: string;
  isActive: boolean;
  createdAt: string;
}

export interface TrackedSymbol {
  symbol: string;
  addedAt: string;
}

export interface WikiData {
  symbol: string;
  companyName: string;
  sector: string;
  businessSummary: string;
  recentPerformance: {
    trend: string;
    notable: string;
  };
  keyRisks: string[];
  sentiment: string;
  lastNewsSummary: string;
  financialsSnapshot: {
    pe: number;
    pb: number;
    roe: number;
  };
  version: number;
  updatedAt: string;
}

export interface PipelineStatus {
  streamA: {
    lastRun: string | null;
    status: "idle" | "running" | "error";
    symbolsProcessed: number;
  };
  streamB: {
    lastRun: string | null;
    status: "idle" | "running" | "error";
    articlesIngested: number;
  };
  synthesis: {
    lastRun: string | null;
    status: "idle" | "running" | "error";
    wikisUpdated: number;
  };
}
