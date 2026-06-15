"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Newspaper,
  Radio,
  BookOpen,
  Search,
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
  createProgressSSE,
} from "@/lib/api";
import type { NewsSource, WikiData, PipelineStatus, PipelineProgress, PipelinePhase } from "@/lib/types";
import { PipelineHistorySection } from "@/components/pipeline/PipelineHistorySection";

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
                      ? "border-terminal-green/50 text-terminal-green bg-terminal-green/10 hover:bg-terminal-green/20"
                      : "border-terminal-border text-terminal-muted hover:border-terminal-green/40 hover:text-terminal-green hover:bg-terminal-green/5",
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

function TrackedSymbolsSection({
  symbols,
  onRemove,
  onAdd,
}: {
  symbols: string[];
  onRemove: (sym: string) => void;
  onAdd: (sym: string) => void;
}) {
  const [removing, setRemoving] = useState<string | null>(null);
  const [adding, setAdding] = useState(false);
  const [addInput, setAddInput] = useState("");
  const [addError, setAddError] = useState("");

  const remove = async (sym: string) => {
    setRemoving(sym);
    try {
      await trackedSymbolsApi.remove(sym);
      onRemove(sym);
    } finally {
      setRemoving(null);
    }
  };

  const addSymbol = async () => {
    const s = addInput.toUpperCase().trim();
    if (!s) return;
    if (!/^[A-Z]{3,5}$/.test(s)) {
      setAddError("Invalid format (e.g. ACB, VNM)");
      return;
    }
    if (symbols.includes(s)) {
      setAddError(`${s} already tracked`);
      return;
    }
    try {
      await trackedSymbolsApi.add(s);
      onAdd(s);
      setAddInput("");
      setAddError("");
      setAdding(false);
    } catch {
      setAddError("Failed to add — check if symbol is valid");
    }
  };

  return (
    <section>
      <div className="flex items-center justify-between mb-3">
        <SectionHeader
          icon={Radio}
          title="Tracked Symbols"
          subtitle={`${symbols.length} symbols in pipeline`}
        />
        <button
          onClick={() => setAdding(true)}
          className="flex items-center gap-1 rounded border border-terminal-accent/30 bg-terminal-accent/5 px-2 py-1 font-mono text-[10px] text-terminal-accent hover:bg-terminal-accent/10 hover:border-terminal-accent/50 transition-all"
        >
          <Plus className="h-3 w-3" />
          Add
        </button>
      </div>

      {adding && (
        <div className="mb-3 rounded border border-terminal-accent/30 bg-terminal-accent/5 p-2.5 space-y-1.5">
          <div className="flex items-center gap-1.5">
            <input
              autoFocus
              value={addInput}
              onChange={(e) => { setAddInput(e.target.value.toUpperCase()); setAddError(""); }}
              onKeyDown={(e) => {
                if (e.key === "Enter") addSymbol();
                if (e.key === "Escape") { setAdding(false); setAddInput(""); setAddError(""); }
              }}
              placeholder="e.g. VNM"
              maxLength={10}
              className="flex-1 bg-terminal-bg border border-terminal-border rounded px-2 py-1 font-mono text-xs text-terminal-text placeholder:text-terminal-muted/40 focus:outline-none focus:border-terminal-accent/50 uppercase"
            />
            <button
              onClick={addSymbol}
              className="rounded border border-terminal-accent/40 bg-terminal-accent/10 px-2 py-1 font-mono text-[10px] text-terminal-accent hover:bg-terminal-accent/20 transition-all"
            >
              Add
            </button>
            <button
              onClick={() => { setAdding(false); setAddInput(""); setAddError(""); }}
              className="rounded border border-terminal-border px-2 py-1 font-mono text-[10px] text-terminal-muted hover:text-terminal-text transition-all"
            >
              Cancel
            </button>
          </div>
          {addError && (
            <p className="font-mono text-[10px] text-terminal-red pl-0.5">{addError}</p>
          )}
        </div>
      )}

      {symbols.length === 0 ? (
        <p className="font-mono text-xs text-terminal-muted text-center py-8">
          No symbols tracked. Click Add above.
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

function WikiSection({ trackedSymbols }: { trackedSymbols: string[] }) {
  const [wikis, setWikis] = useState<WikiData[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedSymbol, setExpandedSymbol] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const PAGE_SIZE = 10;
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchInput, setSearchInput] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await wikiApi.list({ limit: 1000, offset: 0, search: searchQuery });
      let filtered: WikiData[];
      if (searchQuery) {
        filtered = (data.wikis ?? data) as WikiData[];
      } else {
        const tracked = new Set(trackedSymbols);
        filtered = (data.wikis ?? data).filter((w: WikiData) => tracked.has(w.symbol));
      }
      setTotal(filtered.length);
      const start = (page - 1) * PAGE_SIZE;
      setWikis(filtered.slice(start, start + PAGE_SIZE));
    } catch {
      // silently handle
    } finally {
      setLoading(false);
    }
  }, [trackedSymbols, page, searchQuery]);

  useEffect(() => { setPage(1); }, [searchQuery]);

  useEffect(() => { load(); }, [load]);

  const handleSearch = (value: string) => {
    setSearchInput(value);
  };

  const submitSearch = () => {
    setSearchQuery(searchInput.trim());
  };

  return (
    <section>
      <div className="flex items-center justify-between mb-3">
        <SectionHeader
          icon={BookOpen}
          title="Company Wiki"
          subtitle="Synthesized from news + market data"
        />
        <div className="flex items-center gap-1.5">
          <div className="relative">
            <input
              value={searchInput}
              onChange={(e) => handleSearch(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") submitSearch(); }}
              placeholder="Search symbol…"
              maxLength={10}
              className="w-32 bg-terminal-bg border border-terminal-border rounded px-2 py-1 pr-7 font-mono text-[10px] text-terminal-text placeholder:text-terminal-muted/40 focus:outline-none focus:border-terminal-accent/50 transition-colors uppercase"
            />
            {searchInput && (
              <button
                onClick={() => { setSearchInput(""); setSearchQuery(""); }}
                className="absolute right-1 top-1/2 -translate-y-1/2 text-terminal-muted hover:text-terminal-text transition-colors leading-none"
              >
                <span className="text-[10px]">✕</span>
              </button>
            )}
          </div>
          <button
            onClick={submitSearch}
            className="flex items-center gap-1 rounded border border-terminal-accent/30 bg-terminal-accent/5 px-1.5 py-1 font-mono text-[10px] text-terminal-accent hover:bg-terminal-accent/10 hover:border-terminal-accent/50 transition-all"
          >
            <Search className="h-3 w-3" />
          </button>
        </div>
      </div>
      {loading ? (
        <div className="space-y-2">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-12 rounded bg-terminal-surface animate-pulse" />
          ))}
        </div>
      ) : wikis.length === 0 ? (
        <p className="font-mono text-xs text-terminal-muted text-center py-8">
          {searchQuery ? `No results for "${searchQuery}"` : "No wiki data. Run synthesis to generate."}
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
                      (wiki.sentiment === "bullish" || wiki.sentiment === "positive") &&
                        "border-terminal-green/30 text-terminal-green",
                      (wiki.sentiment === "bearish" || wiki.sentiment === "negative") &&
                        "border-terminal-red/30 text-terminal-red",
                      (wiki.sentiment === "neutral" || wiki.sentiment === "slightly_bullish" || wiki.sentiment === "slightly_bearish") &&
                        "border-terminal-border text-terminal-muted",
                      wiki.sentiment === "slightly_bullish" &&
                        "border-terminal-green/20 text-terminal-green/70",
                      wiki.sentiment === "slightly_bearish" &&
                        "border-terminal-amber/20 text-terminal-amber/70"
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
                      { label: "PE", value: wiki.financialsSnapshot?.pe?.toFixed(1) },
                      { label: "PB", value: wiki.financialsSnapshot?.pb?.toFixed(1) },
                      { label: "ROE", value: wiki.financialsSnapshot?.roe?.toFixed(1) },
                    ].map(({ label, value }) => (
                      <div key={label} className="rounded border border-terminal-border bg-terminal-surface px-2 py-1.5 text-center">
                        <p className="font-mono text-[10px] text-terminal-muted">{label}</p>
                        <p className="font-mono text-xs font-semibold text-terminal-text">
                          {value ?? "—"}
                        </p>
                      </div>
                    ))}
                  </div>
                  {(wiki.keyRisks?.length ?? 0) > 0 && (
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

          {/* Wiki pagination */}
          {total > PAGE_SIZE && (() => {
            const totalPages = Math.ceil(total / PAGE_SIZE);
            return (
              <div className="flex items-center justify-between px-2 py-2 border border-terminal-border rounded bg-terminal-surface mt-1">
                <span className="font-mono text-[10px] text-terminal-muted">
                  {total} symbols / p.{page} of {totalPages}
                </span>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="h-5 w-5 flex items-center justify-center rounded border border-terminal-border text-terminal-muted hover:text-terminal-text hover:border-terminal-accent/30 disabled:opacity-30 disabled:cursor-not-allowed transition-all text-[10px]"
                  >
                    ‹
                  </button>
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                    <button
                      key={p}
                      onClick={() => setPage(p)}
                      className={clsx(
                        "h-5 min-w-[20px] px-1 rounded border font-mono text-[10px] transition-all",
                        p === page
                          ? "border-terminal-accent/50 bg-terminal-accent/10 text-terminal-accent"
                          : "border-terminal-border text-terminal-muted hover:text-terminal-text hover:border-terminal-accent/30"
                      )}
                    >
                      {p}
                    </button>
                  ))}
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="h-5 w-5 flex items-center justify-center rounded border border-terminal-border text-terminal-muted hover:text-terminal-text hover:border-terminal-accent/30 disabled:opacity-30 disabled:cursor-not-allowed transition-all text-[10px]"
                  >
                    ›
                  </button>
                </div>
              </div>
            );
          })()}
        </div>
      )}
    </section>
  );
}

