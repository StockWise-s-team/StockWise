import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:18080",
  headers: {
    "Content-Type": "application/json",
  },
});

let isRefreshing = false;
let refreshSubscribers: Array<(token: string) => void> = [];

const subscribeTokenRefresh = (callback: (token: string) => void) => {
  refreshSubscribers.push(callback);
};

const onRefreshComplete = (token: string) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

const clearAuthData = () => {
  if (typeof window !== "undefined") {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("user");
  }
};

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
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
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && originalRequest) {
      if (originalRequest._retry) {
        clearAuthData();
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        return Promise.reject(error);
      }

      if (!isRefreshing) {
        isRefreshing = true;
        originalRequest._retry = true;

        const refreshToken = localStorage.getItem("refreshToken");
        if (!refreshToken) {
          isRefreshing = false;
          clearAuthData();
          if (typeof window !== "undefined") {
            window.location.href = "/login";
          }
          return Promise.reject(error);
        }

        try {
          const res = await api.post("/auth/refresh", { refreshToken });
          const { accessToken, refreshToken: newRefreshToken } = res.data;
          localStorage.setItem("accessToken", accessToken);
          localStorage.setItem("refreshToken", newRefreshToken);
          onRefreshComplete(accessToken);
          isRefreshing = false;

          originalRequest.headers.Authorization = `Bearer ${accessToken}`;
          return api(originalRequest);
        } catch (refreshError) {
          isRefreshing = false;
          refreshSubscribers = [];
          clearAuthData();
          if (typeof window !== "undefined") {
            window.location.href = "/login";
          }
          return Promise.reject(refreshError);
        }
      }

      return new Promise((resolve, reject) => {
        subscribeTokenRefresh((token: string) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          resolve(api(originalRequest));
        });
      });
    }

    return Promise.reject(error);
  }
);

export { clearAuthData };
export default api;
