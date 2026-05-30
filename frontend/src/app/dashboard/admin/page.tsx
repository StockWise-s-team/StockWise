"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Newspaper,
  Radio,
  BookOpen,
  RefreshCw,
  Power,
  Plus,
  Trash2,
  ChevronRight,
  Activity,
  AlertCircle,
  CheckCircle2,
  Clock,
  Zap,
} from "lucide-react";
import { clsx } from "clsx";
import {
  newsSourcesApi,
  trackedSymbolsApi,
  wikiApi,
  pipelineApi,
} from "@/lib/api";
import type { NewsSource, WikiData, PipelineStatus } from "@/lib/types";

// ─── Status pill ────────────────────────────────────────────────────────────────

function StatusPill({
  status,
  label,
}: {
  status: "idle" | "running" | "error";
  label: string;
}) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 rounded px-2 py-0.5 text-xs font-mono font-medium uppercase tracking-wider",
        status === "idle" && "bg-terminal-border text-terminal-muted",
        status === "running" &&
          "bg-terminal-amber/10 text-terminal-amber border border-terminal-amber/20",
        status === "error" && "bg-terminal-red/10 text-terminal-red border border-terminal-red/20"
      )}
    >
      {status === "running" && (
        <RefreshCw className="h-3 w-3 animate-spin" />
      )}
      {status === "idle" && <Clock className="h-3 w-3" />}
      {status === "error" && <AlertCircle className="h-3 w-3" />}
      {label}
    </span>
  );
}

// ─── Section header ────────────────────────────────────────────────────────────

function SectionHeader({
  icon: Icon,
  title,
  subtitle,
}: {
  icon: React.ElementType;
  title: string;
  subtitle?: string;
}) {
  return (
    <div className="flex items-center gap-3 border-b border-terminal-border pb-3 mb-4">
      <div className="flex h-8 w-8 items-center justify-center rounded border border-terminal-border bg-terminal-surface">
        <Icon className="h-4 w-4 text-terminal-accent" />
      </div>
      <div>
        <h2 className="font-mono text-sm font-semibold tracking-widest uppercase text-terminal-text">
          {title}
        </h2>
        {subtitle && (
          <p className="text-xs font-mono text-terminal-muted">{subtitle}</p>
        )}
      </div>
    </div>
  );
}

// ─── News Sources section ─────────────────────────────────────────────────────

