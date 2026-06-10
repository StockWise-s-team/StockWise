export interface User {
  id: string;
  email: string;
  role: string;
  fullName: string | null;
  createdAt: string | null;
}

export interface AuthResponse {
  accessToken: string;
  refreshToken: string | null;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  fullName?: string;
}

export interface UpdateProfileRequest {
  fullName: string;
}

export interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
}

export interface RefreshRequest {
  refreshToken: string;
}

export interface ApiError {
  error: string;
  message: string;
}

export interface LatestPrice {
  symbol: string;
  price: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  change: number;
  changePercent: number;
  tradeDate: string;
  updatedAt: string;
}

export interface OhlcPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface OhlcSeries {
  symbol: string;
  startDate: string;
  endDate: string;
  data: OhlcPoint[];
}

export interface FinancialRatioItem {
  period: string;
  peRatio: number | null;
  pbRatio: number | null;
  eps: number | null;
  roe: number | null;
  roa: number | null;
}

export interface FinancialRatioList {
  symbol: string;
  ratios: FinancialRatioItem[];
}

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

// ─── Portfolio & Paper Trading ───────────────────────────────────────────────
// Contract: portfolio-service (GET/POST/DELETE /portfolio*, GET /portfolio/pnl).

export type OrderSide = "BUY" | "SELL";
export type OrderStatus = "PENDING" | "FILLED" | "CANCELLED";

export interface PortfolioAccount {
  id: string;
  userId: string;
  virtualCash: number;
}

export interface PortfolioTransaction {
  id: string;
  symbol: string;
  type: OrderSide;
  price: number;
  quantity: number;
  executedAt: string;
}

// GET /portfolio response shape. The backend derives user ownership from JWT.
export interface PortfolioSnapshot {
  portfolio: PortfolioAccount;
  holdings: Holding[];
  transactions: PortfolioTransaction[];
}

// POST /portfolio/order request body.
export interface PlaceOrderRequest {
  symbol: string;
  type: OrderSide;
  quantity: number;
  price?: number;
}

// POST /portfolio/order & DELETE /portfolio/order/{id} response (snake_case order_id).
export interface OrderResult {
  order_id: string;
  status: OrderStatus;
  message: string;
}

// Per-holding view-model derived on the client from holdings + live prices.
export interface HoldingView extends Holding {
  currentPrice: number | null;
  costBasis: number;
  marketValue: number | null;
  unrealizedPnl: number | null;
}

// Aggregated portfolio view-model consumed by the dashboard & portfolio pages.
export interface PortfolioView {
  account: PortfolioAccount;
  holdings: HoldingView[];
  transactions: PortfolioTransaction[];
  holdingsValue: number; // valued at current price, falling back to avg cost
  totalValue: number; // cash + holdingsValue
  unrealizedPnl: number; // sum over holdings with a known current price
  realizedPnl: number; // GET /portfolio/pnl
  hasMissingPrices: boolean;
}

// ─── Admin / Pipeline ───────────────────────────────────────────────────────────

export interface NewsSource {
  id: string;
  name: string;
  baseUrl: string;
  crawlerType: string;
  isActive: boolean;
  createdAt: string;
  // snake_case variants from API
  base_url?: string;
  crawler_type?: string;
  is_active?: boolean;
  created_at?: string;
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

export interface PipelineProgress {
  task?: "seed" | "synthesis";
  phase: "idle" | "running" | "done" | "error";
  progress: number; // 0.0 – 1.0
  currentSymbol?: string | null;
  totalSymbols?: number;
  processedSymbols?: number;
  message?: string;
  errors?: string[];
  // snake_case variants from SSE
  current_symbol?: string | null;
  total_symbols?: number;
  processed_symbols?: number;
}

export interface PipelineProgressState {
  seed: PipelineProgress;
  synthesis: PipelineProgress;
}

export type PipelinePhase = "idle" | "seed" | "synth" | "done" | "error";

// ─── Pipeline Run History ────────────────────────────────────────────────────────

export type PipelineRunType = "seed" | "synthesis" | "stream_a" | "stream_b" | "stream_c";
export type PipelineRunTrigger = "scheduled" | "manual" | "api";
export type PipelineRunStatus = "running" | "success" | "partial" | "failed";

export interface PipelineRunSymbol {
  id: string;
  run_id: string;
  symbol: string;
  status: "success" | "error";
  error_message: string | null;
  processed_at: string;
}

export interface PipelineRun {
  id: string;
  run_type: PipelineRunType;
  trigger_type: PipelineRunTrigger;
  status: PipelineRunStatus;
  symbols_requested: number | null;
  symbols_processed: number | null;
  errors: string[];
  duration_seconds: number | null;
  started_at: string;
  finished_at: string | null;
  success_count: number;
  error_count: number;
}

export interface PipelineRunDetail extends PipelineRun {
  symbols_detail: PipelineRunSymbol[];
}

export interface PaginatedResponse<T> {
  runs?: T[];
  wikis?: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface PipelineStatsSummary {
  run_type: string;
  total_runs: number;
  total_symbols: number | null;
  avg_duration: number | null;
  first_run: string | null;
  last_run: string | null;
}

export interface PipelineStats {
  by_type_status: Array<{
    run_type: string;
    status: string;
    count: number;
    avg_duration: number | null;
    last_run: string | null;
  }>;
  summary: PipelineStatsSummary[];
}
