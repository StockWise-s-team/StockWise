"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { IChartApi, ISeriesApi, LineData, Time, UTCTimestamp } from "lightweight-charts";
import {
  ColorType,
  LineSeries,
  createChart,
} from "lightweight-charts";
import { LineChart, Loader2, Zap } from "lucide-react";
import { clsx } from "clsx";
import type { OhlcPoint, Timeframe } from "@/lib/types";
import { TerminalEmptyState, TerminalSectionHeader } from "@/components/ui";
import { marketApi } from "@/lib/api";
import { useMarketData, useMarketTicker } from "@/components/providers/MarketDataProvider";
import { useAuth } from "@/components/providers/AuthProvider";

const PALETTE = [
  "#f0b429", // terminal-accent (amber)
  "#4ade80", // terminal-green
  "#f87171", // terminal-red
  "#60a5fa", // blue-400
  "#c084fc", // purple-400
  "#34d399", // emerald-400
  "#fb923c", // orange-400
  "#f472b6", // pink-400
];

function colorFor(symbol: string, index: number): string {
  if (PALETTE[index]) return PALETTE[index];
  let hash = 0;
  for (let i = 0; i < symbol.length; i++) {
    hash = (hash * 31 + symbol.charCodeAt(i)) >>> 0;
  }
  return PALETTE[hash % PALETTE.length];
}

interface TimeframeConfig {
  days: number;
  liveMode: boolean;
  bucketSeconds: number;
}

const TF_CONFIG: Record<Timeframe, TimeframeConfig> = {
  "1m":  { days: 1,   liveMode: true,  bucketSeconds: 60 },
  "5m":  { days: 1,   liveMode: true,  bucketSeconds: 300 },
  "1d":  { days: 30,  liveMode: false, bucketSeconds: 86400 },
  "1M":  { days: 365, liveMode: false, bucketSeconds: 86400 * 30 },
};

function dateToUTCTimestamp(dateStr: string | Date): UTCTimestamp {
  const d = typeof dateStr === "string" ? new Date(dateStr) : dateStr;
  return Math.floor(d.getTime() / 1000) as UTCTimestamp;
}

/**
 * Safe wrapper: calls series.setData() only if the series is still
 * attached to a live chart. Catches the "Value is null" error that
 * lightweight-charts throws when the series has been detached.
 */
function safeSetData(
  series: ISeriesApi<"Line"> | undefined | null,
  data: LineData[]
) {
  if (!series) return;
  try {
    series.setData(data);
  } catch {
    // series may have been removed from the chart — ignore
  }
}

/**
 * Safe wrapper: calls series.update() only if the point is valid and
 * the series is still attached.
 */
function safeUpdate(
  series: ISeriesApi<"Line"> | undefined | null,
  point: LineData
) {
  if (!series) return;
  // Guard against null / NaN values that cause "Value is null" in LW-Charts
  if (!Number.isFinite(point.value) || point.value <= 0) return;
  if (!Number.isFinite(point.time as number)) return;
  try {
    series.update(point);
  } catch {
    // ignore: LW-Charts rejects times that go backward or null values
  }
}

export interface MultiSymbolChartProps {
  symbols: string[];
  defaultSymbol?: string;
  initialTimeframe?: Timeframe;
}