function NewsSourcesSection() {
  const [sources, setSources] = useState<NewsSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await newsSourcesApi.list();
      setSources(data);
    } catch {
      // silently handle
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const toggle = async (id: string, isActive: boolean) => {
    setToggling(id);
    try {
      await newsSourcesApi.toggle(id, !isActive);
      setSources((prev) =>
        prev.map((s) => (s.id === id ? { ...s, isActive: !isActive } : s))
      );
    } finally {
      setToggling(null);
    }
  };

  return (
    <section>
      <SectionHeader
        icon={Newspaper}
        title="News Sources"
        subtitle={`${sources.length} configured sources`}
      />
      {loading ? (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-12 rounded bg-terminal-surface animate-pulse"
            />
          ))}
        </div>
      ) : (
        <div className="space-y-1">
          {sources.map((src) => (
            <div
              key={src.id}
              className="group flex items-center justify-between rounded border border-terminal-border bg-terminal-surface px-3 py-2.5 transition-colors hover:border-terminal-accent/30"
            >
              <div className="flex items-center gap-3 min-w-0">
                <span
                  className={clsx(
                    "h-1.5 w-1.5 rounded-full flex-shrink-0",
                    src.isActive ? "bg-terminal-green" : "bg-terminal-muted"
                  )}
                />
                <div className="min-w-0">
                  <p className="font-mono text-xs font-semibold tracking-wide text-terminal-text truncate">
                    {src.name}
                  </p>
                  <p className="font-mono text-[10px] text-terminal-muted truncate">
                    {src.baseUrl}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="hidden group-hover:flex font-mono text-[10px] text-terminal-muted border border-terminal-border rounded px-1.5 py-0.5">
                  {src.crawlerType}
                </span>
                <button
                  onClick={() => toggle(src.id, src.isActive)}
                  disabled={toggling === src.id}
                  className={clsx(
                    "flex items-center gap-1.5 rounded px-2 py-1 text-[10px] font-mono font-medium uppercase tracking-wider border transition-all duration-200",
                    src.isActive
                      ? "border-terminal-green/30 text-terminal-green hover:bg-terminal-green/10 hover:border-terminal-green/50"
                      : "border-terminal-muted/30 text-terminal-muted hover:bg-terminal-green/10 hover:border-terminal-green/30 hover:text-terminal-green",
                    toggling === src.id && "opacity-50"
                  )}
                >
                  <Power className="h-3 w-3" />
                  {src.isActive ? "Disable" : "Enable"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

// ─── Tracked Symbols section ───────────────────────────────────────────────────

function TrackedSymbolsSection() {
  const [symbols, setSymbols] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [newSymbol, setNewSymbol] = useState("");
  const [adding, setAdding] = useState(false);
  const [removing, setRemoving] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await trackedSymbolsApi.list();
      setSymbols(data);
    } catch {
      // silently handle
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const add = async (e: React.FormEvent) => {
    e.preventDefault();
    const sym = newSymbol.trim().toUpperCase();
    if (!sym) return;
    setAdding(true);
    try {
      await trackedSymbolsApi.add(sym);
      setSymbols((prev) => [...prev, sym]);
      setNewSymbol("");
    } finally {
      setAdding(false);
    }
  };

  const remove = async (sym: string) => {
    setRemoving(sym);
    try {
      await trackedSymbolsApi.remove(sym);
      setSymbols((prev) => prev.filter((s) => s !== sym));
    } finally {
      setRemoving(null);
    }
  };

  return (
    <section>
      <SectionHeader
        icon={Radio}
        title="Tracked Symbols"
        subtitle={`${symbols.length} symbols in pipeline`}
      />
      <form onSubmit={add} className="flex gap-2 mb-3">
        <input
          value={newSymbol}
          onChange={(e) => setNewSymbol(e.target.value)}
          placeholder="ADD SYMBOL…"
          maxLength={10}
          className="flex-1 bg-terminal-bg border border-terminal-border rounded px-3 py-2 font-mono text-xs text-terminal-text placeholder:text-terminal-muted/50 focus:outline-none focus:border-terminal-accent/50 transition-colors"
        />
        <button
          type="submit"
          disabled={adding}
          className="flex items-center gap-1.5 rounded border border-terminal-accent/30 bg-terminal-accent/10 px-3 py-2 text-xs font-mono font-semibold text-terminal-accent uppercase tracking-wider hover:bg-terminal-accent/20 hover:border-terminal-accent/50 transition-all disabled:opacity-50"
        >
          <Plus className="h-3 w-3" />
          Add
        </button>
      </form>
      {loading ? (
        <div className="h-24 rounded bg-terminal-surface animate-pulse" />
      ) : symbols.length === 0 ? (
        <p className="font-mono text-xs text-terminal-muted text-center py-8">
          No symbols tracked. Run seed script to populate.
        </p>
      ) : (
        <div className="flex flex-wrap gap-1.5">
          {symbols.map((sym) => (
            <span
              key={sym}
              className="inline-flex items-center gap-1.5 rounded border border-terminal-border bg-terminal-surface px-2 py-1 font-mono text-xs font-medium text-terminal-text group"
            >
              <span className="h-1 w-1 rounded-full bg-terminal-accent" />
              {sym}
              <button
                onClick={() => remove(sym)}
                disabled={removing === sym}
                className="ml-1 text-terminal-muted hover:text-terminal-red transition-colors disabled:opacity-50"
              >
                <Trash2 className="h-3 w-3" />
              </button>
            </span>
          ))}
        </div>
      )}
    </section>
  );
}

// ─── Wiki section ───────────────────────────────────────────────────────────────

function WikiSection() {
  const [wikis, setWikis] = useState<WikiData[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedSymbol, setExpandedSymbol] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await wikiApi.list(20);
      setWikis(data);
    } catch {
      // silently handle
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  return (
    <section>
      <SectionHeader
        icon={BookOpen}
        title="Company Wiki"
        subtitle="Synthesized from news + market data"
      />
      {loading ? (
        <div className="space-y-2">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-12 rounded bg-terminal-surface animate-pulse" />
          ))}
        </div>
      ) : wikis.length === 0 ? (
        <p className="font-mono text-xs text-terminal-muted text-center py-8">
          No wiki data. Run synthesis to generate.
        </p>
      ) : (
        <div className="space-y-1">
          {wikis.map((wiki) => (
            <div key={wiki.symbol} className="border border-terminal-border rounded bg-terminal-surface overflow-hidden">
              <button
                onClick={() =>
                  setExpandedSymbol(
                    expandedSymbol === wiki.symbol ? null : wiki.symbol
                  )
                }
                className="w-full flex items-center justify-between px-3 py-2.5 hover:bg-terminal-border/30 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs font-bold tracking-wider text-terminal-accent w-14">
                    {wiki.symbol}
                  </span>
                  <span className="font-mono text-xs text-terminal-muted truncate max-w-[120px]">
                    {wiki.companyName}
                  </span>
                  <span
                    className={clsx(
                      "font-mono text-[10px] px-1.5 py-0.5 rounded border",
                      wiki.sentiment === "positive" &&
                        "border-terminal-green/30 text-terminal-green",
                      wiki.sentiment === "negative" &&
                        "border-terminal-red/30 text-terminal-red",
                      wiki.sentiment === "neutral" &&
                        "border-terminal-border text-terminal-muted"
                    )}
                  >
                    {wiki.sentiment}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-mono text-[10px] text-terminal-muted">
                    v{wiki.version}
                  </span>
                  <ChevronRight
                    className={clsx(
                      "h-3 w-3 text-terminal-muted transition-transform duration-200",
                      expandedSymbol === wiki.symbol && "rotate-90"
                    )}
                  />
                </div>
              </button>
              {expandedSymbol === wiki.symbol && (
                <div className="border-t border-terminal-border px-3 py-3 space-y-3 bg-terminal-bg">
                  <p className="font-mono text-[10px] text-terminal-text leading-relaxed">
                    {wiki.businessSummary}
                  </p>
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      { label: "PE", value: wiki.financialsSnapshot.pe?.toFixed(1) },
                      { label: "PB", value: wiki.financialsSnapshot.pb?.toFixed(1) },
                      { label: "ROE", value: wiki.financialsSnapshot.roe?.toFixed(1) },
                    ].map(({ label, value }) => (
                      <div key={label} className="rounded border border-terminal-border bg-terminal-surface px-2 py-1.5 text-center">
                        <p className="font-mono text-[10px] text-terminal-muted">{label}</p>
                        <p className="font-mono text-xs font-semibold text-terminal-text">
                          {value ?? "—"}
                        </p>
                      </div>
                    ))}
                  </div>
                  {wiki.keyRisks.length > 0 && (
                    <div>
                      <p className="font-mono text-[10px] text-terminal-muted mb-1 uppercase tracking-wider">
                        Key Risks
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {wiki.keyRisks.slice(0, 5).map((risk, i) => (
                          <span
                            key={i}
                            className="font-mono text-[10px] rounded border border-terminal-red/20 bg-terminal-red/5 px-1.5 py-0.5 text-terminal-red/80"
                          >
                            {risk}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  <p className="font-mono text-[10px] text-terminal-muted">
                    Updated: {new Date(wiki.updatedAt).toLocaleString("vi-VN")}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

// ─── Pipeline actions ──────────────────────────────────────────────────────────

function PipelineActions() {
  const [triggering, setTriggering] = useState<string | null>(null);

  const triggerSeed = async () => {
    setTriggering("seed");
    try {
      await trackedSymbolsApi.triggerSeed();
    } finally {
      setTriggering(null);
    }
  };

  const triggerSynthesis = async () => {
    setTriggering("synthesis");
    try {
      await pipelineApi.triggerSynthesis();
    } finally {
      setTriggering(null);
    }
  };

  return (
    <section>
      <SectionHeader
        icon={Zap}
        title="Pipeline Actions"
        subtitle="Manual triggers"
      />
      <div className="grid grid-cols-2 gap-2">
        <button
          onClick={triggerSeed}
          disabled={!!triggering}
          className="flex items-center justify-center gap-2 rounded border border-terminal-border bg-terminal-surface px-3 py-2.5 font-mono text-xs font-medium text-terminal-text hover:border-terminal-accent/40 hover:text-terminal-accent hover:bg-terminal-accent/5 transition-all disabled:opacity-50"
        >
          <RefreshCw className={clsx("h-3.5 w-3.5", triggering === "seed" && "animate-spin")} />
          Seed Prices
        </button>
        <button
          onClick={triggerSynthesis}
          disabled={!!triggering}
          className="flex items-center justify-center gap-2 rounded border border-terminal-border bg-terminal-surface px-3 py-2.5 font-mono text-xs font-medium text-terminal-text hover:border-terminal-accent/40 hover:text-terminal-accent hover:bg-terminal-accent/5 transition-all disabled:opacity-50"
        >
          <Zap className={clsx("h-3.5 w-3.5", triggering === "synthesis" && "animate-spin")} />
          Synthesize
        </button>
      </div>
    </section>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function AdminPage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <div
      className="min-h-screen bg-terminal-bg text-terminal-text font-mono"
      style={{
        fontFamily: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
      }}
    >
      {/* Top bar */}
      <header className="border-b border-terminal-border bg-terminal-surface px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="font-display text-base font-bold tracking-[0.2em] uppercase text-terminal-accent">
            StockWise
          </h1>
          <span className="font-mono text-[10px] text-terminal-muted tracking-widest uppercase">
            Pipeline Admin
          </span>
        </div>
        <div className="flex items-center gap-2 font-mono text-[10px] text-terminal-muted">
          <span className="h-1.5 w-1.5 rounded-full bg-terminal-green animate-pulse" />
          System Online
        </div>
      </header>

      {/* Main grid */}
      <div className="p-6">
        <div className="grid grid-cols-12 gap-5">
          {/* Left column — sources + symbols */}
          <div className="col-span-5 space-y-5">
            <NewsSourcesSection />
            <TrackedSymbolsSection />
          </div>

          {/* Right column — wiki + actions */}
          <div className="col-span-7 space-y-5">
            <WikiSection />
            <PipelineActions />
          </div>
        </div>
      </div>
    </div>
  );
}
