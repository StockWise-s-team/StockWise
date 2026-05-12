import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:18080",
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
        if (!error.config._retry) {
          error.config._retry = true;
          const refreshToken = localStorage.getItem("refreshToken");
          if (refreshToken) {
            return api.post("/auth/refresh", { refreshToken })
              .then((res) => {
                localStorage.setItem("accessToken", res.data.accessToken);
                localStorage.setItem("refreshToken", res.data.refreshToken);
                error.config.headers.Authorization = `Bearer ${res.data.accessToken}`;
                return api(error.config);
              })
              .catch(() => {
                window.location.href = "/login";
                return Promise.reject(error);
              });
          }
        }
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
