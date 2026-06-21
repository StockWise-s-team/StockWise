"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { IChartApi, ISeriesApi, CandlestickData, Time, UTCTimestamp } from "lightweight-charts";
import {
  CandlestickSeries,
  ColorType,
  createChart,
} from "lightweight-charts";
import { BarChart2, Loader2 } from "lucide-react";
import { TerminalEmptyState, TerminalSectionHeader } from "@/components/ui";
import { useMarketTicker } from "@/components/providers/MarketDataProvider";
import type { IntradayOhlcBar } from "@/lib/types";

const BUCKET_SECONDS = 300;
const VN_OFFSET_SECONDS = 7 * 3600;

interface IntradayOhlcChartProps {
  symbol: string;
  bars: IntradayOhlcBar[];
  interval?: string;
  loading?: boolean;
  error?: string | null;
}

function bucketStart(epochSeconds: number): number {
  return Math.floor(epochSeconds / BUCKET_SECONDS) * BUCKET_SECONDS;
}

function epochToUtc(iso: string): number {
  return Math.floor(new Date(iso).getTime() / 1000);
}

function barToCandle(bar: IntradayOhlcBar): CandlestickData | null {
  const timeSec = epochToUtc(bar.time);
  if (!Number.isFinite(timeSec)) return null;
  if (bar.open == null || bar.high == null || bar.low == null || bar.close == null) return null;
  return {
    time: timeSec as UTCTimestamp,
    open: Number(bar.open),
    high: Number(bar.high),
    low: Number(bar.low),
    close: Number(bar.close),
  };
}

function buildCurrentBar(
  bars: IntradayOhlcBar[],
  symbol: string,
  tick: { open?: number | null; high?: number | null; low?: number | null; close?: number | null; timestamp?: string | null; price?: number | null } | null | undefined
): IntradayOhlcBar | null {
  if (!tick) return null;
  const ts = tick.timestamp ?? null;
  if (!ts) return null;
  const tickSec = epochToUtc(ts);
  if (!Number.isFinite(tickSec)) return null;
  const bucket = bucketStart(tickSec);

  const close = Number(tick.close ?? tick.price ?? NaN);
  if (!Number.isFinite(close)) return null;
  const open = Number(tick.open ?? close);
  const highSeed = tick.high != null ? Number(tick.high) : close;
  const lowSeed = tick.low != null ? Number(tick.low) : close;
  const high = Math.max(highSeed, close, open);
  const low = Math.min(lowSeed, close, open);

  const last = bars.length > 0 ? bars[bars.length - 1] : null;
  if (last && bucketStart(epochToUtc(last.time)) === bucket) {
    return {
      time: new Date(bucket * 1000).toISOString(),
      open: last.open ?? open,
      high: Math.max(Number(last.high ?? close), high),
      low: Math.min(Number(last.low ?? close), low),
      close,
      volume: null,
      interval: last.interval,
    };
  }
  if (last && bucket * 1000 <= epochToUtc(last.time) * 1000) {
    return null;
  }
  return {
    time: new Date(bucket * 1000).toISOString(),
    open,
    high,
    low,
    close,
    volume: null,
    interval: last?.interval ?? "5m",
  };
}

function formatBucketLabel(epochSeconds: number): string {
  const localMs = (epochSeconds + VN_OFFSET_SECONDS) * 1000;
  const d = new Date(localMs);
  const hh = String(d.getUTCHours()).padStart(2, "0");
  const mm = String(d.getUTCMinutes()).padStart(2, "0");
  return `${hh}:${mm}`;
}

