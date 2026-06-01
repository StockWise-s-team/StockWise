"use client";

import Link from "next/link";
import {
  LayoutDashboard,
  Briefcase,
  FlaskConical,
  Bot,
  LogOut,
  User,
} from "lucide-react";
import { useAuth } from "@/components/providers/AuthProvider";

const navItems = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/portfolio", label: "Portfolio", icon: Briefcase },
  { href: "/dashboard/sandbox", label: "Sandbox", icon: FlaskConical },
  { href: "/dashboard/advisor", label: "AI Advisor", icon: Bot },
  { href: "/dashboard/profile", label: "Profile", icon: User },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };
  return (
    <div className="flex min-h-screen">
      <aside className="flex w-64 flex-col border-r bg-card p-4">
        <div className="mb-8 text-xl font-bold">StockWise</div>
        <nav className="flex flex-1 flex-col gap-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          ))}
        </nav>
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground cursor-pointer"
        >
          <LogOut className="h-4 w-4" />
          Logout
        </button>
      </aside>
      <main className="flex-1 overflow-auto p-6">{children}</main>
    </div>
  );
}
