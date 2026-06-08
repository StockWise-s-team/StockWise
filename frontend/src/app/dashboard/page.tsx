"use client";

import { useAuth } from "@/components/providers/AuthProvider";
import { usePortfolio } from "@/hooks/usePortfolio";
import { formatVnd, formatPnl, pnlColor } from "@/lib/format";

export default function DashboardPage() {
  const { user } = useAuth();
  const { data, error } = usePortfolio(user?.id);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-body">Dashboard</h1>

      {error && (
        <div className="rounded-lg border border-trading-down/30 bg-trading-down/10 px-4 py-3 text-sm text-trading-down">
          {error}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Stat label="Tổng giá trị danh mục" value={formatVnd(data?.totalValue)} />
        <Stat label="Tiền ảo" value={formatVnd(data?.account.virtualCash)} />
        <Stat
          label="Lãi/lỗ chưa thực hiện"
          value={formatPnl(data?.unrealizedPnl)}
          valueClass={pnlColor(data?.unrealizedPnl)}
        />
        <Stat
          label="Lãi/lỗ đã thực hiện"
          value={formatPnl(data?.realizedPnl)}
          valueClass={pnlColor(data?.realizedPnl)}
        />
      </div>
    </div>
  );
}

function Stat({
  label,
  value,
  valueClass = "text-body",
}: {
  label: string;
  value: string;
  valueClass?: string;
}) {
  return (
    <div className="rounded-lg border border-hairline-on-dark bg-surface-card-dark p-4">
      <h2 className="text-sm font-medium text-muted-strong">{label}</h2>
      <p className={`mt-2 text-2xl font-bold ${valueClass}`}>{value}</p>
    </div>
  );
}