export function MultiSymbolChart({
  symbols,
  defaultSymbol,
  initialTimeframe = "1m",
}: MultiSymbolChartProps) {
  const { isAuthenticated } = useAuth();
  const { getLiveHistory } = useMarketData();
  const [timeframe, setTimeframe] = useState<Timeframe>(initialTimeframe);
  const [enabledSymbols, setEnabledSymbols] = useState<Set<string>>(() => {
    if (defaultSymbol && symbols.includes(defaultSymbol)) {
      return new Set([defaultSymbol, ...symbols.filter((s) => s !== defaultSymbol).slice(0, 2)]);
    }
    return new Set(symbols.slice(0, Math.min(3, symbols.length)));
  });

  // ─── IMPORTANT: series objects are stored ONLY in a ref, NOT in state ───────
  // Storing them in state caused a race condition: the old state value was still
  // read by LiveSymbolUpdater after series were re-created, producing stale refs
  // that lightweight-charts had already detached ("Value is null").
  const seriesBySymbolRef = useRef<Record<string, ISeriesApi<"Line">>>({});

  // Bumped after every fetch cycle so LiveSymbolUpdater keys get refreshed
  const [seriesVersion, setSeriesVersion] = useState(0);

  const [loading, setLoading] = useState<Record<string, boolean>>({});
  const [error, setError] = useState<string | null>(null);
  const [tickCount, setTickCount] = useState<Record<string, number>>({});

  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);

  // Each new fetch run gets a unique generation number.
  // An async callback aborts itself if its generation no longer matches.
  const fetchGenerationRef = useRef(0);

  // ─── Chart initialisation ───────────────────────────────────────────────────
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    // Guard against React Strict Mode double-invoke
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
        rightOffset: 80,
      },
      rightPriceScale: {
        borderColor: "#2a2a2a",
        autoScale: true,
      },
      width: container.clientWidth,
      height: 380,
    });
    chartRef.current = chart;

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
      // Abort any in-flight fetch before destroying the chart
      fetchGenerationRef.current += 1;
      // Clear refs BEFORE chart.remove() so no lingering code can call series methods
      seriesBySymbolRef.current = {};
      try {
        chart.remove();
      } catch {
        // ignore
      }
      chartRef.current = null;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ─── Sync enabledSymbols when props.symbols changes ─────────────────────────
  useEffect(() => {
    setEnabledSymbols((prev) => {
      const next = new Set<string>();
      for (const s of prev) {
        if (symbols.includes(s)) next.add(s);
      }
      if (next.size === 0) {
        if (defaultSymbol && symbols.includes(defaultSymbol)) {
          next.add(defaultSymbol);
        }
        for (const s of symbols) {
          if (next.size >= 3) break;
          if (!next.has(s)) next.add(s);
        }
      }
      return next;
    });
  }, [symbols, defaultSymbol]);

  // ─── Fetch data whenever enabledSymbols / timeframe changes ─────────────────
  useEffect(() => {
    // Take ownership of this fetch run
    const generation = ++fetchGenerationRef.current;

    const chart = chartRef.current;
    if (!chart) return;

    const cfg = TF_CONFIG[timeframe];
    const end = new Date();
    const start = new Date(end);
    start.setDate(end.getDate() - cfg.days);
    const startDate = start.toISOString().slice(0, 10);
    const endDate = end.toISOString().slice(0, 10);

    // 1. Remove series for symbols that are no longer enabled
    for (const sym of Object.keys(seriesBySymbolRef.current)) {
      if (!enabledSymbols.has(sym)) {
        try { chart.removeSeries(seriesBySymbolRef.current[sym]); } catch { /* ignore */ }
        delete seriesBySymbolRef.current[sym];
      }
    }

    setError(null);
    setTickCount({});
    const newLoading: Record<string, boolean> = {};
    for (const sym of enabledSymbols) newLoading[sym] = true;
    setLoading(newLoading);

    const fetchAll = async () => {
      const fetchPromises = Array.from(enabledSymbols).map(async (sym) => {
        const color = colorFor(sym, symbols.indexOf(sym));

        try {
          // Check before every async boundary
          if (generation !== fetchGenerationRef.current) return;

          // 2. Ensure a series exists for this symbol
          let s = seriesBySymbolRef.current[sym];
          if (!s) {
            if (!chartRef.current) return; // chart destroyed mid-flight
            try {
              s = chartRef.current.addSeries(LineSeries, {
                color,
                lineWidth: 2,
                priceLineVisible: false,
                lastValueVisible: true,
                title: sym,
              });
              seriesBySymbolRef.current[sym] = s;
            } catch {
              // Chart was destroyed while we were adding the series
              return;
            }
          } else {
            try { s.applyOptions({ color }); } catch { /* ignore */ }
          }

          // 3. Fetch and populate data
          if (cfg.liveMode) {
            // Fetch today's intraday REST prices first
            try {
              const intraday = await marketApi.getIntradayPrices(sym);
              if (generation !== fetchGenerationRef.current) return;

              if (intraday && intraday.length > 0) {
                const bucketMap = new Map<number, number>();
                for (const p of intraday) {
                  const price = Number(p.price);
                  if (!Number.isFinite(price) || price <= 0) continue;
                  const ts =
                    Math.floor(new Date(p.timestamp).getTime() / 1000 / cfg.bucketSeconds) *
                    cfg.bucketSeconds;
                  if (!Number.isFinite(ts)) continue;
                  bucketMap.set(ts, price);
                }
                const sorted = Array.from(bucketMap.entries())
                  .sort((a, b) => a[0] - b[0])
                  .map(([time, value]) => ({ time: time as Time, value }));
                safeSetData(seriesBySymbolRef.current[sym], sorted);
              } else {
                safeSetData(seriesBySymbolRef.current[sym], []);
              }
            } catch {
              if (generation !== fetchGenerationRef.current) return;
              safeSetData(seriesBySymbolRef.current[sym], []);
            }

            // Replay live ticks that arrived before the fetch completed
            if (generation !== fetchGenerationRef.current) return;
            const history = getLiveHistory(sym);
            for (const tick of history) {
              const rawPrice = Number((tick as any).price ?? (tick as any).close ?? 0);
              if (!Number.isFinite(rawPrice) || rawPrice <= 0) continue;
              const tickSec = Math.floor(new Date((tick as any).timestamp).getTime() / 1000);
              const ts =
                Math.floor(tickSec / cfg.bucketSeconds) * cfg.bucketSeconds as UTCTimestamp;
              safeUpdate(seriesBySymbolRef.current[sym], { time: ts as Time, value: rawPrice });
            }
          } else {
            // Daily / monthly OHLC
            const seriesData = await marketApi.getOhlc(sym, { startDate, endDate });
            if (generation !== fetchGenerationRef.current) return;

            const raw: LineData[] = (seriesData.data || [])
              .map((p: OhlcPoint) => ({
                time: dateToUTCTimestamp(`${p.date}T15:00:00Z`) as Time,
                value: Number(p.close),
              }))
              .filter((d: LineData) =>
                Number.isFinite(d.time as number) && Number.isFinite(d.value) && d.value > 0
              );

            // Deduplicate + sort
            const seen = new Set<number>();
            const uniqueData: LineData[] = [];
            for (const d of raw.sort((a, b) => (a.time as number) - (b.time as number))) {
              const t = d.time as number;
              if (!seen.has(t)) { seen.add(t); uniqueData.push(d); }
            }
            safeSetData(seriesBySymbolRef.current[sym], uniqueData);
          }
        } catch (e) {
          if (generation !== fetchGenerationRef.current) return;
          console.warn(`[MultiSymbolChart] Failed to load ${sym}`, e);
        } finally {
          if (generation === fetchGenerationRef.current) {
            setLoading((prev) => ({ ...prev, [sym]: false }));
          }
        }
      });

      await Promise.all(fetchPromises);
      if (generation !== fetchGenerationRef.current) return;

      // Bump version so LiveSymbolUpdater components re-key and read fresh series
      setSeriesVersion((v) => v + 1);
      try { chartRef.current?.timeScale().fitContent(); } catch { /* ignore */ }
    };

    fetchAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabledSymbols, timeframe, symbols]);

  // ─── Toggle a symbol on/off ─────────────────────────────────────────────────
  const toggleSymbol = useCallback((sym: string) => {
    setEnabledSymbols((prev) => {
      const next = new Set(prev);
      if (next.has(sym)) { next.delete(sym); } else { next.add(sym); }
      return next;
    });
  }, []);

  // ─── Render ─────────────────────────────────────────────────────────────────
  return (
    <section>
      <TerminalSectionHeader
        icon={LineChart}
        title="Multi-symbol price chart"
        subtitle={
          TF_CONFIG[timeframe].liveMode
            ? `Live ticks · ${timeframe} bucket · accumulating`
            : `Daily closes · ${timeframe} view`
        }
        action={
          <div className="flex flex-wrap items-center gap-1">
            {(["1m"] as Timeframe[]).map((tf) => (
              <button
                key={tf}
                type="button"
                onClick={() => setTimeframe(tf)}
                className={clsx(
                  "h-7 rounded border px-2 text-[10px] font-mono font-semibold uppercase tracking-wider transition-colors",
                  tf === timeframe
                    ? "border-terminal-accent/60 bg-terminal-accent/10 text-terminal-accent"
                    : "border-terminal-border bg-terminal-surface text-terminal-muted hover:border-terminal-accent/30 hover:text-terminal-text"
                )}
              >
                {tf}
              </button>
            ))}
          </div>
        }
      />

      {/* Legend */}
      <div className="mb-3 flex flex-wrap gap-1.5">
        {symbols.length === 0 ? (
          <span className="font-mono text-[10px] text-terminal-muted">
            No tracked symbols available
          </span>
        ) : (
          symbols.map((sym, idx) => {
            const color = colorFor(sym, idx);
            const enabled = enabledSymbols.has(sym);
            const isLoading = loading[sym];
            const ticks = tickCount[sym] ?? 0;
            return (
              <button
                key={sym}
                type="button"
                onClick={() => toggleSymbol(sym)}
                className={clsx(
                  "inline-flex items-center gap-1.5 rounded border px-2 py-1 font-mono text-[10px] font-semibold uppercase tracking-wider transition-colors",
                  enabled
                    ? "border-terminal-border bg-terminal-surface text-terminal-text"
                    : "border-terminal-border bg-transparent text-terminal-muted opacity-60 hover:opacity-100"
                )}
                aria-pressed={enabled}
              >
                <span
                  className="h-2 w-2 rounded-full"
                  style={{ backgroundColor: color, opacity: enabled ? 1 : 0.4 }}
                />
                {sym}
                {enabled && TF_CONFIG[timeframe].liveMode && ticks > 0 && (
                  <span className="inline-flex items-center gap-0.5 text-[9px] text-terminal-green">
                    <Zap className="h-2.5 w-2.5" />
                    {ticks}
                  </span>
                )}
                {enabled && isLoading && <Loader2 className="h-2.5 w-2.5 animate-spin" />}
                <span className="text-[9px] text-terminal-muted">{enabled ? "ON" : "OFF"}</span>
              </button>
            );
          })
        )}
      </div>

      {/* Chart container */}
      <div className="h-[420px] rounded border border-terminal-border bg-terminal-surface p-2">
        {error ? (
          <TerminalEmptyState icon={LineChart} title="Chart unavailable" description={error} />
        ) : (
          <div ref={containerRef} className="h-full w-full" />
        )}
      </div>

      {/* Live tick updaters — one per enabled symbol.
          Key includes seriesVersion so they re-mount after a fresh fetch cycle. */}
      {isAuthenticated &&
        Array.from(enabledSymbols).map((sym) => (
          <LiveSymbolUpdater
            key={`${sym}-${timeframe}-${seriesVersion}`}
            symbol={sym}
            seriesRef={seriesBySymbolRef}
            liveMode={TF_CONFIG[timeframe].liveMode}
            bucketSeconds={TF_CONFIG[timeframe].bucketSeconds}
            onTick={() =>
              setTickCount((prev) => ({ ...prev, [sym]: (prev[sym] ?? 0) + 1 }))
            }
          />
        ))}
    </section>
  );
}

