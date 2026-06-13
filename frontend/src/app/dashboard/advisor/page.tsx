"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { ElementType } from "react";
import {
  Activity,
  ArrowUpRight,
  BarChart3,
  Bot,
  BrainCircuit,
  CircleDollarSign,
  CornerDownLeft,
  MessageSquare,
  Plus,
  Radio,
  ShieldAlert,
  Sparkles,
  Trash2,
} from "lucide-react";
import { AgentThoughtStream } from "@/components/advisor/AgentThoughtStream";
import { useAuth } from "@/components/providers/AuthProvider";
import { advisorApi } from "@/lib/api";
import { normalizeAdvisorEnvelope } from "@/lib/sse";
import type { AdvisorMessage, AdvisorSession, SSEEnvelope, SSEEvent } from "@/lib/types";

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

type LocalMessage = Pick<AdvisorMessage, "id" | "role" | "content" | "createdAt"> & {
  sessionId: string;
  pending?: boolean;
};

const newLocalMessage = (role: "user" | "assistant", content: string, sessionId = ""): LocalMessage => ({
  id: `local-${role}-${Date.now()}-${Math.random().toString(16).slice(2)}`,
  role,
  content,
  createdAt: new Date().toISOString(),
  sessionId,
});

const storageKeyForUser = (userId: string) => `stockwise_advisor_active_session:${userId}`;

