"use client";

import { Briefcase, Clock, History, RefreshCw, Wallet } from "lucide-react";
import { useAuth } from "@/components/providers/AuthProvider";
import { usePortfolio } from "@/hooks/usePortfolio";
import { formatVnd, formatPnl, formatQty, formatDateTime, pnlColor } from "@/lib/format";
import {
  TerminalButton,
  TerminalEmptyState,
  TerminalMetricCard,
  TerminalNotice,
  TerminalSectionHeader,
  TerminalSkeletonRows,
  TerminalTable,
} from "@/components/ui";

export default function PortfolioPage() {
  const { user } = useAuth();
  const { data, loading, error, reload } = usePortfolio(user?.id);

  return (
    <div className="min-h-full space-y-5 font-mono text-terminal-text">
      <header className="flex flex-col gap-3 border-b border-terminal-border pb-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-terminal-muted">
            <Wallet className="h-3.5 w-3.5 text-terminal-accent" />
            Portfolio console
          </div>
          <h1 className="font-display text-xl font-bold uppercase tracking-[0.18em] text-terminal-accent">
            Portfolio
          </h1>
          <p className="mt-1 max-w-2xl text-xs leading-relaxed text-terminal-muted">
            Holdings, account value, and executed paper-trading history.
          </p>
        </div>
        <TerminalButton onClick={() => reload()} disabled={loading} tone="muted">
          <RefreshCw className={`h-3 w-3 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </TerminalButton>
      </header>

      {error && <TerminalNotice tone="danger">{error}</TerminalNotice>}

      <section>
        <TerminalSectionHeader
          icon={Briefcase}
          title="Account summary"
          subtitle="Cash and profit/loss telemetry"
        />
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <TerminalMetricCard label="Total value" value={formatVnd(data?.totalValue)} />
          <TerminalMetricCard label="Available virtual cash" value={formatVnd(data?.account.virtualCash)} />
          <TerminalMetricCard
            label="Unrealized P/L"
            value={<span className={pnlColor(data?.unrealizedPnl)}>{formatPnl(data?.unrealizedPnl)}</span>}
          />
          <TerminalMetricCard
            label="Realized P/L"
            value={<span className={pnlColor(data?.realizedPnl)}>{formatPnl(data?.realizedPnl)}</span>}
          />
        </div>
      </section>

      {data?.hasMissingPrices && (
        <TerminalNotice tone="warning">
          Some symbols do not have current market prices, so their value and P/L use cost basis fallback.
        </TerminalNotice>
      )}

      <section>
        <TerminalSectionHeader
          icon={Briefcase}
          title="Holdings"
          subtitle={data ? `${data.holdings.length} open positions` : "Loading positions"}
        />
        {loading && !data ? (
          <TerminalSkeletonRows rows={4} />
        ) : data && data.holdings.length === 0 ? (
          <TerminalEmptyState
            icon={Briefcase}
            title="No holdings yet"
            description="Matched buy orders from Sandbox will appear here."
          />
        ) : (
          <TerminalTable
            headers={[
              { label: "Symbol" },
              { label: "Quantity", align: "right" },
              { label: "Avg cost", align: "right" },
              { label: "Current", align: "right" },
              { label: "Market value", align: "right" },
              { label: "Unrealized P/L", align: "right" },
            ]}
          >
            {data?.holdings.map((holding) => (
              <tr
                key={holding.symbol}
                className="border-b border-terminal-border/60 transition-colors hover:bg-terminal-bg"
              >
                <td className="px-3 py-2.5 font-semibold text-terminal-accent">{holding.symbol}</td>
                <td className="px-3 py-2.5 text-right text-terminal-text">{formatQty(holding.quantity)}</td>
                <td className="px-3 py-2.5 text-right text-terminal-text">{formatVnd(holding.avgPrice)}</td>
                <td className="px-3 py-2.5 text-right text-terminal-text">{formatVnd(holding.currentPrice)}</td>
                <td className="px-3 py-2.5 text-right text-terminal-text">{formatVnd(holding.marketValue)}</td>
                <td className={`px-3 py-2.5 text-right font-semibold ${pnlColor(holding.unrealizedPnl)}`}>
                  {formatPnl(holding.unrealizedPnl)}
                </td>
              </tr>
            ))}
          </TerminalTable>
        )}
      </section>

      <section>
        <TerminalSectionHeader
          icon={History}
          title="Transaction history"
          subtitle={data ? `${data.transactions.length} executed orders` : "Loading orders"}
        />
        {loading && !data ? (
          <TerminalSkeletonRows rows={4} />
        ) : data && data.transactions.length === 0 ? (
          <TerminalEmptyState
            icon={Clock}
            title="No executed transactions"
            description="Filled orders will be listed here."
          />
        ) : (
          <TerminalTable
            headers={[
              { label: "Time" },
              { label: "Symbol" },
              { label: "Side" },
              { label: "Quantity", align: "right" },
              { label: "Fill price", align: "right" },
              { label: "Value", align: "right" },
            ]}
          >
            {data?.transactions.map((transaction) => (
              <tr
                key={transaction.id}
                className="border-b border-terminal-border/60 transition-colors hover:bg-terminal-bg"
              >
                <td className="px-3 py-2.5 text-terminal-muted">{formatDateTime(transaction.executedAt)}</td>
                <td className="px-3 py-2.5 font-semibold text-terminal-accent">{transaction.symbol}</td>
                <td className="px-3 py-2.5">
                  <span
                    className={
                      transaction.type === "BUY"
                        ? "text-terminal-green"
                        : "text-terminal-red"
                    }
                  >
                    {transaction.type}
                  </span>
                </td>
                <td className="px-3 py-2.5 text-right text-terminal-text">{formatQty(transaction.quantity)}</td>
                <td className="px-3 py-2.5 text-right text-terminal-text">{formatVnd(transaction.price)}</td>
                <td className="px-3 py-2.5 text-right text-terminal-text">
                  {formatVnd(transaction.price * transaction.quantity)}
                </td>
              </tr>
            ))}
          </TerminalTable>
        )}
      </section>
    </div>
  );
}
