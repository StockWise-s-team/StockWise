"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Bot,
  Briefcase,
  FlaskConical,
  LayoutDashboard,
  LogOut,
  Menu,
  Settings,
  Shield,
  User,
  X,
} from "lucide-react";
import { useState, useEffect, useRef, ReactNode } from "react";
import { clsx } from "clsx";
import { AuthProvider, useAuth } from "@/components/providers/AuthProvider";
import { MarketDataProvider, useMarketData } from "@/components/providers/MarketDataProvider";
import { trackedSymbolsApi } from "@/lib/api";

const navItems = [
  { href: "/dashboard", label: "Overview", code: "01", icon: LayoutDashboard },
  { href: "/dashboard/portfolio", label: "Portfolio", code: "02", icon: Briefcase },
  { href: "/dashboard/sandbox", label: "Sandbox", code: "03", icon: FlaskConical },
  { href: "/dashboard/advisor", label: "AI Advisor", code: "04", icon: Bot },
  { href: "/dashboard/profile", label: "Profile", code: "05", icon: User },
  { href: "/dashboard/settings", label: "Settings", code: "06", icon: Settings },
  { href: "/dashboard/admin", label: "Admin", code: "07", icon: Shield },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const { logout, user, isLoading } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const filteredNavItems = navItems.filter((item) => {
    if (item.href === "/dashboard/admin") {
      return user?.role === "ROLE_ADMIN";
    }
    return true;
  });

  const isActive = (href: string) =>
    href === "/dashboard" ? pathname === href : pathname.startsWith(href);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-terminal-bg font-mono text-terminal-text">
        <div className="text-center space-y-4">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-terminal-border border-t-terminal-accent mx-auto" />
          <p className="text-[10px] uppercase tracking-[0.2em] text-terminal-muted">Initializing Console...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-terminal-bg font-mono text-terminal-text">
      <header className="sticky top-0 z-40 flex h-12 items-center justify-between border-b border-terminal-border bg-terminal-surface/95 px-4 backdrop-blur md:hidden">
        <Link
          href="/dashboard"
          className="font-display text-sm font-bold uppercase tracking-[0.2em] text-terminal-accent"
        >
          StockWise
        </Link>
        <button
          type="button"
          onClick={() => setSidebarOpen((current) => !current)}
          aria-label={sidebarOpen ? "Close navigation" : "Open navigation"}
          className="flex h-8 w-8 items-center justify-center rounded border border-terminal-border text-terminal-muted transition-colors hover:border-terminal-accent/40 hover:text-terminal-accent"
        >
          {sidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
        </button>
      </header>

      {sidebarOpen && (
        <button
          type="button"
          aria-label="Close navigation"
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-40 bg-black/70 md:hidden"
        />
      )}

      <aside
        className={clsx(
          "fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-terminal-border bg-terminal-surface transition-transform duration-200 md:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="border-b border-terminal-border px-5 py-5">
          <div className="flex items-center justify-between">
            <Link
              href="/dashboard"
              onClick={() => setSidebarOpen(false)}
              className="font-display text-base font-bold uppercase tracking-[0.2em] text-terminal-accent"
            >
              StockWise
            </Link>
            <span className="font-mono text-[9px] uppercase tracking-widest text-terminal-muted">
              v0.1
            </span>
          </div>
          <div className="mt-3 flex items-center justify-between border-t border-terminal-border pt-3">
            <span className="font-mono text-[9px] uppercase tracking-widest text-terminal-muted">
              Market console
            </span>
            <span className="inline-flex items-center gap-1.5 font-mono text-[9px] uppercase text-terminal-green">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-terminal-green" />
              Online
            </span>
          </div>
        </div>

        <nav className="min-h-0 flex-1 overflow-y-auto px-3 py-4">
          <p className="mb-2 px-2 font-mono text-[9px] uppercase tracking-[0.18em] text-terminal-muted">
            Navigation
          </p>
          <div className="space-y-1">
            {filteredNavItems.map((item) => {
              const active = isActive(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setSidebarOpen(false)}
                  aria-current={active ? "page" : undefined}
                  className={clsx(
                    "group flex items-center gap-3 rounded border px-3 py-2.5 transition-colors",
                    active
                      ? "border-terminal-accent/30 bg-terminal-accent/[0.07] text-terminal-accent"
                      : "border-transparent text-terminal-muted hover:border-terminal-border hover:bg-terminal-bg hover:text-terminal-text"
                  )}
                >
                  <span className="font-mono text-[9px] text-terminal-muted/70">
                    {item.code}
                  </span>
                  <item.icon className="h-3.5 w-3.5" />
                  <span className="flex-1 font-mono text-[10px] font-medium uppercase tracking-wider">
                    {item.label}
                  </span>
                  <span
                    className={clsx(
                      "h-1 w-1 rounded-full transition-colors",
                      active ? "bg-terminal-accent" : "bg-transparent group-hover:bg-terminal-muted"
                    )}
                  />
                </Link>
              );
            })}
          </div>
        </nav>

        <div className="border-t border-terminal-border p-3">
          <div className="mb-2 rounded border border-terminal-border bg-terminal-bg px-3 py-2.5">
            <p className="truncate font-mono text-[10px] text-terminal-text">
              {user?.fullName || "StockWise User"}
            </p>
            <p className="mt-0.5 truncate font-mono text-[9px] text-terminal-muted">
              {user?.email || "Authenticated session"}
            </p>
          </div>
          <button
            type="button"
            onClick={logout}
            className="flex w-full items-center gap-3 rounded border border-transparent px-3 py-2 font-mono text-[10px] uppercase tracking-wider text-terminal-muted transition-colors hover:border-terminal-red/20 hover:bg-terminal-red/5 hover:text-terminal-red"
          >
            <LogOut className="h-3.5 w-3.5" />
            End session
          </button>
        </div>
      </aside>

      <main className="min-h-screen md:pl-64">
        <div className="min-h-screen p-4 sm:p-6 lg:p-8">
          <DashboardMarketDataBridge>{children}</DashboardMarketDataBridge>
        </div>
      </main>
    </div>
  );
}

/**
 * Wraps the dashboard children with a MarketDataProvider that
 * auto-subscribes to the user's tracked symbols. The wrapper itself
 * fetches the symbol list and re-fetches when the tab regains focus
 * (so admin additions in another tab show up without a hard reload).
 */
function DashboardMarketDataBridge({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [symbols, setSymbols] = useState<string[]>([]);
  const lastFetchRef = useRef(0);

  useEffect(() => {
    if (!isAuthenticated) return;
    let cancelled = false;
    async function refresh() {
      try {
        const data = await trackedSymbolsApi.list();
        if (cancelled) return;
        setSymbols(data);
        lastFetchRef.current = Date.now();
      } catch {
        // ignore
      }
    }
    void refresh();
    const interval = setInterval(refresh, 15_000);
    const onFocus = () => {
      if (Date.now() - lastFetchRef.current > 1_500) void refresh();
    };
    window.addEventListener("focus", onFocus);
    return () => {
      cancelled = true;
      clearInterval(interval);
      window.removeEventListener("focus", onFocus);
    };
  }, [isAuthenticated]);

  return <MarketDataProvider symbols={symbols}>{children}</MarketDataProvider>;
}