export function IntradayOhlcChart({ symbol, bars, interval = "5m", loading, error }: IntradayOhlcChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const barsRef = useRef<IntradayOhlcBar[]>(bars);
  barsRef.current = bars;

  const [lastBarLabel, setLastBarLabel] = useState<string | null>(null);
  const { ticker } = useMarketTicker(symbol);

  const lastTickTime = useMemo(() => {
    if (!ticker) return null;
    const ts = (ticker as { timestamp?: string | null }).timestamp;
    return ts ?? null;
  }, [ticker]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    if (chartRef.current) return;

    const chart = createChart(container, {
      layout: {
        background: { type: ColorType.Solid, color: "#141414" },
        textColor: "#d4d4d4",
        fontSize: 11,
        fontFamily: "JetBrains Mono, Fira Code, Consolas, monospace",
      },
      grid: {
        vertLines: { color: "#2a2a2a" },
        horzLines: { color: "#2a2a2a" },
      },
      crosshair: { mode: 0 },
      timeScale: {
        borderColor: "#2a2a2a",
        timeVisible: true,
        secondsVisible: false,
        rightOffset: 12,
      },
      rightPriceScale: {
        borderColor: "#2a2a2a",
        autoScale: true,
      },
      width: container.clientWidth,
      height: 380,
    });
    chartRef.current = chart;

    const series = chart.addSeries(CandlestickSeries, {
      upColor: "#4ade80",
      downColor: "#f87171",
      borderUpColor: "#4ade80",
      borderDownColor: "#f87171",
      wickUpColor: "#4ade80",
      wickDownColor: "#f87171",
      priceLineVisible: false,
      lastValueVisible: true,
    });
    seriesRef.current = series;

    const handleResize = () => {
      if (containerRef.current && chartRef.current) {
        try {
          chartRef.current.applyOptions({ width: containerRef.current.clientWidth });
        } catch {
          // ignore
        }
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      seriesRef.current = null;
      try {
        chart.remove();
      } catch {
        // ignore
      }
      chartRef.current = null;
    };
  }, []);

  useEffect(() => {
    const series = seriesRef.current;
    if (!series) return;
    const data = bars
      .map(barToCandle)
      .filter((d): d is CandlestickData => d != null)
      .sort((a, b) => (a.time as number) - (b.time as number));
    try {
      series.setData(data);
    } catch {
      // ignore
    }
    if (data.length > 0) {
      setLastBarLabel(formatBucketLabel(data[data.length - 1].time as number));
    }
  }, [bars]);

  useEffect(() => {
    if (!lastTickTime) return;
    const series = seriesRef.current;
    if (!series) return;
    const currentBar = buildCurrentBar(barsRef.current, symbol, {
      open: (ticker as { open?: number | null } | null)?.open ?? null,
      high: (ticker as { high?: number | null } | null)?.high ?? null,
      low: (ticker as { low?: number | null } | null)?.low ?? null,
      close: (ticker as { close?: number | null } | null)?.close ?? null,
      price: (ticker as { price?: number | null } | null)?.price ?? null,
      timestamp: lastTickTime,
    });
    if (!currentBar) return;
    const candle = barToCandle(currentBar);
    if (!candle) return;
    try {
      series.update(candle);
      setLastBarLabel(formatBucketLabel(candle.time as number));
    } catch {
      // ignore
    }
  }, [lastTickTime, ticker, symbol]);

  const subtitle = (() => {
    if (loading) return "Loading intraday bars…";
    if (error) return error;
    if (bars.length === 0) return "No intraday data available";
    const firstBucket = formatBucketLabel(epochToUtc(bars[0].time));
    return `${bars.length} ${interval} bars · ${firstBucket} → ${lastBarLabel ?? "now"} ICT`;
  })();

  return (
    <section>
      <TerminalSectionHeader
        icon={BarChart2}
        title={`${symbol} Intraday`}
        subtitle={subtitle}
        action={loading ? <Loader2 className="h-3.5 w-3.5 animate-spin text-terminal-muted" /> : undefined}
      />
      <div className="h-96 rounded border border-terminal-border bg-terminal-surface p-2">
        {bars.length === 0 && !loading ? (
          <TerminalEmptyState icon={BarChart2} title="No intraday bars" description="Stream D will populate bars during VN market hours." />
        ) : (
          <div ref={containerRef} className="h-full w-full" />
        )}
      </div>
    </section>
  );
}
