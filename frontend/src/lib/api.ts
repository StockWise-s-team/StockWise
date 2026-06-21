import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { getAccessToken, setAccessToken, clearAccessToken } from "./tokenStore";

import type {
  NewsSource,
  UserNewsSource,
  TrackedSymbol,
  WikiData,
  PipelineStatus,
  PipelineProgress,
  PipelineProgressState,
  LatestPrice,
  OhlcSeries,
  IntradayOhlcSeries,
  FinancialRatioList,
  AdvisorMessage,
  AdvisorSession,
  SSEEnvelope,
} from "./types";
import { parseSSEEnvelopeFrames } from "./sse";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:18080",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

const apiBaseURL = () =>
  (process.env.NEXT_PUBLIC_API_URL || "http://localhost:18080").replace(/\/$/, "");

const AUTH_BYPASS_PATHS = [
  "/auth/refresh",
  "/auth/refresh-token-cookie",
  "/auth/login",
  "/auth/register",
];

const isAuthBypass = (url: string | undefined): boolean => {
  if (!url) return false;
  return AUTH_BYPASS_PATHS.some((path) => url.includes(path));
};

let refreshPromise: Promise<string | null> | null = null;
let refreshSubscribers: Array<(token: string | null) => void> = [];

const subscribeTokenRefresh = (callback: (token: string | null) => void) => {
  refreshSubscribers.push(callback);
};

