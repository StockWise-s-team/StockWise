"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Activity,
  ArrowLeft,
  FlaskConical,
  Gauge,
  Info,
} from "lucide-react";
import { clsx } from "clsx";
import { marketApi, wikiApi } from "@/lib/api";
import { extractErrorMessage } from "@/lib/apiError";
import { formatPercent, formatVnd, toVndYmd } from "@/lib/format";
import { useMarketTicker } from "@/components/providers/MarketDataProvider";
import type {
  IntradayOhlcBar,
  IntradayOhlcSeries,
  LatestPrice,
  OhlcSeries,
  WikiData,
  FinancialRatioList,
} from "@/lib/types";
import {
  TerminalMetricCard,
  TerminalNotice,
  TerminalSectionHeader,
  TerminalSkeletonRows,
  TerminalButton,
  TerminalEmptyState,
} from "@/components/ui";
import { OHLCChart } from "@/components/charts/OHLCChart";
import { IntradayOhlcChart } from "@/components/charts/IntradayOhlcChart";

type ChartTimeframe = "DAILY" | "INTRADAY";

const numberFormatter = new Intl.NumberFormat("vi-VN", {
  maximumFractionDigits: 2,
});

export default function MarketDetailPage() {
  const params = useParams();
  const symbol = (params.symbol as string)?.toUpperCase() || "";

  const [latestPrice, setLatestPrice] = useState<LatestPrice | null>(null);
  const [ohlcSeries, setOhlcSeries] = useState<OhlcSeries | null>(null);
  const [wiki, setWiki] = useState<WikiData | null>(null);
  const [ratios, setRatios] = useState<FinancialRatioList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [timeframe, setTimeframe] = useState<ChartTimeframe>("DAILY");
  const [intradaySeries, setIntradaySeries] = useState<IntradayOhlcSeries | null>(null);
  const [intradayLoading, setIntradayLoading] = useState(false);
  const [intradayError, setIntradayError] = useState<string | null>(null);

  const { ticker } = useMarketTicker(symbol);
  const livePrice = useMemo<LatestPrice | null>(() => {
    if (!ticker) return null;
    return ticker as LatestPrice;
  }, [ticker]);

  useEffect(() => {
    if (!symbol) return;
    let cancelled = false;

    async function loadData() {
      try {
        setLoading(true);
        setError(null);

        const endDate = toVndYmd();
        const start = new Date();
        start.setDate(start.getDate() - 30);
        const startDate = toVndYmd(start);

        const [priceData, ohlcData, wikiData, ratioData] = await Promise.all([
          marketApi.getLatestPrice(symbol).catch(() => null),
          marketApi.getOhlc(symbol, {
            startDate,
            endDate,
          }).catch(() => null),
          wikiApi.get(symbol).catch(() => null),
          marketApi.getRatios(symbol).catch(() => null),
        ]);

        if (cancelled) return;

        setLatestPrice(priceData);
        setOhlcSeries(ohlcData);
        setWiki(wikiData);
        setRatios(ratioData);
      } catch (err) {
        if (!cancelled) {
          setError("Failed to fetch market data. Please make sure data has been seeded.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadData();

    return () => {
      cancelled = true;
    };
  }, [symbol]);

  const loadIntraday = useCallback(async () => {
    if (!symbol) return;
    setIntradayLoading(true);
    setIntradayError(null);
    try {
      const data = await marketApi.getIntradayOhlc(symbol, "5m");
      setIntradaySeries(data);
    } catch (err) {
      setIntradayError(extractErrorMessage(err, "Failed to load intraday bars."));
    } finally {
      setIntradayLoading(false);
    }
  }, [symbol]);

  useEffect(() => {
    if (timeframe === "INTRADAY" && !intradaySeries && !intradayLoading) {
      void loadIntraday();
    }
  }, [timeframe, intradaySeries, intradayLoading, loadIntraday]);

  if (loading) {
    return (
      <div className="space-y-6 font-mono text-terminal-text">
        <div className="h-6 w-32 animate-pulse bg-terminal-surface rounded" />
        <div className="h-12 w-96 animate-pulse bg-terminal-surface rounded" />
        <TerminalSkeletonRows rows={6} />
      </div>
    );
  }

  const priceTone =
    livePrice && livePrice.change < 0
      ? "danger"
      : livePrice
      ? "success"
      : latestPrice && latestPrice.change < 0
      ? "danger"
      : latestPrice
      ? "success"
      : "default";
  const displayedPrice = livePrice ?? latestPrice;

  return (
    <div className="min-h-full space-y-6 font-mono text-terminal-text">
      {/* Header */}
      <header className="border-b border-terminal-border pb-4">
        <div className="mb-4">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1.5 text-xs text-terminal-muted hover:text-terminal-accent transition-colors"
          >
            <ArrowLeft className="h-3 w-3" /> Back to Dashboard
          </Link>
        </div>

        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="mb-1 flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-terminal-muted">
              <span className="h-1.5 w-1.5 rounded-full bg-terminal-accent animate-pulse" />
              Stock Analysis Console
            </div>
            <h1 className="font-display text-2xl font-bold uppercase tracking-[0.18em] text-terminal-accent">
              {symbol}
            </h1>
            <p className="mt-1 text-xs text-terminal-muted">
              {wiki?.companyName || "Company Information Unavailable"} &bull; {wiki?.sector || "Sector Unknown"}
            </p>
          </div>

          <div className="flex gap-2">
            <Link href={`/dashboard/sandbox?symbol=${symbol}`}>
              <TerminalButton tone="accent" className="h-10 px-4">
                <FlaskConical className="h-3.5 w-3.5" />
                Trade in Sandbox
              </TerminalButton>
            </Link>
          </div>
        </div>
      </header>

      {error && <TerminalNotice tone="danger">{error}</TerminalNotice>}

      {/* Metrics Row */}
      <section className="grid gap-3 sm:grid-cols-2">
        <TerminalMetricCard
          label={`${symbol} Latest Price`}
          value={displayedPrice ? formatVnd(displayedPrice.price) : "-"}
          tone={priceTone}
          helper={
            displayedPrice
              ? `${displayedPrice.change >= 0 ? "+" : ""}${numberFormatter.format(
                  displayedPrice.change
                )} (${displayedPrice.changePercent >= 0 ? "+" : ""}${numberFormatter.format(
                  displayedPrice.changePercent
                )}%)`
              : undefined
          }
        />
        <TerminalMetricCard
          label="Sentiment Index"
          value={wiki?.sentiment || "NEUTRAL"}
          tone={
            wiki?.sentiment === "POSITIVE"
              ? "success"
              : wiki?.sentiment === "NEGATIVE"
              ? "danger"
              : "warning"
          }
        />
      </section>

      {/* Financial Ratios Tables (TTM / Annual) */}
      {(ratios?.ratios?.length ?? 0) > 0 && (
        <section className="grid gap-3 sm:grid-cols-2">
          {(["ttm", "annual"] as const).map((periodKey) => {
            const item = ratios!.ratios.find(
              (r) => r.period?.toLowerCase() === periodKey
            );
            if (!item) return null;
            return (
              <FinancialRatioTable
                key={periodKey}
                symbol={symbol}
                period={periodKey}
                item={item}
              />
            );
          })}
        </section>
      )}

      {/* Main Content Layout */}
      <div className="grid gap-6 xl:grid-cols-12">
        {/* Left Column: Chart & News */}
        <div className="space-y-6 xl:col-span-8">
          {/* Chart */}
          <div className="rounded border border-terminal-border bg-terminal-surface p-4">
            <div className="mb-3 flex items-center justify-end gap-1.5">
              <TimeframeToggle value={timeframe} onChange={setTimeframe} />
            </div>
            {timeframe === "DAILY" ? (
              ohlcSeries && ohlcSeries.data && ohlcSeries.data.length > 0 ? (
                <OHLCChart symbol={symbol} data={ohlcSeries.data} />
              ) : (
                <TerminalEmptyState icon={Activity} title="No historical price data" />
              )
            ) : (
              <IntradayChartPanel
                symbol={symbol}
                series={intradaySeries}
                loading={intradayLoading}
                error={intradayError}
                onRetry={loadIntraday}
              />
            )}
          </div>

          {/* News Analysis */}
          {wiki?.lastNewsSummary && (
            <section className="rounded border border-terminal-border bg-terminal-surface p-4 space-y-3">
              <TerminalSectionHeader
                icon={Info}
                title="Recent News Synthesis"
                subtitle="Aggregated news and media consensus"
              />
              <p className="text-xs leading-relaxed text-terminal-muted whitespace-pre-line">
                {wiki.lastNewsSummary}
              </p>
            </section>
          )}
        </div>

        {/* Right Column: Key Details & Risks */}
        <div className="space-y-6 xl:col-span-4">
          {/* Session Details Snapshot */}
          <section className="rounded border border-terminal-border bg-terminal-surface p-4">
            <TerminalSectionHeader
              icon={Gauge}
              title="Session Snapshot"
              subtitle="Latest exchange quotes"
            />
            <div className="space-y-1">
              <SnapshotRow label="Open" value={displayedPrice ? formatVnd(displayedPrice.open) : "-"} />
              <SnapshotRow label="High" value={displayedPrice ? formatVnd(displayedPrice.high) : "-"} />
              <SnapshotRow label="Low" value={displayedPrice ? formatVnd(displayedPrice.low) : "-"} />
              <SnapshotRow label="Close" value={displayedPrice ? formatVnd(displayedPrice.close) : "-"} />
              <SnapshotRow
                label="Volume"
                value={displayedPrice ? new Intl.NumberFormat("vi-VN").format(displayedPrice.volume) : "-"}
              />
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

function TimeframeToggle({ value, onChange }: { value: ChartTimeframe; onChange: (v: ChartTimeframe) => void }) {
  return (
    <div className="inline-flex rounded border border-terminal-border bg-terminal-bg p-0.5">
      <ToggleButton active={value === "DAILY"} onClick={() => onChange("DAILY")}>
        Daily 30D
      </ToggleButton>
      <ToggleButton active={value === "INTRADAY"} onClick={() => onChange("INTRADAY")}>
        Intraday 5m
      </ToggleButton>
    </div>
  );
}

function ToggleButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={clsx(
        "rounded px-3 py-1 text-[10px] font-mono font-semibold uppercase tracking-wider transition-colors",
        active
          ? "bg-terminal-accent/15 text-terminal-accent"
          : "text-terminal-muted hover:text-terminal-text"
      )}
    >
      {children}
    </button>
  );
}

function IntradayChartPanel({
  symbol,
  series,
  loading,
  error,
  onRetry,
}: {
  symbol: string;
  series: IntradayOhlcSeries | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}) {
  const bars: IntradayOhlcBar[] = series?.data ?? [];
  if (error) {
    return (
      <div className="space-y-2">
        <TerminalNotice tone="danger">{error}</TerminalNotice>
        <div className="text-right">
          <TerminalButton size="xs" tone="muted" onClick={onRetry}>
            Retry
          </TerminalButton>
        </div>
      </div>
    );
  }
  return (
    <IntradayOhlcChart
      symbol={symbol}
      bars={bars}
      interval={series?.interval ?? "5m"}
      loading={loading}
    />
  );
}

function SnapshotRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 rounded border border-terminal-border bg-terminal-bg px-3 py-2">
      <span className="text-[10px] uppercase tracking-wider text-terminal-muted">{label}</span>
      <span className="text-right text-xs font-semibold text-terminal-text">{value}</span>
    </div>
  );
}

const periodLabel: Record<"ttm" | "annual", string> = {
  ttm: "TTM (12 tháng cuốn chiếu)",
  annual: "Annual (cả năm tài chính)",
};

function FinancialRatioTable({
  symbol,
  period,
  item,
}: {
  symbol: string;
  period: "ttm" | "annual";
  item: FinancialRatioList["ratios"][number];
}) {
  const rows: Array<{ metric: string; value: string }> = [
    {
      metric: "P/E",
      value: item.peRatio != null ? numberFormatter.format(item.peRatio) : "—",
    },
    {
      metric: "P/B",
      value: item.pbRatio != null ? numberFormatter.format(item.pbRatio) : "—",
    },
    {
      metric: "EPS",
      value: item.eps != null ? numberFormatter.format(item.eps) : "—",
    },
    {
      metric: "ROE",
      value: formatPercent(item.roe),
    },
    {
      metric: "ROA",
      value: formatPercent(item.roa),
    },
  ];
  return (
    <section className="rounded border border-terminal-border bg-terminal-surface p-4 space-y-3">
      <TerminalSectionHeader
        icon={Gauge}
        title={`Financial Ratios — ${symbol} (${period.toUpperCase()})`}
        subtitle={periodLabel[period]}
      />
      <div className="rounded border border-terminal-border bg-terminal-bg">
        <table className="w-full font-mono text-xs">
          <thead>
            <tr className="border-b border-terminal-border text-[10px] uppercase tracking-wider text-terminal-muted">
              <th className="px-3 py-2 text-left font-medium">Metric</th>
              <th className="px-3 py-2 text-right font-medium">Value</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr
                key={row.metric}
                className="border-b border-terminal-border/50 last:border-b-0"
              >
                <td className="px-3 py-2 text-[10px] uppercase tracking-wider text-terminal-muted">
                  {row.metric}
                </td>
                <td className="px-3 py-2 text-right text-xs font-semibold text-terminal-text">
                  {row.value}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
