import axios from "axios";

import type {
  NewsSource,
  TrackedSymbol,
  WikiData,
  PipelineStatus,
  PipelineProgress,
  PipelineProgressState,
} from "./types";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("accessToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
      }
    }
    return Promise.reject(error);
  }
);

export default api;

// ─── News Sources ───────────────────────────────────────────────────────────────

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

// ─── Tracked Symbols ───────────────────────────────────────────────────────────

export const trackedSymbolsApi = {
  list: () =>
    api.get<string[]>("/tracked-symbols").then((r) => r.data),

  add: (symbol: string) =>
    api.post<string>("/tracked-symbols", { symbol }).then((r) => r.data),

  remove: (symbol: string) =>
    api.delete(`/tracked-symbols/${symbol}`),

  triggerSeed: (symbols?: string[]) =>
    api.post("/scripts/seed", {
      symbols: symbols ?? [],
      prices_only: true,
      wiki_only: false,
    }),

  triggerSeedForSymbols: (symbols: string[]) =>
    api.post("/scripts/seed", { symbols }),
};

// ─── Wiki ─────────────────────────────────────────────────────────────────────

export const wikiApi = {
  get: (symbol: string) =>
    api.get<Record<string, unknown>>(`/company-wiki/${symbol}`).then((r) => {
      const w = r.data;
      const rawDate = String(w.updated_at ?? "");
      const isoDate = /^\d{4}-\d{2}-\d{2}T[\d:.]+$/.test(rawDate) ? rawDate + "Z" : rawDate;
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

  list: (params?: { limit?: number; offset?: number }) =>
    api.get<{ wikis: Record<string, unknown>[]; total: number; limit: number; offset: number }>("/company-wiki", { params }).then((r) => {
      const mapped = r.data.wikis.map((w: Record<string, unknown>): WikiData => {
        const rawDate = String(w.updated_at ?? "");
        const isoDate = /^\d{4}-\d{2}-\d{2}T[\d:.]+$/.test(rawDate) ? rawDate + "Z" : rawDate;
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
      return { wikis: mapped, total: r.data.total, limit: r.data.limit, offset: r.data.offset };
    }),
};

// ─── Pipeline Progress ─────────────────────────────────────────────────────────

export const pipelineApi = {
  getStatus: () =>
    api.get<PipelineStatus>("/pipeline/status").then((r) => r.data),

  triggerSynthesis: (symbols?: string[]) =>
    api.post("/synthesis/trigger", { symbols: symbols ?? [] }),

  pollProgress: () =>
    api.get<PipelineProgressState>("/pipeline/progress/poll").then((r) => r.data),
};

export function createProgressSSE(
  onEvent: (data: PipelineProgress) => void,
  onError?: (e: Event) => void
) {
  const baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const url = `${baseURL}/pipeline/progress`;
  const es = new EventSource(url);

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

// ─── Pipeline Run History ─────────────────────────────────────────────────────────

export const pipelineRunsApi = {
  list: (params?: { run_type?: string; status?: string; limit?: number; offset?: number }) =>
    api.get<{ runs: import("./types").PipelineRun[]; total: number; limit: number; offset: number }>("/pipeline/runs", { params }).then((r) => r.data),

  recent: (limit = 10) =>
    api.get<import("./types").PipelineRun[]>("/pipeline/runs/recent", { params: { limit } }).then((r) => r.data),

  detail: (runId: string) =>
    api.get<import("./types").PipelineRunDetail>(`/pipeline/runs/${runId}`).then((r) => r.data),

  stats: () =>
    api.get<import("./types").PipelineStats>("/pipeline/runs/stats").then((r) => r.data),
};
