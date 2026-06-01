import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { getAccessToken, setAccessToken, clearAccessToken } from "./tokenStore";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:18080",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// Endpoints that should never trigger token refresh logic
const AUTH_BYPASS_PATHS = ["/auth/refresh", "/auth/login", "/auth/register"];

const isAuthBypass = (url: string | undefined): boolean => {
  if (!url) return false;
  return AUTH_BYPASS_PATHS.some((path) => url.includes(path));
};

// Shared refresh promise — prevents multiple simultaneous refresh calls
let refreshPromise: Promise<string | null> | null = null;

// Subscribers wait for the ongoing refresh to finish
let refreshSubscribers: Array<(token: string | null) => void> = [];

const subscribeTokenRefresh = (callback: (token: string | null) => void) => {
  refreshSubscribers.push(callback);
};

const onRefreshComplete = (token: string | null) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

// Request interceptor: attach access token from memory store
api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: handle 401 with refresh logic
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Only handle 401 on non-auth-bypass endpoints, and only once
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

const performRefresh = async (originalRequest: InternalAxiosRequestConfig & { _retry?: boolean }): Promise<string | null> => {
  try {
    // Refresh token is in HttpOnly cookie — no manual header needed
    const refreshResponse = await api.post<{ accessToken?: string }>("/auth/refresh");
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