// ─── LiveSymbolUpdater ────────────────────────────────────────────────────────
/**
 * Subscribes to live ticks for one symbol and forwards valid points to the
 * shared seriesBySymbolRef.  We pass the WHOLE ref (not a specific series)
 * so this component never needs to re-mount just because the series object
 * was (re)created during a fetch cycle.
 */
function LiveSymbolUpdater({
  symbol,
  seriesRef,
  liveMode,
  bucketSeconds,
  onTick,
}: {
  symbol: string;
  seriesRef: React.RefObject<Record<string, ISeriesApi<"Line">>>;
  liveMode: boolean;
  bucketSeconds: number;
  onTick: () => void;
}) {
  const { ticker } = useMarketTicker(symbol);
  const onTickRef = useRef(onTick);
  onTickRef.current = onTick;

  // Track the last ticker reference we processed to skip duplicate renders
  const prevTickerRef = useRef<typeof ticker>(null);

  useEffect(() => {
    if (!ticker) return;
    // Skip if this is the exact same tick object (no new data arrived)
    if (ticker === prevTickerRef.current) return;
    prevTickerRef.current = ticker;

    const rawPrice = Number((ticker as any).price ?? (ticker as any).close ?? 0);
    if (!Number.isFinite(rawPrice) || rawPrice <= 0) return;

    // Look up the series in the shared ref — it may not exist yet if the
    // fetch is still in progress; in that case just skip this tick.
    const series = seriesRef.current?.[symbol];
    if (!series) return;

    const nowSec = Math.floor(Date.now() / 1000);
    const ts = liveMode
      ? (Math.floor(nowSec / bucketSeconds) * bucketSeconds) as UTCTimestamp
      : (nowSec as UTCTimestamp);

    safeUpdate(series, { time: ts as Time, value: rawPrice });
    onTickRef.current();
  // Only re-run when the ticker itself changes
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ticker]);

  return null;
}
