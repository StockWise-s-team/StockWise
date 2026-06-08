"use client";

import { useEffect, useMemo, useState } from "react";
import { useAuth } from "@/components/providers/AuthProvider";
import { OHLCChart } from "@/components/charts/OHLCChart";
import { usePortfolio } from "@/hooks/usePortfolio";
import { marketApi } from "@/lib/api";
import { formatVnd, formatPnl, pnlColor } from "@/lib/format";
import type { FinancialRatioList, LatestPrice, OhlcSeries } from "@/lib/types";

const DEFAULT_SYMBOL = "FPT";

const numberFormatter = new Intl.NumberFormat("vi-VN", {
  maximumFractionDigits: 2,
});

export default function DashboardPage() {
  const { user } = useAuth();
  const { data, error: portfolioError } = usePortfolio(user?.id);
  const [latestPrice, setLatestPrice] = useState<LatestPrice | null>(null);
  const [ohlcSeries, setOhlcSeries] = useState<OhlcSeries | null>(null);
  const [ratios, setRatios] = useState<FinancialRatioList | null>(null);
  const [marketLoading, setMarketLoading] = useState(true);
  const [marketError, setMarketError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadMarket() {
      try {
        setMarketLoading(true);
        setMarketError(null);

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
  }, []);

  const latestRatio = useMemo(() => ratios?.ratios?.[0] ?? null, [ratios]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-body">Dashboard</h1>
        <p className="mt-1 text-sm text-muted-strong">
          Tong quan danh muc va du lieu thi truong cho ma {DEFAULT_SYMBOL}.
        </p>
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
          label={`${DEFAULT_SYMBOL} latest`}
          value={marketLoading ? "Loading..." : formatVnd(latestPrice?.price)}
          valueClass={
            latestPrice && latestPrice.change < 0 ? "text-trading-down" : "text-trading-up"
          }
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
        <Stat label="Trading date" value={marketLoading ? "Loading..." : latestPrice?.tradeDate ?? "-"} />
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
        <OHLCChart symbol={DEFAULT_SYMBOL} data={ohlcSeries?.data ?? []} />

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
