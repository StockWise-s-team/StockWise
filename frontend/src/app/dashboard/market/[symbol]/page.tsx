"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Activity,
  ArrowLeft,
  BookOpen,
  FlaskConical,
  Gauge,
  Info,
  TrendingDown,
} from "lucide-react";
import { marketApi, wikiApi } from "@/lib/api";
import { formatVnd } from "@/lib/format";
import type { LatestPrice, OhlcSeries, WikiData, FinancialRatioList } from "@/lib/types";
import {
  TerminalMetricCard,
  TerminalNotice,
  TerminalSectionHeader,
  TerminalSkeletonRows,
  TerminalButton,
  TerminalEmptyState,
} from "@/components/ui";
import { OHLCChart } from "@/components/charts/OHLCChart";

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

  useEffect(() => {
    if (!symbol) return;
    let cancelled = false;

    async function loadData() {
      try {
        setLoading(true);
        setError(null);

        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - 30);

        const [priceData, ohlcData, wikiData, ratioData] = await Promise.all([
          marketApi.getLatestPrice(symbol).catch(() => null),
          marketApi.getOhlc(symbol, {
            startDate: startDate.toISOString().slice(0, 10),
            endDate: endDate.toISOString().slice(0, 10),
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

  if (loading) {
    return (
      <div className="space-y-6 font-mono text-terminal-text">
        <div className="h-6 w-32 animate-pulse bg-terminal-surface rounded" />
        <div className="h-12 w-96 animate-pulse bg-terminal-surface rounded" />
        <TerminalSkeletonRows rows={6} />
      </div>
    );
  }

  const latestRatio = ratios?.ratios?.[0] ?? null;
  const priceTone =
    latestPrice && latestPrice.change < 0
      ? "danger"
      : latestPrice
      ? "success"
      : "default";

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
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <TerminalMetricCard
          label={`${symbol} Latest Price`}
          value={latestPrice ? formatVnd(latestPrice.price) : "-"}
          tone={priceTone}
          helper={
            latestPrice
              ? `${latestPrice.change >= 0 ? "+" : ""}${numberFormatter.format(
                  latestPrice.change
                )} (${latestPrice.changePercent >= 0 ? "+" : ""}${numberFormatter.format(
                  latestPrice.changePercent
                )}%)`
              : undefined
          }
        />
        <TerminalMetricCard
          label="P/E Ratio"
          value={latestRatio?.peRatio != null ? numberFormatter.format(latestRatio.peRatio) : "-"}
        />
        <TerminalMetricCard
          label="ROE"
          value={latestRatio?.roe != null ? `${numberFormatter.format(latestRatio.roe * 100)}%` : "-"}
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

      {/* Main Content Layout */}
      <div className="grid gap-6 xl:grid-cols-12">
        {/* Left Column: Chart & News */}
        <div className="space-y-6 xl:col-span-8">
          {/* Chart */}
          <div className="rounded border border-terminal-border bg-terminal-surface p-4">
            {ohlcSeries && ohlcSeries.data && ohlcSeries.data.length > 0 ? (
              <OHLCChart symbol={symbol} data={ohlcSeries.data} />
            ) : (
              <TerminalEmptyState icon={Activity} title="No historical price data" />
            )}
          </div>

          {/* Business Summary */}
          <section className="rounded border border-terminal-border bg-terminal-surface p-4 space-y-3">
            <TerminalSectionHeader
              icon={BookOpen}
              title="Business Overview"
              subtitle="LLM-Synthesized Knowledge Base"
            />
            <p className="text-xs leading-relaxed text-terminal-text whitespace-pre-line">
              {wiki?.businessSummary || "No business summary generated for this ticker."}
            </p>
          </section>

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
              <SnapshotRow label="Open" value={latestPrice ? formatVnd(latestPrice.open) : "-"} />
              <SnapshotRow label="High" value={latestPrice ? formatVnd(latestPrice.high) : "-"} />
              <SnapshotRow label="Low" value={latestPrice ? formatVnd(latestPrice.low) : "-"} />
              <SnapshotRow label="Close" value={latestPrice ? formatVnd(latestPrice.close) : "-"} />
              <SnapshotRow
                label="Volume"
                value={latestPrice ? new Intl.NumberFormat("vi-VN").format(latestPrice.volume) : "-"}
              />
              <SnapshotRow
                label="P/B"
                value={latestRatio?.pbRatio != null ? numberFormatter.format(latestRatio.pbRatio) : "-"}
              />
              <SnapshotRow
                label="EPS"
                value={latestRatio?.eps != null ? numberFormatter.format(latestRatio.eps) : "-"}
              />
            </div>
          </section>

          {/* Risk Factors */}
          <section className="rounded border border-terminal-border bg-terminal-surface p-4 space-y-3">
            <TerminalSectionHeader
              icon={TrendingDown}
              title="Risk & Performance Analysis"
              subtitle="Highlighted risk parameters"
            />

            {wiki?.keyRisks && wiki.keyRisks.length > 0 ? (
              <ul className="space-y-2">
                {wiki.keyRisks.map((risk, index) => (
                  <li
                    key={index}
                    className="flex items-start gap-2 rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-xs"
                  >
                    <span className="text-terminal-red font-bold font-mono">!</span>
                    <span className="text-terminal-text">{risk}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-terminal-muted">No specific risk highlights logged.</p>
            )}

            {wiki?.recentPerformance && (
              <div className="mt-4 rounded border border-terminal-border bg-terminal-bg p-3 text-xs space-y-1">
                <div className="font-semibold text-terminal-accent uppercase tracking-wider text-[10px]">
                  Recent Trend
                </div>
                <div className="text-terminal-text capitalize">
                  {typeof wiki.recentPerformance === "string"
                    ? wiki.recentPerformance
                    : wiki.recentPerformance.trend}
                </div>
                {typeof wiki.recentPerformance !== "string" && wiki.recentPerformance.notable && (
                  <>
                    <div className="font-semibold text-terminal-accent uppercase tracking-wider text-[10px] mt-2">
                      Key Event
                    </div>
                    <div className="text-terminal-muted">{wiki.recentPerformance.notable}</div>
                  </>
                )}
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
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
