"use client";

import { useEffect, useMemo, useState } from "react";
import { OHLCChart } from "@/components/charts/OHLCChart";
import { marketApi } from "@/lib/api";
import { useLivePrice } from "@/hooks/useMarketWebSocket";
import type { LatestPrice, OhlcSeries, FinancialRatioList } from "@/lib/types";

const DEFAULT_SYMBOL = "FPT";

const currencyFormatter = new Intl.NumberFormat("vi-VN", {
  style: "currency",
  currency: "VND",
  maximumFractionDigits: 0,
});

const numberFormatter = new Intl.NumberFormat("vi-VN", {
  maximumFractionDigits: 2,
});

export default function DashboardPage() {
  const [latestPrice, setLatestPrice] = useState<LatestPrice | null>(null);
  const [ohlcSeries, setOhlcSeries] = useState<OhlcSeries | null>(null);
  const [ratios, setRatios] = useState<FinancialRatioList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Live price via WebSocket
  const [livePrice, setLivePrice] = useState<LatestPrice | null>(null);

  const handleLivePrice = (price: LatestPrice) => {
    setLivePrice(price);
  };

  const { isConnected: wsConnected } = useLivePrice(
    loading ? null : DEFAULT_SYMBOL,
    handleLivePrice
  );

  // Derive the display price: live if available, fallback to initial REST price
  const displayPrice = livePrice ?? latestPrice;

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      try {
        setLoading(true);
        setError(null);

        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - 30);

        const [latest, ohlc, ratioList] = await Promise.all([
          marketApi.getLatestPrice(DEFAULT_SYMBOL),
          marketApi.getOhlc(DEFAULT_SYMBOL, {
            startDate: startDate.toISOString().slice(0, 10),
            endDate: endDate.toISOString().slice(0, 10),
          }),
          marketApi.getRatios(DEFAULT_SYMBOL),
        ]);

        if (cancelled) return;

        setLatestPrice(latest);
        setOhlcSeries(ohlc);
        setRatios(ratioList);
      } catch (err) {
        if (cancelled) return;
        setError("Không thể tải dữ liệu thị trường lúc này.");
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadDashboard();

    return () => {
      cancelled = true;
    };
  }, []);

  const latestRatio = useMemo(() => ratios?.ratios?.[0] ?? null, [ratios]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="mb-2 text-3xl font-bold">Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            Theo dõi nhanh dữ liệu thị trường cho mã {DEFAULT_SYMBOL}.
          </p>
        </div>
        {wsConnected && (
          <div className="flex items-center gap-2 rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500" />
            </span>
            Live
          </div>
        )}
      </div>

      {error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg border bg-card p-4 shadow-sm">
          <h2 className="text-sm font-medium text-muted-foreground">Latest Price</h2>
          <p className="mt-2 text-2xl font-bold">
            {loading ? "Loading..." : displayPrice ? currencyFormatter.format(displayPrice.price) : "—"}
          </p>
          <p
            className={`mt-1 text-sm ${
              displayPrice && displayPrice.change < 0 ? "text-red-600" : "text-green-600"
            }`}
          >
            {displayPrice
              ? `${displayPrice.change >= 0 ? "+" : ""}${numberFormatter.format(displayPrice.change)} (${displayPrice.changePercent >= 0 ? "+" : ""}${numberFormatter.format(displayPrice.changePercent)}%)`
              : "—"}
          </p>
        </div>

        <div className="rounded-lg border bg-card p-4 shadow-sm">
          <h2 className="text-sm font-medium text-muted-foreground">Trading Date</h2>
          <p className="mt-2 text-2xl font-bold">
            {loading ? "Loading..." : latestPrice?.tradeDate ?? "—"}
          </p>
        </div>

        <div className="rounded-lg border bg-card p-4 shadow-sm">
          <h2 className="text-sm font-medium text-muted-foreground">P/E Ratio</h2>
          <p className="mt-2 text-2xl font-bold">
            {loading ? "Loading..." : latestRatio?.peRatio != null ? numberFormatter.format(latestRatio.peRatio) : "—"}
          </p>
        </div>

        <div className="rounded-lg border bg-card p-4 shadow-sm">
          <h2 className="text-sm font-medium text-muted-foreground">ROE</h2>
          <p className="mt-2 text-2xl font-bold">
            {loading ? "Loading..." : latestRatio?.roe != null ? `${numberFormatter.format(latestRatio.roe * 100)}%` : "—"}
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <OHLCChart symbol={DEFAULT_SYMBOL} data={ohlcSeries?.data ?? []} />

        <div className="rounded-lg border bg-card p-4 shadow-sm">
          <h3 className="mb-4 text-lg font-semibold">Market Snapshot</h3>
          <div className="space-y-3 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Open</span>
              <span className="font-medium">
                {latestPrice ? currencyFormatter.format(latestPrice.open) : "—"}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">High</span>
              <span className="font-medium">
                {latestPrice ? currencyFormatter.format(latestPrice.high) : "—"}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Low</span>
              <span className="font-medium">
                {latestPrice ? currencyFormatter.format(latestPrice.low) : "—"}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Volume</span>
              <span className="font-medium">
                {latestPrice ? new Intl.NumberFormat("vi-VN").format(latestPrice.volume) : "—"}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">P/B</span>
              <span className="font-medium">
                {latestRatio?.pbRatio != null ? numberFormatter.format(latestRatio.pbRatio) : "—"}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">EPS</span>
              <span className="font-medium">
                {latestRatio?.eps != null ? numberFormatter.format(latestRatio.eps) : "—"}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
