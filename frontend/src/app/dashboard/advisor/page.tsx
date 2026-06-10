"use client";

import { useMemo, useState } from "react";
import {
  Activity,
  ArrowUpRight,
  BarChart3,
  Bot,
  BrainCircuit,
  CircleDollarSign,
  CornerDownLeft,
  Radio,
  RotateCcw,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
import { AgentThoughtStream } from "@/components/advisor/AgentThoughtStream";
import { useSSE } from "@/hooks/useSSE";

const promptGroups = [
  {
    icon: BarChart3,
    label: "Market pulse",
    prompt: "Summarize today's market trend and identify the strongest sectors.",
  },
  {
    icon: ShieldAlert,
    label: "Risk scan",
    prompt: "Review my portfolio concentration and highlight the main risks.",
  },
  {
    icon: CircleDollarSign,
    label: "Stock thesis",
    prompt: "Build a concise investment thesis for VNM with risks and catalysts.",
  },
];

export default function AdvisorPage() {
  const [message, setMessage] = useState("");
  const [submittedMessage, setSubmittedMessage] = useState("");
  const [session, setSession] = useState(0);
  const endpoint = submittedMessage
    ? `/advisor/chat/stream?session=${session}`
    : null;
  const events = useSSE(endpoint);

  const status = useMemo(() => {
    if (!submittedMessage) return "standby";
    if (events.some((event) => event.type === "error")) return "error";
    if (events.some((event) => event.type === "answer")) return "complete";
    return "processing";
  }, [events, submittedMessage]);

  const handleSend = () => {
    const nextMessage = message.trim();
    if (!nextMessage) return;

    setSubmittedMessage(nextMessage);
    setMessage("");
    setSession((value) => value + 1);
  };

  const resetSession = () => {
    setSubmittedMessage("");
    setMessage("");
    setSession((value) => value + 1);
  };

  return (
    <div
      className="min-h-full bg-terminal-bg font-mono text-terminal-text"
      style={{
        fontFamily: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
      }}
    >
      <header className="mb-5 flex flex-col gap-4 border-b border-terminal-border pb-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.22em] text-terminal-muted">
            <span className="h-1.5 w-1.5 rounded-full bg-terminal-green" />
            Intelligence workspace
          </div>
          <h1 className="font-display text-xl font-bold uppercase tracking-[0.16em] text-terminal-accent">
            AI Advisor
          </h1>
          <p className="mt-1 max-w-2xl text-xs leading-relaxed text-terminal-muted">
            Market research, portfolio context, and risk analysis in one
            traceable decision stream.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 rounded border border-terminal-border bg-terminal-surface px-2 py-1 text-[10px] uppercase tracking-wider text-terminal-muted">
            <Radio className="h-3 w-3 text-terminal-green" />
            Live context
          </span>
          <button
            type="button"
            onClick={resetSession}
            disabled={!submittedMessage}
            className="inline-flex items-center gap-1.5 rounded border border-terminal-border px-2 py-1 text-[10px] uppercase tracking-wider text-terminal-muted transition-colors hover:border-terminal-accent/40 hover:text-terminal-accent disabled:cursor-not-allowed disabled:opacity-30"
          >
            <RotateCcw className="h-3 w-3" />
            New session
          </button>
        </div>
      </header>

      <div className="grid min-h-[calc(100vh-11.5rem)] grid-cols-1 gap-5 xl:grid-cols-12">
        <aside className="order-2 space-y-5 xl:order-1 xl:col-span-4">
          <section>
            <SectionTitle
              icon={Sparkles}
              title="Research prompts"
              subtitle="Start with a focused mandate"
            />
            <div className="space-y-1.5">
              {promptGroups.map(({ icon: Icon, label, prompt }, index) => (
                <button
                  key={label}
                  type="button"
                  onClick={() => setMessage(prompt)}
                  className="group flex w-full items-start gap-3 rounded border border-terminal-border bg-terminal-surface px-3 py-3 text-left transition-colors hover:border-terminal-accent/40 hover:bg-terminal-accent/5"
                >
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded border border-terminal-border bg-terminal-bg text-terminal-muted transition-colors group-hover:border-terminal-accent/30 group-hover:text-terminal-accent">
                    <Icon className="h-3.5 w-3.5" />
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="flex items-center justify-between">
                      <span className="text-[10px] font-semibold uppercase tracking-widest text-terminal-text">
                        {label}
                      </span>
                      <span className="text-[9px] text-terminal-muted">
                        0{index + 1}
                      </span>
                    </span>
                    <span className="mt-1 block text-[10px] leading-relaxed text-terminal-muted">
                      {prompt}
                    </span>
                  </span>
                  <ArrowUpRight className="mt-0.5 h-3 w-3 shrink-0 text-terminal-muted transition-colors group-hover:text-terminal-accent" />
                </button>
              ))}
            </div>
          </section>

          <section>
            <SectionTitle
              icon={Activity}
              title="Session telemetry"
              subtitle="Current analysis state"
            />
            <div className="grid grid-cols-3 gap-1.5">
              <TelemetryItem label="Status" value={status} state={status} />
              <TelemetryItem
                label="Steps"
                value={String(events.filter((event) => event.type === "thought").length).padStart(2, "0")}
              />
              <TelemetryItem
                label="Output"
                value={events.some((event) => event.type === "answer") ? "READY" : "—"}
              />
            </div>
            <div className="mt-1.5 rounded border border-terminal-border bg-terminal-surface px-3 py-2.5">
              <p className="text-[9px] uppercase tracking-widest text-terminal-muted">
                Scope
              </p>
              <p className="mt-1 text-[10px] leading-relaxed text-terminal-text">
                Educational analysis only. Validate market data and risk
                assumptions before making a trade.
              </p>
            </div>
          </section>
        </aside>

        <section className="order-1 flex min-h-[570px] flex-col overflow-hidden rounded border border-terminal-border bg-terminal-surface xl:order-2 xl:col-span-8">
          <div className="flex items-center justify-between border-b border-terminal-border px-4 py-3">
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded border border-terminal-accent/30 bg-terminal-accent/5">
                <BrainCircuit className="h-4 w-4 text-terminal-accent" />
              </div>
              <div>
                <h2 className="text-xs font-semibold uppercase tracking-widest text-terminal-text">
                  Analysis stream
                </h2>
                <p className="text-[10px] text-terminal-muted">
                  Agent reasoning and final response
                </p>
              </div>
            </div>
            <StatusBadge status={status} />
          </div>

          <div className="flex-1 overflow-y-auto bg-terminal-bg/60 p-4">
            {!submittedMessage ? (
              <div className="flex h-full min-h-[360px] items-center justify-center">
                <div className="max-w-sm text-center">
                  <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded border border-terminal-border bg-terminal-surface">
                    <Bot className="h-5 w-5 text-terminal-accent" />
                  </div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-terminal-text">
                    Awaiting research brief
                  </p>
                  <p className="mt-2 text-[10px] leading-relaxed text-terminal-muted">
                    Ask about a stock, market regime, portfolio exposure, or
                    select a structured prompt from the research panel.
                  </p>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="ml-auto max-w-[88%] rounded border border-terminal-accent/30 bg-terminal-accent/5 px-3 py-2.5">
                  <div className="mb-1 flex items-center justify-between gap-4">
                    <span className="text-[9px] font-semibold uppercase tracking-widest text-terminal-accent">
                      Research brief
                    </span>
                    <span className="text-[9px] text-terminal-muted">USER</span>
                  </div>
                  <p className="whitespace-pre-wrap text-xs leading-relaxed text-terminal-text">
                    {submittedMessage}
                  </p>
                </div>

                {events.map((event, index) => (
                  <AgentThoughtStream key={`${session}-${index}`} event={event} />
                ))}

                {status === "processing" && (
                  <div className="flex items-center gap-2 px-1 py-2 text-[10px] uppercase tracking-widest text-terminal-muted">
                    <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-terminal-amber" />
                    Advisor is processing the brief
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="border-t border-terminal-border bg-terminal-surface p-3">
            <div className="flex items-end gap-2 rounded border border-terminal-border bg-terminal-bg p-1.5 transition-colors focus-within:border-terminal-accent/50">
              <textarea
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    handleSend();
                  }
                }}
                rows={2}
                className="max-h-32 min-h-[44px] flex-1 resize-none bg-transparent px-2 py-1.5 text-xs leading-relaxed text-terminal-text outline-none placeholder:text-terminal-muted/50"
                placeholder="Enter a stock, market, or portfolio research question..."
                aria-label="Advisor research question"
              />
              <button
                type="button"
                onClick={handleSend}
                disabled={!message.trim()}
                className="flex h-9 items-center gap-2 rounded border border-terminal-accent/40 bg-terminal-accent/10 px-3 text-[10px] font-semibold uppercase tracking-wider text-terminal-accent transition-colors hover:border-terminal-accent/70 hover:bg-terminal-accent/20 disabled:cursor-not-allowed disabled:border-terminal-border disabled:bg-transparent disabled:text-terminal-muted disabled:opacity-40"
              >
                Analyze
                <CornerDownLeft className="h-3 w-3" />
              </button>
            </div>
            <div className="mt-2 flex items-center justify-between px-1 text-[9px] uppercase tracking-wider text-terminal-muted">
              <span>Enter to send · Shift + Enter for newline</span>
              <span>Context-aware session</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

function SectionTitle({
  icon: Icon,
  title,
  subtitle,
}: {
  icon: React.ElementType;
  title: string;
  subtitle: string;
}) {
  return (
    <div className="mb-3 flex items-center gap-3 border-b border-terminal-border pb-3">
      <div className="flex h-8 w-8 items-center justify-center rounded border border-terminal-border bg-terminal-surface">
        <Icon className="h-4 w-4 text-terminal-accent" />
      </div>
      <div>
        <h2 className="text-xs font-semibold uppercase tracking-widest text-terminal-text">
          {title}
        </h2>
        <p className="text-[10px] text-terminal-muted">{subtitle}</p>
      </div>
    </div>
  );
}

function TelemetryItem({
  label,
  value,
  state,
}: {
  label: string;
  value: string;
  state?: string;
}) {
  const valueColor =
    state === "error"
      ? "text-terminal-red"
      : state === "complete"
        ? "text-terminal-green"
        : state === "processing"
          ? "text-terminal-amber"
          : "text-terminal-text";

  return (
    <div className="rounded border border-terminal-border bg-terminal-surface px-2 py-2.5">
      <p className="text-[9px] uppercase tracking-wider text-terminal-muted">
        {label}
      </p>
      <p className={`mt-1 truncate text-[10px] font-semibold uppercase ${valueColor}`}>
        {value}
      </p>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const classes =
    status === "error"
      ? "border-terminal-red/30 bg-terminal-red/5 text-terminal-red"
      : status === "complete"
        ? "border-terminal-green/30 bg-terminal-green/5 text-terminal-green"
        : status === "processing"
          ? "border-terminal-amber/30 bg-terminal-amber/5 text-terminal-amber"
          : "border-terminal-border bg-terminal-bg text-terminal-muted";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded border px-2 py-1 text-[9px] font-medium uppercase tracking-widest ${classes}`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          status === "processing" ? "animate-pulse bg-terminal-amber" : "bg-current"
        }`}
      />
      {status}
    </span>
  );
}
