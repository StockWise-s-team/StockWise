"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import type { SSEEvent } from "@/lib/types";

const MOCK_EVENTS: SSEEvent[] = [
  { type: "thought", content: "Analyzing your query..." },
  { type: "thought", content: "Retrieving market data..." },
  { type: "answer", content: "Based on current trends, the market looks positive." },
];

const AI_SERVICE_BASE = process.env.NEXT_PUBLIC_AI_SERVICE_URL || "http://localhost:18000";

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

    const url = endpoint.startsWith("http") ? endpoint : `${AI_SERVICE_BASE}${endpoint}`;

    try {
      const es = new EventSource(url);
      eventSourceRef.current = es;

      es.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as SSEEvent;
          setEvents((prev) => [...prev, data]);
        } catch {
          setEvents((prev) => [
            ...prev,
            { type: "answer", content: event.data },
          ]);
        }
      };

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
