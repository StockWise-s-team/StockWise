import api, { clearAuthData } from "./api";
import type { AuthResponse, LoginRequest, RegisterRequest, User, UpdateProfileRequest, ChangePasswordRequest } from "./types";

export const login = async (email: string, password: string): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>("/auth/login", { email, password } as LoginRequest);
  const data = response.data;
  localStorage.setItem("accessToken", data.accessToken);
  localStorage.setItem("refreshToken", data.refreshToken);
  localStorage.setItem("user", JSON.stringify(data.user));
  return data;
};

export const register = async (email: string, password: string, fullName?: string): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>("/auth/register", { email, password, fullName } as RegisterRequest);
  const data = response.data;
  localStorage.setItem("accessToken", data.accessToken);
  localStorage.setItem("refreshToken", data.refreshToken);
  localStorage.setItem("user", JSON.stringify(data.user));
  return data;
};

export const logout = async (): Promise<void> => {
  const refreshToken = localStorage.getItem("refreshToken");
  try {
    await api.post("/auth/logout", { refreshToken });
  } catch {
  } finally {
    clearAuthData();
  }
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

export const getCurrentUserFromApi = async (): Promise<User> => {
  const response = await api.get<User>("/auth/me");
  const user = response.data;
  localStorage.setItem("user", JSON.stringify(user));
  return user;
};

export const updateProfile = async (fullName: string): Promise<User> => {
  const response = await api.put<User>("/auth/profile", { fullName } as UpdateProfileRequest);
  const user = response.data;
  localStorage.setItem("user", JSON.stringify(user));
  return user;
};

export const changePassword = async (currentPassword: string, newPassword: string): Promise<void> => {
  await api.put("/auth/password", { currentPassword, newPassword } as ChangePasswordRequest);
};

export const getAccessToken = (): string | null => {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("accessToken");
};

export const isAuthenticated = (): boolean => {
  return !!getAccessToken();
};
