"use client";

import { useAuth } from "@/components/providers/AuthProvider";
import { usePortfolio } from "@/hooks/usePortfolio";
import { formatVnd, formatPnl, formatQty, formatDateTime, pnlColor } from "@/lib/format";
import { RefreshCw } from "lucide-react";

export default function PortfolioPage() {
  const { user } = useAuth();
  const { data, loading, error, reload } = usePortfolio(user?.id);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-body">Portfolio</h1>
        <button
          onClick={() => reload()}
          disabled={loading}
          className="flex items-center gap-2 rounded-md border border-hairline-on-dark px-3 py-2 text-sm font-medium text-muted-strong transition-colors hover:text-primary disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Làm mới
        </button>
      </div>

      {error && (
        <div className="rounded-lg border border-trading-down/30 bg-trading-down/10 px-4 py-3 text-sm text-trading-down">
          {error}
        </div>
      )}

      {/* Summary cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <SummaryCard label="Tổng giá trị" value={formatVnd(data?.totalValue)} />
        <SummaryCard label="Tiền ảo khả dụng" value={formatVnd(data?.account.virtualCash)} />
        <SummaryCard
          label="Lãi/lỗ chưa thực hiện"
          value={formatPnl(data?.unrealizedPnl)}
          valueClass={pnlColor(data?.unrealizedPnl)}
        />
        <SummaryCard
          label="Lãi/lỗ đã thực hiện"
          value={formatPnl(data?.realizedPnl)}
          valueClass={pnlColor(data?.realizedPnl)}
        />
      </div>

      {data?.hasMissingPrices && (
        <p className="text-xs text-muted">
          * Một số mã chưa có giá thị trường — giá trị và lãi/lỗ của các mã đó tạm tính theo giá vốn.
        </p>
      )}

      {/* Holdings */}
      <section className="rounded-lg border border-hairline-on-dark bg-surface-card-dark">
        <header className="border-b border-hairline-on-dark px-4 py-3">
          <h2 className="text-lg font-semibold text-body">Danh mục nắm giữ</h2>
        </header>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-hairline-on-dark text-muted-strong">
                <th className="px-4 py-3 text-left font-medium">Mã</th>
                <th className="px-4 py-3 text-right font-medium">Số lượng</th>
                <th className="px-4 py-3 text-right font-medium">Giá vốn TB</th>
                <th className="px-4 py-3 text-right font-medium">Giá hiện tại</th>
                <th className="px-4 py-3 text-right font-medium">Giá trị thị trường</th>
                <th className="px-4 py-3 text-right font-medium">Lãi/lỗ chưa TH</th>
              </tr>
            </thead>
            <tbody>
              {loading && !data && (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-muted">
                    Đang tải…
                  </td>
                </tr>
              )}
              {data && data.holdings.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-muted">
                    Chưa có cổ phiếu nào. Hãy đặt lệnh mua trong Sandbox.
                  </td>
                </tr>
              )}
              {data?.holdings.map((h) => (
                <tr key={h.symbol} className="border-b border-hairline-on-dark/50">
                  <td className="px-4 py-3 font-medium text-body">{h.symbol}</td>
                  <td className="px-4 py-3 text-right text-body">{formatQty(h.quantity)}</td>
                  <td className="px-4 py-3 text-right text-body">{formatVnd(h.avgPrice)}</td>
                  <td className="px-4 py-3 text-right text-body">{formatVnd(h.currentPrice)}</td>
                  <td className="px-4 py-3 text-right text-body">{formatVnd(h.marketValue)}</td>
                  <td className={`px-4 py-3 text-right font-medium ${pnlColor(h.unrealizedPnl)}`}>
                    {formatPnl(h.unrealizedPnl)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Transaction history */}
      <section className="rounded-lg border border-hairline-on-dark bg-surface-card-dark">
        <header className="border-b border-hairline-on-dark px-4 py-3">
          <h2 className="text-lg font-semibold text-body">Lịch sử giao dịch</h2>
        </header>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-hairline-on-dark text-muted-strong">
                <th className="px-4 py-3 text-left font-medium">Thời gian</th>
                <th className="px-4 py-3 text-left font-medium">Mã</th>
                <th className="px-4 py-3 text-left font-medium">Loại</th>
                <th className="px-4 py-3 text-right font-medium">Số lượng</th>
                <th className="px-4 py-3 text-right font-medium">Giá khớp</th>
                <th className="px-4 py-3 text-right font-medium">Giá trị</th>
              </tr>
            </thead>
            <tbody>
              {data && data.transactions.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-muted">
                    Chưa có giao dịch nào được khớp.
                  </td>
                </tr>
              )}
              {data?.transactions.map((t) => (
                <tr key={t.id} className="border-b border-hairline-on-dark/50">
                  <td className="px-4 py-3 text-muted-strong">{formatDateTime(t.executedAt)}</td>
                  <td className="px-4 py-3 font-medium text-body">{t.symbol}</td>
                  <td className="px-4 py-3">
                    <span
                      className={
                        t.type === "BUY" ? "text-trading-up" : "text-trading-down"
                      }
                    >
                      {t.type === "BUY" ? "Mua" : "Bán"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right text-body">{formatQty(t.quantity)}</td>
                  <td className="px-4 py-3 text-right text-body">{formatVnd(t.price)}</td>
                  <td className="px-4 py-3 text-right text-body">
                    {formatVnd(t.price * t.quantity)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function SummaryCard({
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
      <p className="text-sm text-muted-strong">{label}</p>
      <p className={`mt-2 text-xl font-bold ${valueClass}`}>{value}</p>
    </div>
  );
}
