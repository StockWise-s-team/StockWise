import type { SSEEnvelope, SSEEvent } from "@/lib/types";

export interface ParsedSSE {
  events: SSEEvent[];
  remainder: string;
}

export function parseSSEFrames(buffer: string): ParsedSSE {
  const frames = buffer.replace(/\r\n/g, "\n").split("\n\n");
  const remainder = frames.pop() ?? "";
  const events: SSEEvent[] = [];

  for (const frame of frames) {
    const data = frame
      .split("\n")
      .filter((line) => line.startsWith("data:"))
      .map((line) => line.slice(5).trimStart())
      .join("\n");
    if (!data) continue;
    events.push(JSON.parse(data) as SSEEvent);
  }

  return { events, remainder };
}

export interface ParsedSSEEnvelopes {
  events: SSEEnvelope[];
  remainder: string;
}

export function parseSSEEnvelopeFrames(buffer: string): ParsedSSEEnvelopes {
  const frames = buffer.replace(/\r\n/g, "\n").split("\n\n");
  const remainder = frames.pop() ?? "";
  const events: SSEEnvelope[] = [];

  for (const frame of frames) {
    const data = frame
      .split("\n")
      .filter((line) => line.startsWith("data:"))
      .map((line) => line.slice(5).trimStart())
      .join("\n");
    if (!data) continue;
    events.push(JSON.parse(data) as SSEEnvelope);
  }

  return { events, remainder };
}

export function normalizeAdvisorEnvelope(envelope: SSEEnvelope): SSEEvent | null {
  const data = envelope.data ?? {};
  if (envelope.type === "thought") {
    return { type: "thought", content: String(data.message ?? "") };
  }
  if (envelope.type === "tool_call") {
    const tool = String(data.tool ?? "tool");
    const status = String(data.status ?? "started");
    return { type: "thought", content: `${tool} ${status}` };
  }
  if (envelope.type === "tool_result") {
    return { type: "thought", content: String(data.summary ?? "Tool completed") };
  }
  if (envelope.type === "final") {
    return { type: "answer", content: String(data.answer ?? "") };
  }
  if (envelope.type === "error") {
    return { type: "error", content: String(data.message ?? "Advisor stream failed") };
  }
  return null;
}
