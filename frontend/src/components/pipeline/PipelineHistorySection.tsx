"use client";

import { useState, useEffect, useCallback } from "react";
import {
  History,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Clock,
  CheckCircle2,
  AlertCircle,
  XCircle,
  Timer,
  Database,
  BookOpen,
  Radio,
  Zap,
  Filter,
} from "lucide-react";
import { clsx } from "clsx";
import { pipelineRunsApi } from "@/lib/api";
import type { PipelineRun, PipelineRunDetail, PipelineRunType, PipelineRunStatus } from "@/lib/types";

// ─── Icon map ─────────────────────────────────────────────────────────────────

const RUN_TYPE_ICONS: Record<PipelineRunType, React.ElementType> = {
  seed: Database,
  synthesis: BookOpen,
  stream_a: Radio,
  stream_b: Radio,
  stream_c: Zap,
};

const RUN_TYPE_LABELS: Record<PipelineRunType, string> = {
  seed: "Seed",
  synthesis: "Synthesis",
  stream_a: "Stream A",
  stream_b: "Stream B",
  stream_c: "Stream C",
};

const STATUS_CONFIG: Record<
  PipelineRunStatus,
  { label: string; color: string; bg: string; border: string }
> = {
  success: {
    label: "success",
    color: "text-terminal-green",
    bg: "bg-terminal-green/10",
    border: "border-terminal-green/30",
  },
  partial: {
    label: "partial",
    color: "text-terminal-amber",
    bg: "bg-terminal-amber/10",
    border: "border-terminal-amber/30",
  },
  failed: {
    label: "failed",
    color: "text-terminal-red",
    bg: "bg-terminal-red/10",
    border: "border-terminal-red/30",
  },
  running: {
    label: "running",
    color: "text-terminal-amber",
    bg: "bg-terminal-amber/10",
    border: "border-terminal-amber/30",
  },
};

const TRIGGER_LABELS: Record<string, string> = {
  scheduled: "SCHED",
  api: "API",
  manual: "MANUAL",
};

// ─── Formatting helpers ─────────────────────────────────────────────────────────

function formatDuration(seconds: number | null): string {
  if (seconds === null) return "—";
  if (seconds < 60) return `${seconds}s`;
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return s > 0 ? `${m}m ${s}s` : `${m}m`;
}

