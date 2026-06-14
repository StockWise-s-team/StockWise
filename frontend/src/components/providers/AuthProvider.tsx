"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import { useRouter, usePathname } from "next/navigation";
import api from "@/lib/api";
import { setAccessToken, clearAccessToken } from "@/lib/tokenStore";
import type {
  User,
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  UpdateProfileRequest,
  ChangePasswordRequest,
} from "@/lib/types";

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (fullName: string) => Promise<User>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  refreshUser: () => Promise<User>;
  error: string | null;
  setError: (error: string | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const STORAGE_KEY = "stockwise_user";

function getStoredUser(): User | null {
  if (typeof window === "undefined") return null;
  const userStr = localStorage.getItem(STORAGE_KEY);
  if (!userStr) return null;
  try {
    return JSON.parse(userStr) as User;
  } catch {
    return null;
  }
}

function saveStoredUser(user: User | null) {
  if (typeof window === "undefined") return;
  if (user) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
    document.cookie = `user_role=${user.role}; path=/; max-age=604800; SameSite=Lax`;
  } else {
    localStorage.removeItem(STORAGE_KEY);
    document.cookie = "user_role=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
  }
}

function mapErrorToMessage(errorCode: string | undefined, action: "login" | "register"): string {
  if (!errorCode) return action === "login" ? "Sai tài khoản hoặc mật khẩu." : "Không thể kết nối đến server. Vui lòng thử lại.";

  const messages: Record<string, string> = {
    INVALID_CREDENTIALS: "Email hoặc mật khẩu không đúng. Vui lòng kiểm tra lại.",
EMAIL_ALREADY_EXISTS: "Email này đã được đăng ký. Vui lòng đăng nhập hoặc sử dụng email khác.",
EMAIL_ALREADY_REGISTERED: "Email này đã được đăng ký. Vui lòng đăng nhập hoặc sử dụng email khác.",
USER_NOT_FOUND: "Tài khoản không tồn tại. Vui lòng đăng ký trước.",
INVALID_REFRESH_TOKEN: "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.",
UNAUTHORIZED: "Bạn không có quyền thực hiện thao tác này.",

ACCESS_DENIED: "Bạn không có quyền truy cập trang này.",
VALIDATION_ERROR: "Thông tin nhập không hợp lệ. Vui lòng kiểm tra lại.",
INCORRECT_PASSWORD: "Mật khẩu hiện tại không đúng. Vui lòng thử lại.",
SERVICE_UNAVAILABLE: "Server đang bận. Vui lòng thử lại sau vài phút.",
INTERNAL_ERROR: "Đã xảy ra lỗi không mong muốn. Vui lòng thử lại.",
  };

  return messages[errorCode] || (action === "login"
    ? "Đăng nhập thất bại. Vui lòng thử lại."
    : "Đăng ký thất bại. Vui lòng thử lại.");
}

// Refresh access token using HttpOnly cookie (no manual token needed)
async function tryRestoreToken(): Promise<boolean> {
  try {
    const response = await api.post<{ accessToken?: string }>("/auth/refresh-token-cookie");
    const newToken = response.data?.accessToken;
    if (newToken) {
      setAccessToken(newToken);
      return true;
    }
  } catch (err: any) {
    const status = err?.response?.status;
    // Only clear session on explicit auth rejection (401/403).
    // For server errors (500, network errors), keep user optimistically
    // and let the axios 401 interceptor handle retries on subsequent requests.
    if (status === 400 || status === 401 || status === 403) {
      saveStoredUser(null);
      clearAccessToken();
      return false;
    }
    // Server error or network issue — keep user logged in optimistically
    return true;
  }
  saveStoredUser(null);
  clearAccessToken();
  return false;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const pathname = usePathname();

  // On mount: restore token from refresh cookie if user profile exists in localStorage.
  // Access token in memory is already gone on reload, so we must rehydrate from /auth/refresh.
  useEffect(() => {
    async function initAuth() {
      const storedUser = getStoredUser();
      if (storedUser) {
        setUser(storedUser);
        const restored = await tryRestoreToken();
        if (!restored) {
          setUser(null);
        }
      }
      setIsLoading(false);
    }
    void initAuth();
  }, []);

  useEffect(() => {
    if (!isLoading) {
      if (!user && !pathname.startsWith("/login") && !pathname.startsWith("/register") && pathname !== "/") {
        router.push("/login");
      }
    }
  }, [isLoading, user, pathname, router]);

  const login = async (email: string, password: string) => {
    setError(null);
    try {
      const response = await api.post<AuthResponse>("/auth/login", { email, password } as LoginRequest);
      const userData = response.data.user;
      const accessToken = response.data.accessToken;
      if (accessToken) {
        // Store access token in memory only — never persist to localStorage
        setAccessToken(accessToken);
      }
      saveStoredUser(userData);
      setUser(userData);
      router.push("/dashboard");
    } catch (err: any) {
      const friendly = mapErrorToMessage(err.response?.data?.err, "login");
      setError(friendly);
      throw err;
    }
  };

  const register = async (email: string, password: string, fullName?: string) => {
    setError(null);
    try {
      const response = await api.post<AuthResponse>("/auth/register", { email, password, fullName } as RegisterRequest);
      const userData = response.data.user;
      const accessToken = response.data.accessToken;
      if (accessToken) {
        // Store access token in memory only — never persist to localStorage
        setAccessToken(accessToken);
      }
      saveStoredUser(userData);
      setUser(userData);
      router.push("/dashboard");
    } catch (err: any) {
      const friendly = mapErrorToMessage(err.response?.data?.err, "register");
      setError(friendly);
      throw err;
    }
  };

  const logout = async () => {
    try {
      await api.post("/auth/logout");
    } catch {
      // Ignore logout errors — clear everything regardless
    } finally {
      saveStoredUser(null);
      clearAccessToken();
      setUser(null);
      router.push("/login");
    }
  };

  const refreshUser = async (): Promise<User> => {
    const response = await api.get<User>("/auth/me");
    const userData = response.data;
    saveStoredUser(userData);
    setUser(userData);
    return userData;
  };

  const updateProfile = async (fullName: string): Promise<User> => {
    const response = await api.put<User>("/auth/profile", { fullName } as UpdateProfileRequest);
    const userData = response.data;
    saveStoredUser(userData);
    setUser(userData);
    return userData;
  };

  const changePassword = async (currentPassword: string, newPassword: string): Promise<void> => {
    await api.put("/auth/password", { currentPassword, newPassword } as ChangePasswordRequest);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        updateProfile,
        changePassword,
        refreshUser,
        error,
        setError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