// ─── Pipeline Actions ──────────────────────────────────────────────────────────



function PipelineActions() {
  const [state, setState] = useState<{ queuedSymbols: string[] }>({ queuedSymbols: [] });
  const [input, setInput] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [allSymbols, setAllSymbols] = useState<string[]>([]);

  // Load tracked symbols for autocomplete
  useEffect(() => {
    trackedSymbolsApi.list().then((syms) => setAllSymbols(syms));
  }, []);

  // Auto-suggest while typing — filter from fetched symbols
  const handleInput = (val: string) => {
    setInput(val);
    if (val.trim().length > 0) {
      const q = val.toUpperCase();
      setSuggestions(allSymbols.filter((s) => s.startsWith(q) && !state.queuedSymbols.includes(s)));
    } else {
      setSuggestions([]);
    }
  };

  const addSymbol = (sym: string) => {
    const s = sym.toUpperCase().trim();
    if (!s || state.queuedSymbols.includes(s) || seedState.phase === "running" || synthState.phase === "running") return;
    setState((prev) => ({ ...prev, queuedSymbols: [...prev.queuedSymbols, s] }));
    setInput("");
    setSuggestions([]);
  };

  const removeSymbol = (sym: string) => {
    if (seedState.phase === "running" || synthState.phase === "running") return;
    setState((prev) => ({ ...prev, queuedSymbols: prev.queuedSymbols.filter((s) => s !== sym) }));
  };

  // Track seed and synth separately, show as one unified pipeline
  const [seedState, setSeedState] = useState<{ phase: string; progress: number; currentSymbol: string | null; totalSymbols: number; processedSymbols: number; message: string; errors: string[] }>({ phase: "idle", progress: 0, currentSymbol: null, totalSymbols: 0, processedSymbols: 0, message: "Ready", errors: [] });
  const [synthState, setSynthState] = useState<{ phase: string; progress: number; currentSymbol: string | null; totalSymbols: number; processedSymbols: number; message: string; errors: string[] }>({ phase: "idle", progress: 0, currentSymbol: null, totalSymbols: 0, processedSymbols: 0, message: "Ready", errors: [] });

  // Unified phase derived from both
  const unifiedPhase: PipelinePhase =
    seedState.phase === "running" ? "seed" :
    synthState.phase === "running" ? "synth" :
    seedState.phase === "done" && synthState.phase === "idle" ? "seed" :
    synthState.phase === "done" ? "done" :
    seedState.phase === "error" || synthState.phase === "error" ? "error" :
    "idle";

  const unifiedProgress = unifiedPhase === "seed" ? seedState.progress : unifiedPhase === "synth" ? synthState.progress : unifiedPhase === "done" ? 1 : 0;
  const unifiedSymbol = unifiedPhase === "seed" ? seedState.currentSymbol : synthState.currentSymbol;
  const unifiedTotal = unifiedPhase === "seed" ? seedState.totalSymbols : synthState.totalSymbols;
  const unifiedProcessed = unifiedPhase === "seed" ? seedState.processedSymbols : synthState.processedSymbols;
  const unifiedMessage = unifiedPhase === "seed" ? seedState.message : synthState.message;
  const unifiedErrors = [...seedState.errors, ...synthState.errors];

  const handleProgress = useCallback((data: PipelineProgress) => {
    const sPhase = data.phase;
    const isSeed = data.task === "seed";
    const setFn = isSeed ? setSeedState : setSynthState;

    if (sPhase === "running") {
      setFn({ phase: "running", progress: data.progress ?? 0, currentSymbol: data.current_symbol ?? null, totalSymbols: data.total_symbols ?? 0, processedSymbols: data.processed_symbols ?? 0, message: data.message ?? "", errors: data.errors ?? [] });
    } else if (sPhase === "done") {
      setFn((prev) => ({ ...prev, phase: "done", progress: 1, processedSymbols: prev.totalSymbols }));
    } else if (sPhase === "error") {
      setFn((prev) => ({ ...prev, phase: "error", message: data.message ?? "Unknown error", errors: data.errors ?? [] }));
    } else if (sPhase === "idle") {
      setFn((prev) => ({ ...prev, phase: "idle" }));
    }
  }, []);

  const isRunning = unifiedPhase === "seed" || unifiedPhase === "synth";
  const isDone = unifiedPhase === "done";
  const isError = unifiedPhase === "error";

  // SSE for live progress
  useEffect(() => {
    const es = createProgressSSE(handleProgress);
    return () => es.close();
  }, [handleProgress]);

  const runPipeline = async () => {
    if (state.queuedSymbols.length === 0) return;
    setSeedState({ phase: "idle", progress: 0, currentSymbol: null, totalSymbols: 0, processedSymbols: 0, message: "Ready", errors: [] });
    setSynthState({ phase: "idle", progress: 0, currentSymbol: null, totalSymbols: 0, processedSymbols: 0, message: "Ready", errors: [] });
    try {
      await trackedSymbolsApi.triggerSeedForSymbols(state.queuedSymbols);
    } catch {
      setSeedState((p) => ({ ...p, phase: "error", message: "Seed request failed", errors: ["Seed request failed"] }));
    }
  };

  const phaseLabel =
    unifiedPhase === "seed" ? "Seeding prices" :
    unifiedPhase === "synth" ? "Synthesizing wiki" :
    unifiedPhase === "done" ? "Complete" :
    unifiedPhase === "error" ? "Failed" : "Ready";

  const pct = Math.round(unifiedProgress * 100);

  return (
    <section>
      <div className="flex items-center justify-between mb-2">
        <span className="font-mono text-[10px] text-terminal-muted tracking-widest uppercase">
          Pipeline Queue
        </span>
        <span className={clsx(
          "font-mono text-[10px] px-1.5 py-0.5 rounded border",
          unifiedPhase === "idle" && "border-terminal-border text-terminal-muted",
          unifiedPhase === "seed" && "border-terminal-amber/30 text-terminal-amber",
          unifiedPhase === "synth" && "border-terminal-accent/30 text-terminal-accent",
          unifiedPhase === "done" && "border-terminal-green/30 text-terminal-green",
          unifiedPhase === "error" && "border-terminal-red/30 text-terminal-red",
        )}>
          {phaseLabel}
        </span>
      </div>

      {/* Symbol input */}
      <div className="relative mb-2">
        <div className="flex items-center gap-1.5">
          <div className="relative flex-1">
            <input
              value={input}
              onChange={(e) => handleInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && input.trim()) { e.preventDefault(); addSymbol(input); }
              }}
              placeholder="ADD SYMBOL…"
              maxLength={10}
              disabled={isRunning}
              className="w-full bg-terminal-bg border border-terminal-border rounded px-2.5 py-1.5 pr-16 font-mono text-xs text-terminal-text placeholder:text-terminal-muted/40 focus:outline-none focus:border-terminal-accent/50 disabled:opacity-40 transition-colors uppercase"
            />
            {input && (
              <button
                onClick={() => addSymbol(input)}
                disabled={isRunning}
                className="absolute right-1.5 top-1/2 -translate-y-1/2 h-5 w-5 rounded bg-terminal-accent/10 border border-terminal-accent/30 flex items-center justify-center hover:bg-terminal-accent/20 disabled:opacity-30 transition-all"
              >
                <Plus className="h-3 w-3 text-terminal-accent" />
              </button>
            )}
          </div>
        </div>

        {/* Autocomplete dropdown */}
        {suggestions.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-1 rounded border border-terminal-border bg-terminal-surface z-20 shadow-lg overflow-hidden">
            {suggestions.slice(0, 6).map((s) => (
              <button key={s} onClick={() => addSymbol(s)} className="w-full px-3 py-1.5 font-mono text-xs text-terminal-text hover:bg-terminal-accent/10 hover:text-terminal-accent text-left uppercase transition-colors">
                {s}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Symbol chips */}
      {state.queuedSymbols.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {state.queuedSymbols.map((sym) => (
            <span key={sym} className="inline-flex items-center gap-1 rounded border border-terminal-border bg-terminal-surface px-1.5 py-0.5 font-mono text-[10px] text-terminal-text group">
              {sym}
              {!isRunning && (
                <button onClick={() => removeSymbol(sym)} className="opacity-0 group-hover:opacity-100 transition-opacity">
                  <Trash2 className="h-2.5 w-2.5 text-terminal-red/60 hover:text-terminal-red" />
                </button>
              )}
            </span>
          ))}
        </div>
      )}

      {/* Run button */}
      <button
        onClick={runPipeline}
        disabled={state.queuedSymbols.length === 0 || isRunning}
        className={clsx(
          "w-full rounded border py-2 px-4 font-mono text-[11px] font-semibold uppercase tracking-wider transition-all flex items-center justify-center gap-2",
          state.queuedSymbols.length > 0 && !isRunning
            ? "border-terminal-accent/40 text-terminal-accent hover:bg-terminal-accent/10 hover:border-terminal-accent/70"
            : "border-terminal-border text-terminal-muted cursor-not-allowed opacity-40",
        )}
      >
        {isRunning ? (
          <>
            <RefreshCw className="h-3.5 w-3.5 animate-spin" />
            {unifiedPhase === "seed" ? "Seeding…" : "Synthesizing…"}
          </>
        ) : (
          <>
            <Zap className="h-3.5 w-3.5" />
            Run Pipeline
          </>
        )}
      </button>

      {/* Progress bar */}
      {isRunning && (
        <div className="mt-2 space-y-1">
          <div className="relative h-1 w-full rounded-full bg-terminal-border overflow-hidden">
            <div className="absolute left-0 top-0 h-full rounded-full bg-terminal-accent transition-all duration-500 ease-out" style={{ width: `${pct}%` }} />
          </div>
          {unifiedSymbol && (
            <p className="font-mono text-[10px] text-terminal-text">
              &gt; {unifiedSymbol}
              <span className="text-terminal-muted ml-2">({unifiedProcessed}/{unifiedTotal})</span>
            </p>
          )}
          <p className="font-mono text-[10px] text-terminal-muted">{unifiedMessage}</p>
        </div>
      )}

      {/* Done banner */}
      {isDone && (
        <div className="mt-2 rounded border border-terminal-green/20 bg-terminal-green/5 p-2 flex items-center gap-2">
          <CheckCircle2 className="h-3.5 w-3.5 text-terminal-green flex-shrink-0" />
          <div>
            <p className="font-mono text-[10px] text-terminal-green">
              {state.queuedSymbols.length} symbols seeded &amp; synthesized
            </p>
            <button onClick={() => { setState({ queuedSymbols: [] }); setSeedState((p) => ({ ...p, phase: "idle" })); setSynthState((p) => ({ ...p, phase: "idle" })); }} className="font-mono text-[10px] text-terminal-green/60 hover:text-terminal-green underline mt-0.5">
              Clear queue
            </button>
          </div>
        </div>
      )}

      {/* Error banner */}
      {isError && (
        <div className="mt-2 rounded border border-terminal-red/20 bg-terminal-red/5 p-2">
          <div className="flex items-center gap-2 mb-1">
            <AlertCircle className="h-3.5 w-3.5 text-terminal-red flex-shrink-0" />
            <p className="font-mono text-[10px] text-terminal-red">{unifiedMessage || "Pipeline failed"}</p>
          </div>
          <button onClick={() => { setState((p) => ({ ...p, phase: "idle" })); setSeedState((p) => ({ ...p, phase: "idle" })); setSynthState((p) => ({ ...p, phase: "idle" })); }} className="font-mono text-[10px] text-terminal-red/60 hover:text-terminal-red underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Error log */}
      {unifiedErrors.length > 0 && (
        <div className="mt-2 rounded border border-terminal-red/20 bg-terminal-red/5 p-2 space-y-0.5">
          {unifiedErrors.slice(0, 5).map((e, i) => (
            <p key={i} className="font-mono text-[10px] text-terminal-red/70">&gt; {e}</p>
          ))}
        </div>
      )}
    </section>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function AdminPage() {
  const [mounted, setMounted] = useState(false);

  // Shared tracked symbols — used by WikiSection (filter) and TrackedSymbolsSection (refresh)
  const [trackedSymbols, setTrackedSymbols] = useState<string[]>([]);
  const loadTrackedSymbols = useCallback(async () => {
    try {
      const data = await trackedSymbolsApi.list();
      setTrackedSymbols(data);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { setMounted(true); loadTrackedSymbols(); }, [loadTrackedSymbols]);

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
            <TrackedSymbolsSection
              symbols={trackedSymbols}
              onRemove={(sym) => setTrackedSymbols((prev) => prev.filter((s) => s !== sym))}
              onAdd={(sym) => setTrackedSymbols((prev) => [...prev, sym])}
            />
          </div>

          {/* Right column — wiki + actions */}
          <div className="col-span-7 space-y-5">
            <WikiSection trackedSymbols={trackedSymbols} />
            <PipelineActions />
            <PipelineHistorySection />
          </div>
        </div>
      </div>
    </div>
  );
}
