"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { useRouter, usePathname } from "next/navigation";
import api, { clearAuthData } from "@/lib/api";
import type { User, LoginRequest, RegisterRequest } from "@/lib/types";

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function mapErrorToMessage(errorCode: string | undefined, action: "login" | "register"): string {
  if (!errorCode) return action === "login" ? "Sai tài khoản hoặc mật khẩu." : "Không thể kết nối đến server. Vui lòng thử lại.";

  const messages: Record<string, string> = {
    // Auth errors
    INVALID_CREDENTIALS: "Email hoặc mật khẩu không đúng. Vui lòng kiểm tra lại.",
    EMAIL_ALREADY_EXISTS: "Email này đã được đăng ký. Vui lòng đăng nhập hoặc sử dụng email khác.",
    EMAIL_ALREADY_REGISTERED: "Email này đã được đăng ký. Vui lòng đăng nhập hoặc sử dụng email khác.",
    USER_NOT_FOUND: "Tài khoản không tồn tại. Vui lòng đăng ký trước.",
    INVALID_REFRESH_TOKEN: "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.",
    UNAUTHORIZED: "Bạn không có quyền thực hiện thao tác này.",
    ACCESS_DENIED: "Bạn không có quyền truy cập trang này.",
    // Validation errors
    VALIDATION_ERROR: "Thông tin nhập không hợp lệ. Vui lòng kiểm tra lại.",
    // Service errors
    SERVICE_UNAVAILABLE: "Server đang bận. Vui lòng thử lại sau vài phút.",
    INTERNAL_ERROR: "Đã xảy ra lỗi không mong muốn. Vui lòng thử lại.",
  };

  return messages[errorCode] || (action === "login"
    ? "Đăng nhập thất bại. Vui lòng thử lại."
    : "Đăng ký thất bại. Vui lòng thử lại.");
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("accessToken");
      const userStr = localStorage.getItem("user");
      if (token && userStr) {
        try {
          setUser(JSON.parse(userStr) as User);
        } catch {
          localStorage.removeItem("accessToken");
          localStorage.removeItem("refreshToken");
          localStorage.removeItem("user");
        }
      }
    }
    setIsLoading(false);
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
      const res = await api.post<{ accessToken: string; refreshToken: string; user: User }>(
        "/auth/login",
        { email, password } as LoginRequest
      );
      const data = res.data;
      localStorage.setItem("accessToken", data.accessToken);
      localStorage.setItem("refreshToken", data.refreshToken);
      localStorage.setItem("user", JSON.stringify(data.user));
      setUser(data.user);
      router.push("/dashboard");
    } catch (err: any) {
      const friendly = mapErrorToMessage(err.response?.data?.error, "login");
      setError(friendly);
    }
  };

  const register = async (email: string, password: string, fullName?: string) => {
    setError(null);
    try {
      const res = await api.post<{ accessToken: string; refreshToken: string; user: User }>(
        "/auth/register",
        { email, password, fullName } as RegisterRequest
      );
      const data = res.data;
      localStorage.setItem("accessToken", data.accessToken);
      localStorage.setItem("refreshToken", data.refreshToken);
      localStorage.setItem("user", JSON.stringify(data.user));
      setUser(data.user);
      router.push("/dashboard");
    } catch (err: any) {
      const friendly = mapErrorToMessage(err.response?.data?.error, "register");
      setError(friendly);
    }
  };

  const logout = async () => {
    const refreshToken = localStorage.getItem("refreshToken");
    try {
      const token = localStorage.getItem("accessToken");
      if (token) {
        await api.post("/auth/logout", { refreshToken });
      }
    } catch {
    } finally {
      clearAuthData();
      setUser(null);
      router.push("/login");
    }
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
        error,
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