function formatRelativeTime(isoStr: string): string {
  if (!isoStr) return "—";
  const then = new Date(isoStr).getTime();
  const now = Date.now();
  const diff = Math.floor((now - then) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

function formatDateTime(isoStr: string): string {
  if (!isoStr) return "—";
  return new Date(isoStr).toLocaleString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

// ─── Run Type Filter ───────────────────────────────────────────────────────────

const ALL_RUN_TYPES: Array<{ value: string; label: string }> = [
  { value: "", label: "All" },
  { value: "seed", label: "Seed" },
  { value: "synthesis", label: "Synthesis" },
  { value: "stream_a", label: "Stream A" },
  { value: "stream_b", label: "Stream B" },
];

// ─── Stats bar ─────────────────────────────────────────────────────────────────

function RunStatsBar({ runs }: { runs: PipelineRun[] }) {
  const total = runs.length;
  const success = runs.filter((r) => r.status === "success").length;
  const partial = runs.filter((r) => r.status === "partial").length;
  const failed = runs.filter((r) => r.status === "failed").length;
  const avgDuration =
    runs.length > 0
      ? Math.round(runs.reduce((s, r) => s + (r.duration_seconds ?? 0), 0) / runs.filter((r) => r.duration_seconds !== null).length) || 0
      : 0;

  const statItems = [
    { label: "Total", value: total, color: "text-terminal-text" },
    { label: "OK", value: success, color: "text-terminal-green" },
    { label: "Partial", value: partial, color: "text-terminal-amber" },
    { label: "Failed", value: failed, color: "text-terminal-red" },
    { label: "Avg", value: formatDuration(avgDuration), color: "text-terminal-muted" },
  ];

  return (
    <div className="flex items-center gap-4 px-3 py-2 bg-terminal-surface border border-terminal-border rounded">
      {statItems.map(({ label, value, color }) => (
        <div key={label} className="flex items-center gap-1.5">
          <span className={clsx("font-mono text-xs font-semibold", color)}>{value}</span>
          <span className="font-mono text-[10px] text-terminal-muted uppercase tracking-wider">{label}</span>
        </div>
      ))}
    </div>
  );
}

// ─── Run Detail Row ─────────────────────────────────────────────────────────────

function RunDetail({ run }: { run: PipelineRun }) {
  const [expanded, setExpanded] = useState(false);
  const [detail, setDetail] = useState<PipelineRunDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const statusCfg = STATUS_CONFIG[run.status as PipelineRunStatus] ?? STATUS_CONFIG.failed;
  const RunIcon = RUN_TYPE_ICONS[run.run_type as PipelineRunType] ?? Zap;
  const typeLabel = RUN_TYPE_LABELS[run.run_type as PipelineRunType] ?? run.run_type;
  const triggerLabel = TRIGGER_LABELS[run.trigger_type] ?? run.trigger_type;

  const loadDetail = useCallback(async () => {
    if (detail) return;
    setLoadingDetail(true);
    try {
      const d = await pipelineRunsApi.detail(run.id);
      setDetail(d);
    } catch {
      // ignore
    } finally {
      setLoadingDetail(false);
    }
  }, [run.id, detail]);

  const toggle = async () => {
    setExpanded((v) => !v);
    if (!expanded && !detail) {
      await loadDetail();
    }
  };

  return (
    <div className="border border-terminal-border rounded overflow-hidden bg-terminal-surface">
      {/* Main row */}
      <button
        onClick={toggle}
        className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-terminal-border/20 transition-colors text-left"
      >
        {/* Run type icon */}
        <RunIcon
          className={clsx(
            "h-3.5 w-3.5 flex-shrink-0",
            run.run_type === "seed" && "text-terminal-blue",
            run.run_type === "synthesis" && "text-terminal-purple",
            run.run_type === "stream_a" && "text-terminal-green",
            run.run_type === "stream_b" && "text-terminal-amber",
          )}
        />

        {/* Type badge */}
        <span className="font-mono text-[10px] font-bold tracking-widest uppercase text-terminal-muted w-16 flex-shrink-0">
          {typeLabel}
        </span>

        {/* Trigger */}
        <span className="font-mono text-[9px] px-1 py-0.5 rounded border border-terminal-border text-terminal-muted flex-shrink-0">
          {triggerLabel}
        </span>

        {/* Status pill */}
        <span
          className={clsx(
            "font-mono text-[9px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded border flex-shrink-0",
            statusCfg.color,
            statusCfg.bg,
            statusCfg.border,
          )}
        >
          {statusCfg.label}
        </span>

        {/* Stats */}
        <div className="flex items-center gap-3 flex-1 min-w-0">
          {run.symbols_requested !== null && (
            <span className="font-mono text-[10px] text-terminal-muted flex-shrink-0">
              <span className="text-terminal-text font-semibold">{run.symbols_requested}</span>
              {run.symbols_processed !== null && run.symbols_processed < run.symbols_requested && (
                <span className="text-terminal-amber ml-0.5">
                  /{run.symbols_requested}
                </span>
              )}
            </span>
          )}
          {run.duration_seconds !== null && (
            <span className="flex items-center gap-0.5 font-mono text-[10px] text-terminal-muted flex-shrink-0">
              <Timer className="h-2.5 w-2.5" />
              {formatDuration(run.duration_seconds)}
            </span>
          )}
        </div>

        {/* Time */}
        <span className="font-mono text-[10px] text-terminal-muted flex-shrink-0 hidden sm:block">
          {formatDateTime(run.started_at)}
        </span>
        <span className="font-mono text-[9px] text-terminal-muted flex-shrink-0 sm:hidden">
          {formatRelativeTime(run.started_at)}
        </span>

        {/* Expand chevron */}
        <div className="flex-shrink-0">
          {expanded ? (
            <ChevronUp className="h-3 w-3 text-terminal-muted" />
          ) : (
            <ChevronDown className="h-3 w-3 text-terminal-muted" />
          )}
        </div>
      </button>

      {/* Expanded detail */}
      {expanded && (
        <div className="border-t border-terminal-border bg-terminal-bg px-3 py-3 space-y-2">
          {/* Timeline */}
          <div className="flex items-center gap-3 text-[10px] font-mono text-terminal-muted">
            <span>started {formatDateTime(run.started_at)}</span>
            {run.finished_at && (
              <>
                <span className="text-terminal-border">→</span>
                <span>finished {formatDateTime(run.finished_at)}</span>
              </>
            )}
            {run.duration_seconds !== null && (
              <>
                <span className="text-terminal-border">→</span>
                <span>duration {formatDuration(run.duration_seconds)}</span>
              </>
            )}
          </div>

          {/* Symbol results */}
          {loadingDetail ? (
            <div className="flex items-center gap-2">
              <RefreshCw className="h-3 w-3 animate-spin text-terminal-muted" />
              <span className="font-mono text-[10px] text-terminal-muted">Loading symbol results…</span>
            </div>
          ) : detail && detail.symbols_detail.length > 0 ? (
            <div>
              <p className="font-mono text-[9px] text-terminal-muted uppercase tracking-wider mb-1.5">
                Symbol Results
                <span className="ml-2 text-terminal-accent/60">
                  {detail.symbols_detail.filter((s) => s.status === "success").length} ok
                  {detail.symbols_detail.filter((s) => s.status === "error").length > 0 && (
                    <span className="text-terminal-red/60 ml-1">
                      / {detail.symbols_detail.filter((s) => s.status === "error").length} errors
                    </span>
                  )}
                </span>
              </p>
              <div className="flex flex-wrap gap-1">
                {detail.symbols_detail.map((sym) => (
                  <span
                    key={sym.symbol}
                    className={clsx(
                      "inline-flex items-center gap-1 font-mono text-[10px] px-1.5 py-0.5 rounded border",
                      sym.status === "success"
                        ? "border-terminal-green/20 bg-terminal-green/5 text-terminal-green/80"
                        : "border-terminal-red/20 bg-terminal-red/5 text-terminal-red/80",
                    )}
                    title={sym.error_message ?? undefined}
                  >
                    {sym.status === "success" ? (
                      <CheckCircle2 className="h-2.5 w-2.5 flex-shrink-0" />
                    ) : (
                      <XCircle className="h-2.5 w-2.5 flex-shrink-0" />
                    )}
                    {sym.symbol}
                  </span>
                ))}
              </div>
            </div>
          ) : (
            <p className="font-mono text-[10px] text-terminal-muted">No symbol-level data available.</p>
          )}

          {/* Errors */}
          {run.errors.length > 0 && (
            <div>
              <p className="font-mono text-[9px] text-terminal-red/80 uppercase tracking-wider mb-1">
                Pipeline Errors
              </p>
              <div className="space-y-0.5">
                {run.errors.map((err, i) => (
                  <p key={i} className="font-mono text-[10px] text-terminal-red/70 leading-relaxed">
                    <span className="text-terminal-red/40">! </span>
                    {err.length > 120 ? err.slice(0, 120) + "…" : err}
                  </p>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Main section ───────────────────────────────────────────────────────────────

export function PipelineHistorySection() {
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [total, setTotal] = useState(0);
  const PAGE_SIZE = 5;
  const [page, setPage] = useState(1);

  const load = useCallback(async () => {
    try {
      const params: Parameters<typeof pipelineRunsApi.list>[0] = { limit: PAGE_SIZE, offset: (page - 1) * PAGE_SIZE };
      if (filterType) params.run_type = filterType;
      if (filterStatus) params.status = filterStatus;
      const data = await pipelineRunsApi.list(params);
      setRuns(data.runs ?? data);
      setTotal(data.total ?? 0);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, [filterType, filterStatus, page]);

  useEffect(() => {
    setPage(1);
    setLoading(true);
  }, [filterType, filterStatus]);

  useEffect(() => {
    load();
  }, [load]);

  const refresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const pageNumbers = Array.from({ length: totalPages }, (_, i) => i + 1)
    .filter(
      (p) =>
        p === 1 ||
        p === totalPages ||
        Math.abs(p - page) <= 1
    )
    .reduce<number[]>((acc, p, _, arr) => {
      if (acc.length && p - acc[acc.length - 1] > 1) acc.push(-1);
      acc.push(p);
      return acc;
    }, []);

  return (
    <section>
      {/* Header */}
      <div className="flex items-center justify-between border-b border-terminal-border pb-3 mb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded border border-terminal-border bg-terminal-surface">
            <History className="h-4 w-4 text-terminal-accent" />
          </div>
          <div>
            <h2 className="font-mono text-sm font-semibold tracking-widest uppercase text-terminal-text">
              Run History
            </h2>
            <p className="font-mono text-xs text-terminal-muted">
              {total > 0 ? `${total} total runs` : "No runs recorded"}
            </p>
          </div>
        </div>
        <button
          onClick={refresh}
          disabled={refreshing}
          className="flex items-center gap-1.5 rounded border border-terminal-border px-2 py-1.5 font-mono text-[10px] font-medium text-terminal-muted hover:text-terminal-text hover:border-terminal-accent/30 transition-all disabled:opacity-50"
        >
          <RefreshCw className={clsx("h-3 w-3", refreshing && "animate-spin")} />
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2 mb-3">
        <Filter className="h-3 w-3 text-terminal-muted flex-shrink-0" />
        <div className="flex gap-1">
          {ALL_RUN_TYPES.map(({ value, label }) => (
            <button
              key={value}
              onClick={() => setFilterType(value)}
              className={clsx(
                "font-mono text-[10px] px-2 py-1 rounded border transition-all",
                filterType === value
                  ? "border-terminal-accent/40 bg-terminal-accent/10 text-terminal-accent"
                  : "border-terminal-border bg-terminal-surface text-terminal-muted hover:border-terminal-border/80",
              )}
            >
              {label}
            </button>
          ))}
        </div>
        <div className="flex gap-1 ml-auto">
          {["", "success", "partial", "failed"].map((val) => (
            <button
              key={val}
              onClick={() => setFilterStatus(val)}
              className={clsx(
                "font-mono text-[10px] px-2 py-1 rounded border transition-all",
                filterStatus === val
                  ? val === "success"
                    ? "border-terminal-green/40 bg-terminal-green/10 text-terminal-green"
                    : val === "partial"
                    ? "border-terminal-amber/40 bg-terminal-amber/10 text-terminal-amber"
                    : val === "failed"
                    ? "border-terminal-red/40 bg-terminal-red/10 text-terminal-red"
                    : "border-terminal-accent/40 bg-terminal-accent/10 text-terminal-accent"
                  : "border-terminal-border bg-terminal-surface text-terminal-muted hover:border-terminal-border/80",
              )}
            >
              {val === "" ? "All" : val}
            </button>
          ))}
        </div>
      </div>

      {/* Stats bar */}
      {!loading && runs.length > 0 && <RunStatsBar runs={runs} />}

      {/* Pagination bar */}
      {!loading && totalPages > 1 && (
        <div className="flex items-center justify-between px-2 py-2 mt-2 border border-terminal-border rounded bg-terminal-surface">
          <span className="font-mono text-[10px] text-terminal-muted">
            {total} runs / page {page} of {totalPages}
          </span>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="h-5 w-5 flex items-center justify-center rounded border border-terminal-border text-terminal-muted hover:text-terminal-text hover:border-terminal-accent/30 disabled:opacity-30 disabled:cursor-not-allowed transition-all text-[10px]"
            >
              ‹
            </button>
            {pageNumbers.map((p, i) =>
              p === -1 ? (
                <span key={`ellipsis-${i}`} className="text-terminal-muted text-[10px] px-0.5">…</span>
              ) : (
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
              )
            )}
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="h-5 w-5 flex items-center justify-center rounded border border-terminal-border text-terminal-muted hover:text-terminal-text hover:border-terminal-accent/30 disabled:opacity-30 disabled:cursor-not-allowed transition-all text-[10px]"
            >
              ›
            </button>
          </div>
        </div>
      )}

      {/* Loading */}
      {loading ? (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-12 rounded bg-terminal-surface animate-pulse" />
          ))}
        </div>
      ) : runs.length === 0 ? (
        <div className="border border-terminal-border rounded bg-terminal-surface px-4 py-8 text-center">
          <Clock className="h-6 w-6 text-terminal-muted mx-auto mb-2" />
          <p className="font-mono text-xs text-terminal-muted">
            No pipeline runs recorded yet.
          </p>
          <p className="font-mono text-[10px] text-terminal-muted/60 mt-1">
            Runs appear here after executing seed, synthesis, or scheduled streams.
          </p>
        </div>
      ) : (
        <div className="space-y-1">
          {runs.map((run) => (
            <RunDetail key={run.id} run={run} />
          ))}
        </div>
      )}
    </section>
  );
}