const onRefreshComplete = (token: string | null) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !isAuthBypass(originalRequest.url)
    ) {
      if (originalRequest._retry) {
        clearAccessToken();
        window.location.href = "/login";
        return Promise.reject(error);
      }

      if (!refreshPromise) {
        originalRequest._retry = true;
        refreshPromise = performRefresh(originalRequest);
      }

      try {
        const newToken = await refreshPromise;
        if (newToken) {
          return api(originalRequest);
        } else {
          clearAccessToken();
          window.location.href = "/login";
          return Promise.reject(error);
        }
      } catch {
        clearAccessToken();
        window.location.href = "/login";
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

const performRefresh = async (
  originalRequest: InternalAxiosRequestConfig & { _retry?: boolean }
): Promise<string | null> => {
  try {
    const refreshResponse = await api.post<{ accessToken?: string }>(
      "/auth/refresh-token-cookie"
    );
    const newToken = refreshResponse.data?.accessToken ?? null;

    if (newToken) {
      setAccessToken(newToken);
    }

    onRefreshComplete(newToken);
    refreshPromise = null;
    return newToken;
  } catch {
    onRefreshComplete(null);
    refreshPromise = null;
    clearAccessToken();
    throw new Error("Refresh failed");
  }
};

export { subscribeTokenRefresh };
export default api;

export const marketApi = {
  getLatestPrice: (symbol: string) =>
    api.get<LatestPrice>(`/market/price/${symbol}`).then((r) => r.data),

  getLatestPriceBatch: (symbols: string[]) =>
    api
      .get<Record<string, LatestPrice>>(`/market/price/batch`, {
        params: { symbols: symbols.join(",") },
      })
      .then((r) => r.data),

  getOhlc: (symbol: string, params?: { startDate?: string; endDate?: string }) =>
    api
      .get<OhlcSeries>(`/market/ohlc/${symbol}`, { params })
      .then((r) => r.data),

  getRatios: (symbol: string) =>
    api.get<FinancialRatioList>(`/market/ratio/${symbol}`).then((r) => r.data),

  getIntradayOhlc: (symbol: string, interval = "5m") =>
    api
      .get<IntradayOhlcSeries>(`/market/ohlc/intraday/${symbol}`, {
        params: { interval },
      })
      .then((r) => r.data),
};

export const newsSourcesApi = {
  list: () =>
    api.get<NewsSource[]>("/news-sources").then((r) =>
      r.data.map((s) => ({
        ...s,
        baseUrl: s.base_url ?? s.baseUrl,
        crawlerType: s.crawler_type ?? s.crawlerType,
        isActive: s.is_active ?? s.isActive,
        createdAt: s.created_at ?? s.createdAt,
      }))
    ),

  toggle: (id: string, isActive: boolean) =>
    api.patch<NewsSource>(`/news-sources/${id}`, { is_active: isActive }),
};

export const trackedSymbolsApi = {
  list: () => api.get<string[]>("/tracked-symbols").then((r) => r.data),

  add: (symbol: string) =>
    api.post<string>("/tracked-symbols", { symbol }).then((r) => r.data),

  remove: (symbol: string) => api.delete(`/tracked-symbols/${symbol}`),

  triggerSeed: (symbols?: string[]) =>
    api.post("/scripts/seed", {
      symbols: symbols ?? [],
      prices_only: true,
      wiki_only: false,
    }),

  triggerSeedForSymbols: (symbols: string[]) => api.post("/scripts/seed", { symbols }),
};

export const userSelectionsApi = {
  listSymbols: () =>
    api.get<string[]>("/user/tracked-symbols").then((r) => r.data),

  updateSymbols: (symbols: string[]) =>
    api.put("/user/tracked-symbols", { symbols }),

  listNewsSources: () =>
    api.get<UserNewsSource[]>("/user/news-sources").then((r) =>
      r.data.map((s) => ({
        ...s,
        baseUrl: s.base_url ?? s.baseUrl,
        crawlerType: s.crawler_type ?? s.crawlerType,
        isActive: s.is_active ?? s.isActive,
        isSelected: s.is_selected ?? s.isSelected,
        createdAt: s.created_at ?? s.createdAt,
      }))
    ),

  updateNewsSources: (sourceIds: string[]) =>
    api.put("/user/news-sources", { source_ids: sourceIds }),
};

export const wikiApi = {
  get: (symbol: string) =>
    api.get<Record<string, unknown>>(`/company-wiki/${symbol}`).then((r) => {
      const w = r.data;
      const rawDate = String(w.updated_at ?? "");
      const isoDate = /^\d{4}-\d{2}-\d{2}T[\d:.]+$/.test(rawDate)
        ? rawDate + "Z"
        : rawDate;
      return {
        symbol: w.symbol,
        companyName: w.company_name,
        sector: w.sector,
        businessSummary: w.business_summary,
        recentPerformance: w.recent_performance,
        keyRisks: w.key_risks ?? [],
        sentiment: w.sentiment,
        lastNewsSummary: w.last_news_summary,
        financialsSnapshot: w.financials_snapshot,
        version: w.version,
        updatedAt: isoDate,
      } as WikiData;
    }),

  list: (params?: { limit?: number; offset?: number; search?: string }) =>
    api
      .get<{
        wikis: Record<string, unknown>[];
        total: number;
        limit: number;
        offset: number;
      }>("/company-wiki", { params })
      .then((r) => {
        const mapped = r.data.wikis.map((w: Record<string, unknown>): WikiData => {
          const rawDate = String(w.updated_at ?? "");
          const isoDate = /^\d{4}-\d{2}-\d{2}T[\d:.]+$/.test(rawDate)
            ? rawDate + "Z"
            : rawDate;
          return {
            symbol: String(w.symbol ?? ""),
            companyName: String(w.company_name ?? ""),
            sector: String(w.sector ?? ""),
            businessSummary: String(w.business_summary ?? ""),
            recentPerformance: (w.recent_performance ?? null) as WikiData["recentPerformance"],
            keyRisks: Array.isArray(w.key_risks) ? (w.key_risks as string[]) : [],
            sentiment: String(w.sentiment ?? ""),
            lastNewsSummary: String(w.last_news_summary ?? ""),
            financialsSnapshot: (w.financials_snapshot ?? null) as WikiData["financialsSnapshot"],
            version: Number(w.version ?? 0),
            updatedAt: isoDate,
          };
        });
        return {
          wikis: mapped,
          total: r.data.total,
          limit: r.data.limit,
          offset: r.data.offset,
        };
      }),
};

export const pipelineApi = {
  getStatus: () => api.get<PipelineStatus>("/pipeline/status").then((r) => r.data),

  triggerSynthesis: (symbols?: string[]) =>
    api.post("/synthesis/trigger", { symbols: symbols ?? [] }),

  pollProgress: () =>
    api.get<PipelineProgressState>("/pipeline/progress/poll").then((r) => r.data),
};

const mapAdvisorSession = (session: AdvisorSession): AdvisorSession => ({
  ...session,
  createdAt: session.createdAt ?? session.created_at ?? "",
  updatedAt: session.updatedAt ?? session.updated_at ?? "",
});

const mapAdvisorMessage = (message: AdvisorMessage): AdvisorMessage => ({
  ...message,
  sessionId: message.sessionId ?? message.session_id ?? "",
  createdAt: message.createdAt ?? message.created_at ?? "",
  role: message.role,
  metadata: message.metadata ?? {},
});

async function refreshAccessTokenForFetch(): Promise<string | null> {
  try {
    const response = await api.post<{ accessToken?: string }>("/auth/refresh-token-cookie");
    const token = response.data?.accessToken ?? null;
    if (token) {
      setAccessToken(token);
    }
    return token;
  } catch {
    clearAccessToken();
    return null;
  }
}

async function postAdvisorStream(
  body: { message: string; session_id?: string },
  token: string | null,
  signal?: AbortSignal
): Promise<Response> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "text/event-stream",
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return fetch(`${apiBaseURL()}/api/v1/advisor/chat`, {
    method: "POST",
    headers,
    credentials: "include",
    body: JSON.stringify(body),
    signal,
  });
}

export const advisorApi = {
  listSessions: () =>
    api
      .get<AdvisorSession[]>("/api/v1/advisor/sessions")
      .then((r) => r.data.map(mapAdvisorSession)),

  getMessages: (sessionId: string) =>
    api
      .get<AdvisorMessage[]>(`/api/v1/advisor/sessions/${sessionId}/messages`)
      .then((r) => r.data.map(mapAdvisorMessage)),

  deleteSession: (sessionId: string) =>
    api.delete<void>(`/api/v1/advisor/sessions/${sessionId}`),

  streamChat: async ({
    message,
    sessionId,
    signal,
    onEnvelope,
  }: {
    message: string;
    sessionId?: string | null;
    signal?: AbortSignal;
    onEnvelope: (envelope: SSEEnvelope) => void;
  }) => {
    const body = {
      message,
      ...(sessionId ? { session_id: sessionId } : {}),
    };

    let response = await postAdvisorStream(body, getAccessToken(), signal);
    if (response.status === 401) {
      const refreshedToken = await refreshAccessTokenForFetch();
      if (refreshedToken) {
        response = await postAdvisorStream(body, refreshedToken, signal);
      }
    }

    if (!response.ok || !response.body) {
      throw new Error(`Advisor stream failed with status ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const parsed = parseSSEEnvelopeFrames(buffer);
      buffer = parsed.remainder;
      parsed.events.forEach(onEnvelope);
    }

    buffer += decoder.decode();
    const parsed = parseSSEEnvelopeFrames(buffer + "\n\n");
    parsed.events.forEach(onEnvelope);
  },
};

export function createProgressSSE(
  onEvent: (data: PipelineProgress) => void,
  onError?: (e: Event) => void
) {
  const baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:18080";
  const url = `${baseURL}/pipeline/progress`;
  const es = new EventSource(url, { withCredentials: true });

  es.onmessage = (evt) => {
    try {
      const data: PipelineProgress = JSON.parse(evt.data);
      onEvent(data);
    } catch {
      // ignore parse errors
    }
  };

  if (onError) {
    es.onerror = onError;
  }

  return es;
}

export const pipelineRunsApi = {
  list: (params?: {
    run_type?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }) =>
    api
      .get<{
        runs: import("./types").PipelineRun[];
        total: number;
        limit: number;
        offset: number;
      }>("/pipeline/runs", { params })
      .then((r) => r.data),

  recent: (limit = 10) =>
    api
      .get<import("./types").PipelineRun[]>("/pipeline/runs/recent", {
        params: { limit },
      })
      .then((r) => r.data),

  detail: (runId: string) =>
    api
      .get<import("./types").PipelineRunDetail>(`/pipeline/runs/${runId}`)
      .then((r) => r.data),

  stats: () =>
    api.get<import("./types").PipelineStats>("/pipeline/runs/stats").then((r) => r.data),
};
