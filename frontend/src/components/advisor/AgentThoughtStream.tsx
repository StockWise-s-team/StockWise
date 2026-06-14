"use client";

import { AlertTriangle, Bot, CheckCircle2, Cpu } from "lucide-react";
import type { SSEEvent } from "@/lib/types";
import { Markdown } from "@/components/common/Markdown";

interface AgentThoughtStreamProps {
  event: SSEEvent;
}

const eventConfig: Record<
  SSEEvent["type"],
  {
    label: string;
    icon: typeof Cpu;
    shell: string;
    iconShell: string;
    labelColor: string;
  }
> = {
  thought: {
    label: "Agent trace",
    icon: Cpu,
    shell: "border-terminal-border bg-terminal-surface",
    iconShell: "border-terminal-border bg-terminal-bg text-terminal-amber",
    labelColor: "text-terminal-amber",
  },
  answer: {
    label: "Advisor output",
    icon: CheckCircle2,
    shell: "border-terminal-green/25 bg-terminal-green/5",
    iconShell: "border-terminal-green/25 bg-terminal-green/10 text-terminal-green",
    labelColor: "text-terminal-green",
  },
  error: {
    label: "System error",
    icon: AlertTriangle,
    shell: "border-terminal-red/30 bg-terminal-red/5",
    iconShell: "border-terminal-red/30 bg-terminal-red/10 text-terminal-red",
    labelColor: "text-terminal-red",
  },
};

export function AgentThoughtStream({ event }: AgentThoughtStreamProps) {
  const config = eventConfig[event.type];
  const Icon = config.icon;

  return (
    <div className={`flex gap-3 rounded border p-3 ${config.shell}`}>
      <div
        className={`flex h-7 w-7 shrink-0 items-center justify-center rounded border ${config.iconShell}`}
      >
        <Icon className="h-3.5 w-3.5" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="mb-1.5 flex items-center justify-between gap-3">
          <span
            className={`text-[9px] font-semibold uppercase tracking-[0.18em] ${config.labelColor}`}
          >
            {config.label}
          </span>
          <Bot className="h-3 w-3 text-terminal-muted" />
        </div>
        {event.type === "answer" ? (
          <Markdown content={event.content} />
        ) : (
          <p className="whitespace-pre-wrap text-xs leading-relaxed text-terminal-text">
            {event.content}
          </p>
        )}
      </div>
    </div>
  );
}
