"use client";

import React from "react";
import type { SSEEvent } from "@/lib/types";

interface AgentThoughtStreamProps {
  event: SSEEvent;
}

export function AgentThoughtStream({ event }: AgentThoughtStreamProps) {
  const colorMap: Record<SSEEvent["type"], string> = {
    thought: "text-blue-600 border-blue-200 bg-blue-50",
    answer: "text-green-700 border-green-200 bg-green-50",
    error: "text-red-600 border-red-200 bg-red-50",
  };

  const labelMap: Record<SSEEvent["type"], string> = {
    thought: "Thought",
    answer: "Answer",
    error: "Error",
  };

  return (
    <div className={`mb-3 rounded-md border p-3 ${colorMap[event.type]}`}>
      <span className="text-xs font-semibold uppercase">
        {labelMap[event.type]}
      </span>
      <p className="mt-1 text-sm whitespace-pre-wrap">{event.content}</p>
    </div>
  );
}
