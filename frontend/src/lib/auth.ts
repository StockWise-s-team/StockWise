import api from "./api";
import type { AuthResponse, LoginRequest, RegisterRequest, User } from "./types";

export const login = async (email: string, password: string): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>("/auth/login", { email, password } as LoginRequest);
  const data = response.data;
  localStorage.setItem("accessToken", data.accessToken);
  localStorage.setItem("refreshToken", data.refreshToken);
  localStorage.setItem("user", JSON.stringify(data.user));
  return data;
};

export const register = async (email: string, password: string): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>("/auth/register", { email, password } as RegisterRequest);
  const data = response.data;
  localStorage.setItem("accessToken", data.accessToken);
  localStorage.setItem("refreshToken", data.refreshToken);
  localStorage.setItem("user", JSON.stringify(data.user));
  return data;
};

export const logout = (): void => {
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
  localStorage.removeItem("user");
};

export const getCurrentUser = (): User | null => {
  if (typeof window === "undefined") return null;
  const userStr = localStorage.getItem("user");
  if (!userStr) return null;
  try {
    return JSON.parse(userStr) as User;
  } catch {
    return null;
  }
};

export const getAccessToken = (): string | null => {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("accessToken");
};

export const isAuthenticated = (): boolean => {
  return !!getAccessToken();
};