function formatSessionTime(value: string) {
  if (!value) return "--";
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export default function AdvisorPage() {
  const { user, isLoading: authLoading } = useAuth();
  const [message, setMessage] = useState("");
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [sessions, setSessions] = useState<AdvisorSession[]>([]);
  const [messages, setMessages] = useState<LocalMessage[]>([]);
  const [streamEvents, setStreamEvents] = useState<SSEEvent[]>([]);
  const [assistantDraft, setAssistantDraft] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const draftRef = useRef("");
  const finalReceivedRef = useRef(false);

  const activeSessionStorageKey = user ? storageKeyForUser(user.id) : null;

  const persistActiveSession = useCallback(
    (sessionId: string | null) => {
      if (!activeSessionStorageKey || typeof window === "undefined") return;
      if (sessionId) {
        localStorage.setItem(activeSessionStorageKey, sessionId);
      } else {
        localStorage.removeItem(activeSessionStorageKey);
      }
    },
    [activeSessionStorageKey]
  );

  const refreshSessions = useCallback(async () => {
    const list = await advisorApi.listSessions();
    setSessions(list);
    return list;
  }, []);

  const loadSession = useCallback(
    async (sessionId: string) => {
      if (isStreaming) return;
      setIsLoadingMessages(true);
      setLoadError(null);
      try {
        const history = await advisorApi.getMessages(sessionId);
        setMessages(
          history.map((item) => ({
            id: item.id,
            role: item.role,
            content: item.content,
            createdAt: item.createdAt,
            sessionId: item.sessionId,
          }))
        );
        setActiveSessionId(sessionId);
        persistActiveSession(sessionId);
        setStreamEvents([]);
        setAssistantDraft("");
        draftRef.current = "";
      } catch {
        setLoadError("Could not load this advisor session.");
      } finally {
        setIsLoadingMessages(false);
      }
    },
    [isStreaming, persistActiveSession]
  );

  useEffect(() => {
    if (authLoading || !user) {
      if (!user) {
        setSessions([]);
        setMessages([]);
        setActiveSessionId(null);
      }
      return;
    }

    let cancelled = false;

    async function initializeSessions() {
      setIsLoadingSessions(true);
      setLoadError(null);
      try {
        const list = await advisorApi.listSessions();
        if (cancelled) return;
        setSessions(list);

        const storedSessionId =
          activeSessionStorageKey && typeof window !== "undefined"
            ? localStorage.getItem(activeSessionStorageKey)
            : null;
        if (storedSessionId && list.some((item) => item.id === storedSessionId)) {
          const history = await advisorApi.getMessages(storedSessionId);
          if (cancelled) return;
          setMessages(
            history.map((item) => ({
              id: item.id,
              role: item.role,
              content: item.content,
              createdAt: item.createdAt,
              sessionId: item.sessionId,
            }))
          );
          setActiveSessionId(storedSessionId);
        } else {
          setMessages([]);
          setActiveSessionId(null);
          persistActiveSession(null);
        }
      } catch {
        if (!cancelled) setLoadError("Could not load advisor sessions.");
      } finally {
        if (!cancelled) setIsLoadingSessions(false);
      }
    }

    void initializeSessions();
    return () => {
      cancelled = true;
    };
  }, [activeSessionStorageKey, persistActiveSession, user, authLoading]);

  useEffect(() => {
    return () => {
      abortRef.current?.abort();
    };
  }, []);

  const status = useMemo(() => {
    if (isStreaming) return "processing";
    if (streamEvents.some((event) => event.type === "error") || loadError) return "error";
    if (messages.length > 0 || streamEvents.some((event) => event.type === "answer")) return "complete";
    return "standby";
  }, [isStreaming, loadError, messages.length, streamEvents]);

  const activeSession = sessions.find((item) => item.id === activeSessionId);

  const resetSession = () => {
    if (isStreaming) return;
    setActiveSessionId(null);
    persistActiveSession(null);
    setMessages([]);
    setStreamEvents([]);
    setAssistantDraft("");
    setMessage("");
    setLoadError(null);
    draftRef.current = "";
  };

  const handleDeleteSession = async (sessionId: string) => {
    if (isStreaming) return;
    try {
      await advisorApi.deleteSession(sessionId);
      setSessions((current) => current.filter((item) => item.id !== sessionId));
      if (activeSessionId === sessionId) {
        resetSession();
      }
    } catch {
      setLoadError("Could not delete this advisor session.");
    }
  };

  const captureSessionId = (envelope: SSEEnvelope) => {
    if (!envelope.session_id) return;
    setActiveSessionId((current) => {
      if (current === envelope.session_id) return current;
      persistActiveSession(envelope.session_id);
      return envelope.session_id;
    });
  };

  const handleEnvelope = (envelope: SSEEnvelope) => {
    captureSessionId(envelope);

    if (envelope.type === "token") {
      const token = String(envelope.data?.token ?? "");
      if (token) {
        draftRef.current += token;
        setAssistantDraft(draftRef.current);
      }
      return;
    }

    if (envelope.type === "final") {
      finalReceivedRef.current = true;
      const answer = String(envelope.data?.answer ?? draftRef.current).trim();
      if (answer) {
        setMessages((current) => [...current, newLocalMessage("assistant", answer, envelope.session_id)]);
      }
      draftRef.current = "";
      setAssistantDraft("");
    }

    const displayEvent = normalizeAdvisorEnvelope(envelope);
    if (displayEvent) {
      setStreamEvents((current) => [...current, displayEvent]);
    }
  };

  const handleSend = async () => {
    const nextMessage = message.trim();
    if (!nextMessage || isStreaming) return;

    setMessage("");
    setLoadError(null);
    setStreamEvents([]);
    setAssistantDraft("");
    draftRef.current = "";
    finalReceivedRef.current = false;
    const targetSessionId = activeSessionId;
    setMessages((current) => [...current, newLocalMessage("user", nextMessage, targetSessionId ?? "")]);

    const controller = new AbortController();
    abortRef.current = controller;
    setIsStreaming(true);

    try {
      await advisorApi.streamChat({
        message: nextMessage,
        sessionId: targetSessionId,
        signal: controller.signal,
        onEnvelope: handleEnvelope,
      });

      if (!finalReceivedRef.current && draftRef.current.trim()) {
        setMessages((current) => [
          ...current,
          newLocalMessage("assistant", draftRef.current.trim(), activeSessionId ?? ""),
        ]);
      }
      await refreshSessions();
    } catch (error) {
      if (!controller.signal.aborted && !finalReceivedRef.current) {
        const content = error instanceof Error ? error.message : "Advisor stream failed.";
        setStreamEvents((current) => [...current, { type: "error", content }]);
      }
    } finally {
      setIsStreaming(false);
      abortRef.current = null;
      draftRef.current = "";
      setAssistantDraft("");
    }
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
            Market research, portfolio context, and risk analysis in one traceable decision stream.
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
            disabled={isStreaming || (!activeSessionId && messages.length === 0)}
            className="inline-flex items-center gap-1.5 rounded border border-terminal-border px-2 py-1 text-[10px] uppercase tracking-wider text-terminal-muted transition-colors hover:border-terminal-accent/40 hover:text-terminal-accent disabled:cursor-not-allowed disabled:opacity-30"
          >
            <Plus className="h-3 w-3" />
            New session
          </button>
        </div>
      </header>

      <div className="grid min-h-[calc(100vh-11.5rem)] grid-cols-1 gap-5 xl:grid-cols-12">
        <aside className="order-2 space-y-5 xl:order-1 xl:col-span-4">
          <section>
            <SectionTitle icon={MessageSquare} title="Sessions" subtitle="Persisted advisor history" />
            <div className="space-y-1.5">
              {isLoadingSessions ? (
                <p className="rounded border border-terminal-border bg-terminal-surface px-3 py-3 text-[10px] uppercase tracking-wider text-terminal-muted">
                  Loading sessions
                </p>
              ) : sessions.length === 0 ? (
                <p className="rounded border border-terminal-border bg-terminal-surface px-3 py-3 text-[10px] leading-relaxed text-terminal-muted">
                  No saved advisor sessions yet.
                </p>
              ) : (
                sessions.map((session) => (
                  <div
                    key={session.id}
                    className={`group flex w-full items-start gap-2 rounded border p-1.5 transition-colors ${
                      activeSessionId === session.id
                        ? "border-terminal-accent/50 bg-terminal-accent/10"
                        : "border-terminal-border bg-terminal-surface hover:border-terminal-accent/40 hover:bg-terminal-accent/5"
                    }`}
                  >
                    <button
                      type="button"
                      onClick={() => void loadSession(session.id)}
                      disabled={isStreaming || isLoadingMessages}
                      className="flex min-w-0 flex-1 items-start gap-3 rounded px-1.5 py-1.5 text-left disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded border border-terminal-border bg-terminal-bg text-terminal-muted transition-colors group-hover:border-terminal-accent/30 group-hover:text-terminal-accent">
                        <MessageSquare className="h-3.5 w-3.5" />
                      </span>
                      <span className="min-w-0 flex-1">
                        <span className="block truncate text-[10px] font-semibold uppercase tracking-widest text-terminal-text">
                          {session.title || "Untitled session"}
                        </span>
                        <span className="mt-1 block text-[9px] uppercase tracking-wider text-terminal-muted">
                          {formatSessionTime(session.updatedAt)}
                        </span>
                      </span>
                    </button>
                    <button
                      type="button"
                      onClick={() => void handleDeleteSession(session.id)}
                      disabled={isStreaming}
                      className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded border border-transparent text-terminal-muted transition-colors hover:border-terminal-red/30 hover:text-terminal-red"
                      aria-label="Delete advisor session"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </section>

          <section>
            <SectionTitle icon={Sparkles} title="Research prompts" subtitle="Start with a focused mandate" />
            <div className="space-y-1.5">
              {promptGroups.map(({ icon: Icon, label, prompt }, index) => (
                <button
                  key={label}
                  type="button"
                  onClick={() => setMessage(prompt)}
                  disabled={isStreaming}
                  className="group flex w-full items-start gap-3 rounded border border-terminal-border bg-terminal-surface px-3 py-3 text-left transition-colors hover:border-terminal-accent/40 hover:bg-terminal-accent/5 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded border border-terminal-border bg-terminal-bg text-terminal-muted transition-colors group-hover:border-terminal-accent/30 group-hover:text-terminal-accent">
                    <Icon className="h-3.5 w-3.5" />
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="flex items-center justify-between">
                      <span className="text-[10px] font-semibold uppercase tracking-widest text-terminal-text">
                        {label}
                      </span>
                      <span className="text-[9px] text-terminal-muted">0{index + 1}</span>
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
            <SectionTitle icon={Activity} title="Session telemetry" subtitle="Current analysis state" />
            <div className="grid grid-cols-3 gap-1.5">
              <TelemetryItem label="Status" value={status} state={status} />
              <TelemetryItem
                label="Steps"
                value={String(streamEvents.filter((event) => event.type === "thought").length).padStart(2, "0")}
              />
              <TelemetryItem label="Saved" value={activeSessionId ? "YES" : "NEW"} />
            </div>
            <div className="mt-1.5 rounded border border-terminal-border bg-terminal-surface px-3 py-2.5">
              <p className="text-[9px] uppercase tracking-widest text-terminal-muted">Active session</p>
              <p className="mt-1 truncate text-[10px] leading-relaxed text-terminal-text">
                {activeSession?.title || activeSessionId || "Draft session"}
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
                  Saved conversation and live agent trace
                </p>
              </div>
            </div>
            <StatusBadge status={status} />
          </div>

          <div className="flex-1 overflow-y-auto bg-terminal-bg/60 p-4">
            {messages.length === 0 && streamEvents.length === 0 && !assistantDraft ? (
              <div className="flex h-full min-h-[360px] items-center justify-center">
                <div className="max-w-sm text-center">
                  <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded border border-terminal-border bg-terminal-surface">
                    <Bot className="h-5 w-5 text-terminal-accent" />
                  </div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-terminal-text">
                    Awaiting research brief
                  </p>
                  <p className="mt-2 text-[10px] leading-relaxed text-terminal-muted">
                    Ask about a stock, market regime, portfolio exposure, or select a structured prompt.
                  </p>
                  {loadError && <p className="mt-3 text-[10px] text-terminal-red">{loadError}</p>}
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                {messages.map((item) =>
                  item.role === "user" ? (
                    <div
                      key={item.id}
                      className="ml-auto max-w-[88%] rounded border border-terminal-accent/30 bg-terminal-accent/5 px-3 py-2.5"
                    >
                      <div className="mb-1 flex items-center justify-between gap-4">
                        <span className="text-[9px] font-semibold uppercase tracking-widest text-terminal-accent">
                          Research brief
                        </span>
                        <span className="text-[9px] text-terminal-muted">USER</span>
                      </div>
                      <p className="whitespace-pre-wrap text-xs leading-relaxed text-terminal-text">
                        {item.content}
                      </p>
                    </div>
                  ) : (
                    <AgentThoughtStream
                      key={item.id}
                      event={{ type: "answer", content: item.content }}
                    />
                  )
                )}

                {streamEvents
                  .filter((event) => event.type !== "answer")
                  .map((event, index) => (
                    <AgentThoughtStream key={`event-${index}`} event={event} />
                  ))}

                {assistantDraft && (
                  <AgentThoughtStream event={{ type: "answer", content: assistantDraft }} />
                )}

                {isStreaming && (
                  <div className="flex items-center gap-2 px-1 py-2 text-[10px] uppercase tracking-widest text-terminal-muted">
                    <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-terminal-amber" />
                    Advisor is processing the brief
                  </div>
                )}
                {loadError && <p className="text-[10px] text-terminal-red">{loadError}</p>}
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
                    void handleSend();
                  }
                }}
                rows={2}
                className="max-h-32 min-h-[44px] flex-1 resize-none bg-transparent px-2 py-1.5 text-xs leading-relaxed text-terminal-text outline-none placeholder:text-terminal-muted/50"
                placeholder="Enter a stock, market, or portfolio research question..."
                aria-label="Advisor research question"
                disabled={isStreaming}
              />
              <button
                type="button"
                onClick={() => void handleSend()}
                disabled={!message.trim() || isStreaming}
                className="flex h-9 items-center gap-2 rounded border border-terminal-accent/40 bg-terminal-accent/10 px-3 text-[10px] font-semibold uppercase tracking-wider text-terminal-accent transition-colors hover:border-terminal-accent/70 hover:bg-terminal-accent/20 disabled:cursor-not-allowed disabled:border-terminal-border disabled:bg-transparent disabled:text-terminal-muted disabled:opacity-40"
              >
                Analyze
                <CornerDownLeft className="h-3 w-3" />
              </button>
            </div>
            <div className="mt-2 flex items-center justify-between px-1 text-[9px] uppercase tracking-wider text-terminal-muted">
              <span>Enter to send | Shift + Enter for newline</span>
              <span>{activeSessionId ? "Persisted context" : "New session"}</span>
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
  icon: ElementType;
  title: string;
  subtitle: string;
}) {
  return (
    <div className="mb-3 flex items-center gap-3 border-b border-terminal-border pb-3">
      <div className="flex h-8 w-8 items-center justify-center rounded border border-terminal-border bg-terminal-surface">
        <Icon className="h-4 w-4 text-terminal-accent" />
      </div>
      <div>
        <h2 className="text-xs font-semibold uppercase tracking-widest text-terminal-text">{title}</h2>
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
      <p className="text-[9px] uppercase tracking-wider text-terminal-muted">{label}</p>
      <p className={`mt-1 truncate text-[10px] font-semibold uppercase ${valueColor}`}>{value}</p>
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
