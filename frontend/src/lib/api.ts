import axios from "axios";

import type {
  NewsSource,
  TrackedSymbol,
  WikiData,
  PipelineStatus,
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
    api.get<NewsSource[]>("/news-sources").then((r) => r.data),

  toggle: (id: string, isActive: boolean) =>
    api.patch<NewsSource>(`/news-sources/${id}`, { isActive }),
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
      prices: true,
      wiki: false,
      ratios: false,
    }),
};

// ─── Wiki ─────────────────────────────────────────────────────────────────────

export const wikiApi = {
  get: (symbol: string) =>
    api.get<WikiData>(`/company-wiki/${symbol}`).then((r) => r.data),

  list: (limit = 50) =>
    api.get<WikiData[]>("/company-wiki", { params: { limit } }).then((r) => r.data),
};

// ─── Pipeline Status ───────────────────────────────────────────────────────────

export const pipelineApi = {
  getStatus: () =>
    api.get<PipelineStatus>("/pipeline/status").then((r) => r.data),

  triggerSynthesis: (symbols?: string[]) =>
    api.post("/synthesis/trigger", { symbols: symbols ?? [] }),
};
