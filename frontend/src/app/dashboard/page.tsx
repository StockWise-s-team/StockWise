"use client";

import { useEffect, useMemo, useState } from "react";
import { useAuth } from "@/components/providers/AuthProvider";
import dynamic from "next/dynamic";
const TradingViewChart = dynamic(
  () => import("@/components/charts/TradingViewChart"),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-[350px] items-center justify-center rounded-lg border border-hairline-on-dark bg-surface-card-dark text-muted">
        Đang tải biểu đồ...
      </div>
    ),
  }
);
import { usePortfolio } from "@/hooks/usePortfolio";
import { marketApi, trackedSymbolsApi } from "@/lib/api";
import { useLivePrice } from "@/hooks/useMarketWebSocket";
import { formatVnd, formatPnl, pnlColor } from "@/lib/format";
import type { FinancialRatioList, LatestPrice, OhlcSeries } from "@/lib/types";

const numberFormatter = new Intl.NumberFormat("vi-VN", {
  maximumFractionDigits: 2,
});

export default function DashboardPage() {
  const { user } = useAuth();
  const { data, error: portfolioError } = usePortfolio(user?.id);
  const [symbolsList, setSymbolsList] = useState<string[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string>("FPT");
  const [latestPrice, setLatestPrice] = useState<LatestPrice | null>(null);
  const [ohlcSeries, setOhlcSeries] = useState<OhlcSeries | null>(null);
  const [ratios, setRatios] = useState<FinancialRatioList | null>(null);
  const [marketLoading, setMarketLoading] = useState(true);
  const [marketError, setMarketError] = useState<string | null>(null);

  // Live price via WebSocket
  const [livePrice, setLivePrice] = useState<LatestPrice | null>(null);

  const handleLivePrice = (price: LatestPrice) => {
    setLivePrice(price);

    // Update the OHLC series data dynamically
    setOhlcSeries((prevSeries) => {
      if (!prevSeries || !prevSeries.data || prevSeries.data.length === 0) return prevSeries;

      const updatedData = [...prevSeries.data];
      const lastBar = updatedData[updatedData.length - 1];

      // Match the date format YYYY-MM-DD
      if (lastBar.date === price.tradeDate) {
        updatedData[updatedData.length - 1] = {
          ...lastBar,
          close: price.price, // Using the updated price/close
          high: Math.max(lastBar.high, price.high),
          low: Math.min(lastBar.low, price.low),
          volume: price.volume,
        };
      } else if (new Date(price.tradeDate) > new Date(lastBar.date)) {
        updatedData.push({
          date: price.tradeDate,
          open: price.open,
          high: price.high,
          low: price.low,
          close: price.price,
          volume: price.volume,
        });
      }

      return {
        ...prevSeries,
        data: updatedData,
      };
    });
  };

  // Fetch tracked symbols list on mount
  useEffect(() => {
    trackedSymbolsApi.list()
      .then((syms) => {
        const defaultSymbols = ["FPT", "VNM", "HPG", "VIC", "MSN"];
        const combined = Array.from(new Set([...(syms || []), ...defaultSymbols]));
        setSymbolsList(combined);
        if (syms && syms.length > 0 && !syms.includes("FPT")) {
          setSelectedSymbol(syms[0]);
        }
      })
      .catch((err) => {
        console.error("Failed to load tracked symbols, using defaults:", err);
        setSymbolsList(["FPT", "VNM", "HPG", "VIC", "MSN"]);
      });
  }, []);

  // Reset live price when selected symbol changes
  useEffect(() => {
    setLivePrice(null);
  }, [selectedSymbol]);

  const { isConnected: wsConnected } = useLivePrice(
    user?.id ? selectedSymbol : null,
    handleLivePrice
  );

  // Derive the display price: live if available, fallback to initial REST price
  const displayPrice = livePrice ?? latestPrice;

  useEffect(() => {
    let cancelled = false;

    async function loadMarket() {
      if (!selectedSymbol) return;
      try {
        setMarketLoading(true);
        setMarketError(null);

        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - 30);

        const [latest, ohlc, ratioList] = await Promise.all([
          marketApi.getLatestPrice(selectedSymbol),
          marketApi.getOhlc(selectedSymbol, {
            startDate: startDate.toISOString().slice(0, 10),
            endDate: endDate.toISOString().slice(0, 10),
          }),
          marketApi.getRatios(selectedSymbol),
        ]);

        if (cancelled) return;
        setLatestPrice(latest);
        setOhlcSeries(ohlc);
        setRatios(ratioList);
      } catch {
        if (!cancelled) setMarketError("Khong the tai du lieu thi truong luc nay.");
      } finally {
        if (!cancelled) setMarketLoading(false);
      }
    }

    void loadMarket();

    return () => {
      cancelled = true;
    };
  }, [selectedSymbol]);

  const latestRatio = useMemo(() => {
    const baseRatio = ratios?.ratios?.[0] ?? null;
    if (!baseRatio) return null;

    // Recalculate P/E dynamically if we have a live price and valid EPS
    if (displayPrice && baseRatio.eps && baseRatio.eps > 0) {
      return {
        ...baseRatio,
        peRatio: displayPrice.price / baseRatio.eps,
      };
    }
    return baseRatio;
  }, [ratios, displayPrice]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="mb-2 text-3xl font-bold">Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            Theo dõi nhanh dữ liệu thị trường cho mã {selectedSymbol}.
          </p>
        </div>
        <div className="flex items-center gap-4">
          {symbolsList.length > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-muted-strong">Mã chứng khoán:</span>
              <select
                value={selectedSymbol}
                onChange={(e) => setSelectedSymbol(e.target.value)}
                className="rounded-md border border-hairline-on-dark bg-surface-card-dark px-3 py-1.5 text-sm font-semibold text-body focus:outline-none focus:ring-1 focus:ring-primary"
              >
                {symbolsList.map((sym) => (
                  <option key={sym} value={sym}>
                    {sym}
                  </option>
                ))}
              </select>
            </div>
          )}
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
      </div>

      {(portfolioError || marketError) && (
        <div className="rounded-lg border border-trading-down/30 bg-trading-down/10 px-4 py-3 text-sm text-trading-down">
          {portfolioError || marketError}
        </div>
      )}

      <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Stat label="Tong gia tri danh muc" value={formatVnd(data?.totalValue)} />
        <Stat label="Tien ao" value={formatVnd(data?.account.virtualCash)} />
        <Stat
          label="Lai/lo chua thuc hien"
          value={formatPnl(data?.unrealizedPnl)}
          valueClass={pnlColor(data?.unrealizedPnl)}
        />
        <Stat
          label="Lai/lo da thuc hien"
          value={formatPnl(data?.realizedPnl)}
          valueClass={pnlColor(data?.realizedPnl)}
        />
      </section>

      <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Stat
          label={`${selectedSymbol} latest`}
          value={marketLoading ? "Loading..." : formatVnd(displayPrice?.price)}
          valueClass={
            displayPrice && displayPrice.change < 0 ? "text-trading-down" : "text-trading-up"
          }
          helper={
            displayPrice
              ? `${displayPrice.change >= 0 ? "+" : ""}${numberFormatter.format(
                  displayPrice.change
                )} (${displayPrice.changePercent >= 0 ? "+" : ""}${numberFormatter.format(
                  displayPrice.changePercent
                )}%)`
              : undefined
          }
        />
        <Stat label="Trading date" value={marketLoading ? "Loading..." : displayPrice?.tradeDate ?? "-"} />
        <Stat
          label="P/E"
          value={
            marketLoading || latestRatio?.peRatio == null
              ? marketLoading
                ? "Loading..."
                : "-"
              : numberFormatter.format(latestRatio.peRatio)
          }
        />
        <Stat
          label="ROE"
          value={
            marketLoading || latestRatio?.roe == null
              ? marketLoading
                ? "Loading..."
                : "-"
              : `${numberFormatter.format(latestRatio.roe * 100)}%`
          }
        />
      </section>

      <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <TradingViewChart symbol={selectedSymbol} data={ohlcSeries?.data ?? []} />

        <section className="rounded-lg border border-hairline-on-dark bg-surface-card-dark p-4">
          <h2 className="mb-4 text-lg font-semibold text-body">Market Snapshot</h2>
          <div className="space-y-3 text-sm">
            <SnapshotRow label="Open" value={formatVnd(latestPrice?.open)} />
            <SnapshotRow label="High" value={formatVnd(latestPrice?.high)} />
            <SnapshotRow label="Low" value={formatVnd(latestPrice?.low)} />
            <SnapshotRow
              label="Volume"
              value={
                latestPrice ? new Intl.NumberFormat("vi-VN").format(latestPrice.volume) : "-"
              }
            />
            <SnapshotRow
              label="P/B"
              value={latestRatio?.pbRatio == null ? "-" : numberFormatter.format(latestRatio.pbRatio)}
            />
            <SnapshotRow
              label="EPS"
              value={latestRatio?.eps == null ? "-" : numberFormatter.format(latestRatio.eps)}
            />
          </div>
        </section>
      </div>
    </div>
  );
}

function Stat({
  label,
  value,
  helper,
  valueClass = "text-body",
}: {
  label: string;
  value: string;
  helper?: string;
  valueClass?: string;
}) {
  return (
    <div className="rounded-lg border border-hairline-on-dark bg-surface-card-dark p-4">
      <h2 className="text-sm font-medium text-muted-strong">{label}</h2>
      <p className={`mt-2 text-2xl font-bold ${valueClass}`}>{value}</p>
      {helper && <p className="mt-1 text-sm text-muted">{helper}</p>}
    </div>
  );
}

function SnapshotRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span className="text-muted-strong">{label}</span>
      <span className="text-right font-medium text-body">{value}</span>
    </div>
  );
}
