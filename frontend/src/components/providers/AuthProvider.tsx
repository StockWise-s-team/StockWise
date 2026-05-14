"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { useRouter, usePathname } from "next/navigation";
import type { User } from "@/lib/types";

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
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const text = await res.text();
      if (!res.ok) {
        let errorCode: string | undefined;
        try {
          const json = JSON.parse(text);
          errorCode = json.error || json.message;
        } catch {
          // body rong hoac khong phai json
        }
        const friendly = mapErrorToMessage(errorCode, "login");
        throw new Error(friendly);
      }

      const data = JSON.parse(text);
      localStorage.setItem("accessToken", data.accessToken);
      localStorage.setItem("refreshToken", data.refreshToken);
      localStorage.setItem("user", JSON.stringify(data.user));
      setUser(data.user);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message);
      throw err;
    }
  };

  const register = async (email: string, password: string, fullName?: string) => {
    setError(null);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, fullName }),
      });

      const text = await res.text();
      if (!res.ok) {
        let errorCode: string | undefined;
        try {
          const json = JSON.parse(text);
          errorCode = json.error || json.message;
        } catch {
          // body rong hoac khong phai json
        }
        const friendly = mapErrorToMessage(errorCode, "register");
        throw new Error(friendly);
      }

      const data = JSON.parse(text);
      localStorage.setItem("accessToken", data.accessToken);
      localStorage.setItem("refreshToken", data.refreshToken);
      localStorage.setItem("user", JSON.stringify(data.user));
      setUser(data.user);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message);
      throw err;
    }
  };

  const logout = async () => {
    try {
      const token = localStorage.getItem("accessToken");
      if (token) {
        await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/logout`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
          },
        });
      }
    } catch {
      // ignore
    } finally {
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      localStorage.removeItem("user");
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
