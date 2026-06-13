"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import type { SSEEvent } from "@/lib/types";

const MOCK_EVENTS: SSEEvent[] = [
  { type: "thought", content: "Analyzing your query..." },
  { type: "thought", content: "Retrieving market data..." },
  { type: "answer", content: "Based on current trends, the market looks positive." },
];

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:18080";

export function useSSE(endpoint: string | null): SSEEvent[] {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);
  const mockIndexRef = useRef(0);
  const mockIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const cleanup = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    if (mockIntervalRef.current) {
      clearInterval(mockIntervalRef.current);
      mockIntervalRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (!endpoint) {
      cleanup();
      setEvents([]);
      return;
    }

    const url = endpoint.startsWith("http") ? endpoint : `${API_BASE}${endpoint}`;

    try {
      const es = new EventSource(url, { withCredentials: true });
      eventSourceRef.current = es;

      const handleEvent = (type: "thought" | "answer" | "error", dataStr: string, isToken = false, isFinal = false) => {
        try {
          let content = dataStr;
          try {
            const parsed = JSON.parse(dataStr);
            if (parsed && typeof parsed === "object") {
              if (parsed.data) {
                if (isToken) {
                  content = parsed.data.token || "";
                } else if (isFinal) {
                  content = parsed.data.answer || "";
                } else {
                  content = parsed.data.message || parsed.data.answer || dataStr;
                }
              } else {
                content = parsed.content || parsed.message || dataStr;
              }
            }
          } catch {}

          if (!content && isToken) return;

          setEvents((prev) => {
            if (type === "answer" && prev.length > 0 && prev[prev.length - 1].type === "answer") {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              if (isFinal) {
                updated[updated.length - 1] = { type, content };
              } else {
                updated[updated.length - 1] = { type, content: last.content + content };
              }
              return updated;
            }
            return [...prev, { type, content }];
          });
        } catch (err) {
          console.error("SSE handling error:", err);
        }
      };

      es.addEventListener("thought", (e) => handleEvent("thought", (e as MessageEvent).data));
      es.addEventListener("token", (e) => handleEvent("answer", (e as MessageEvent).data, true));
      es.addEventListener("final", (e) => handleEvent("answer", (e as MessageEvent).data, false, true));
      es.addEventListener("error", (e) => {
        const msg = e as MessageEvent;
        if (msg.data) {
          handleEvent("error", msg.data);
        }
      });
      es.onmessage = (e) => handleEvent("answer", e.data);

      es.onerror = () => {
        es.close();
      };
    } catch {
      mockIndexRef.current = 0;
      setEvents([]);
      mockIntervalRef.current = setInterval(() => {
        setEvents((prev) => {
          if (mockIndexRef.current >= MOCK_EVENTS.length) {
            if (mockIntervalRef.current) {
              clearInterval(mockIntervalRef.current);
              mockIntervalRef.current = null;
            }
            return prev;
          }
          const next = MOCK_EVENTS[mockIndexRef.current++];
          return [...prev, next];
        });
      }, 800);
    }

    return cleanup;
  }, [endpoint, cleanup]);

  return events;
}
