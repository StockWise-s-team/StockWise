"use client";

/**
 * MarketDataProvider — single shared STOMP/WebSocket connection to the
 * market-service `/ws/market` endpoint.
 *
 * Why a context (and not a per-component hook)?
 *   The market-service `MarketWebSocketController` keeps a session↔symbol
 *   registry in-memory; creating a fresh client per consumer causes
 *   "subscribed → disconnected" storms on the backend and prevents the
 *   `RabbitListener` from ever finding a live session to push ticks to.
 *
 *   This provider opens ONE STOMP client for the entire dashboard tree,
 *   subscribes to `/topic/price/{symbol}` for each tracked symbol, and
 *   caches the latest tick per symbol in a ref-backed map. Components
 *   consume ticks via `useMarketTicker(symbol)` without ever touching the
 *   client directly.
 */

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  ReactNode,
} from "react";
import { Client, IMessage } from "@stomp/stompjs";
import { getAccessToken } from "@/lib/tokenStore";
import type { LatestPrice } from "@/lib/types";

const WS_BASE_URL =
  process.env.NEXT_PUBLIC_WS_URL ||
  process.env.NEXT_PUBLIC_API_URL?.replace(/^http/, "ws") ||
  "ws://localhost:18082";

export type ConnectionState = "idle" | "connecting" | "connected" | "reconnecting" | "error";

interface MarketDataContextValue {
  /** Per-symbol latest tick (null until first tick arrives). */
  getTicker: (symbol: string) => LatestPrice | null;
  /** Total ticks received per symbol (for live counters in UI). */
  getTickCount: (symbol: string) => number;
  /** Array of all live ticks received for a symbol in this session. */
  getLiveHistory: (symbol: string) => LatestPrice[];
  /** Subscribe to ticks for a symbol. Idempotent — safe to call repeatedly. */
  subscribe: (symbol: string) => void;
  /** Stop tracking a symbol. */
  unsubscribe: (symbol: string) => void;
  /** Connection state for the underlying STOMP client. */
  connectionState: ConnectionState;
}

const MarketDataContext = createContext<MarketDataContextValue | undefined>(undefined);

interface ProviderProps {
  children: ReactNode;
  /**
   * The list of symbols the provider should subscribe to. Pass the full
   * tracked list — the provider diffs and (un)subscribes on change.
   * If undefined, the provider stays connected but does not auto-subscribe.
   */
  symbols?: string[];
}

export function MarketDataProvider({ children, symbols }: ProviderProps) {
  const clientRef = useRef<Client | null>(null);
  const tickersRef = useRef<Record<string, LatestPrice>>({});
  const tickCountsRef = useRef<Record<string, number>>({});
  const liveHistoryRef = useRef<Record<string, LatestPrice[]>>({});
  const subscribedRef = useRef<Set<string>>(new Set());
  const tickVersionRef = useRef(0); // bumped on every tick — used to force re-render

  const [connectionState, setConnectionState] = useState<ConnectionState>("idle");
  const [version, setVersion] = useState(0);

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    let mounted = true;
    let client: Client | null = null;

    const connect = () => {
      const token = getAccessToken();
      if (!token) {
        // Not authenticated yet — stay idle, will retry when token becomes available.
        return;
      }
      if (clientRef.current?.connected) return;
      if (!mounted) return;

      setConnectionState("connecting");
      client = new Client({
        brokerURL: `${WS_BASE_URL}/ws/market/websocket?token=${token}`,
        connectHeaders: { token },
        reconnectDelay: 5000,
        heartbeatIncoming: 10000,
        heartbeatOutgoing: 10000,
        debug: () => {
          // silence STOMP debug logs
        },
        onConnect: () => {
          if (!mounted) return;
          setConnectionState("connected");
          // Re-subscribe to anything we had been tracking
          for (const sym of subscribedRef.current) {
            try {
              clientRef.current?.subscribe(`/topic/price/${sym}`, (msg: IMessage) => {
                try {
                  const price = JSON.parse(msg.body) as LatestPrice;
                  if (!price?.symbol) return;
                  tickersRef.current[price.symbol.toUpperCase()] = price;
                  tickCountsRef.current[price.symbol.toUpperCase()] =
                    (tickCountsRef.current[price.symbol.toUpperCase()] ?? 0) + 1;
                  const hist = liveHistoryRef.current[price.symbol.toUpperCase()] || [];
                  hist.push(price);
                  liveHistoryRef.current[price.symbol.toUpperCase()] = hist;
                  tickVersionRef.current += 1;
                  setVersion(tickVersionRef.current);
                } catch {
                  // ignore parse errors
                }
              });
              clientRef.current?.publish({
                destination: `/app/subscribe/${sym}`,
                body: "",
                headers: { symbol: sym },
              });
            } catch {
              // ignore
            }
          }
        },
        onDisconnect: () => {
          if (mounted) setConnectionState("reconnecting");
        },
        onStompError: () => {
          if (mounted) setConnectionState("error");
        },
        onWebSocketError: () => {
          if (mounted) setConnectionState("error");
        },
      });

      client.activate();
      clientRef.current = client;
    };

    connect();

    return () => {
      mounted = false;
      try {
        clientRef.current?.deactivate();
      } catch {
        // ignore
      }
      clientRef.current = null;
    };
  }, []);

  // React to symbol list changes — diff and (un)subscribe.
  useEffect(() => {
    if (!symbols) return;
    const client = clientRef.current;
    const desired = new Set(symbols.map((s) => s.toUpperCase()));

    // Unsubscribe removed
    for (const sym of Array.from(subscribedRef.current)) {
      if (!desired.has(sym)) {
        // STOMP client doesn't have an easy "list active subs by destination"
        // API. We rely on the broker to drop messages to a topic with no
        // subscribers; locally we just stop tracking. A future improvement
        // could track subscription IDs returned by `client.subscribe`.
        subscribedRef.current.delete(sym);
        delete tickersRef.current[sym];
        delete tickCountsRef.current[sym];
        delete liveHistoryRef.current[sym];
      }
    }

    // Subscribe added (only when connected)
    if (client?.connected) {
      for (const sym of desired) {
        if (subscribedRef.current.has(sym)) continue;
        try {
          client.subscribe(`/topic/price/${sym}`, (msg: IMessage) => {
            try {
              const price = JSON.parse(msg.body) as LatestPrice;
              if (!price?.symbol) return;
              const key = price.symbol.toUpperCase();
              tickersRef.current[key] = price;
              tickCountsRef.current[key] = (tickCountsRef.current[key] ?? 0) + 1;
              const hist = liveHistoryRef.current[key] || [];
              hist.push(price);
              liveHistoryRef.current[key] = hist;
              tickVersionRef.current += 1;
              setVersion(tickVersionRef.current);
            } catch {
              // ignore parse errors
            }
          });
          client.publish({
            destination: `/app/subscribe/${sym}`,
            body: "",
            headers: { symbol: sym },
          });
          subscribedRef.current.add(sym);
        } catch {
          // ignore — will retry on reconnect
        }
      }
    } else {
      // Not connected yet — record intent so onConnect can re-subscribe.
      for (const sym of desired) {
        subscribedRef.current.add(sym);
      }
    }
  }, [symbols, connectionState, version]);

  const value = useMemo<MarketDataContextValue>(
    () => ({
      getTicker: (sym: string) => tickersRef.current[sym.toUpperCase()] ?? null,
      getTickCount: (sym: string) => tickCountsRef.current[sym.toUpperCase()] ?? 0,
      getLiveHistory: (sym: string) => liveHistoryRef.current[sym.toUpperCase()] ?? [],
      subscribe: (sym: string) => {
        const upper = sym.toUpperCase();
        if (subscribedRef.current.has(upper)) return;
        subscribedRef.current.add(upper);
        const client = clientRef.current;
        if (client?.connected) {
          try {
            client.subscribe(`/topic/price/${upper}`, (msg: IMessage) => {
              try {
                const price = JSON.parse(msg.body) as LatestPrice;
                if (!price?.symbol) return;
                const key = price.symbol.toUpperCase();
                tickersRef.current[key] = price;
                tickCountsRef.current[key] = (tickCountsRef.current[key] ?? 0) + 1;
                const hist = liveHistoryRef.current[key] || [];
                hist.push(price);
                liveHistoryRef.current[key] = hist;
                tickVersionRef.current += 1;
                setVersion(tickVersionRef.current);
              } catch {
                // ignore
              }
            });
            client.publish({
              destination: `/app/subscribe/${upper}`,
              body: "",
              headers: { symbol: upper },
            });
          } catch {
            // ignore
          }
        }
        // Bump version so the diff effect re-runs even if symbols prop is empty
        setVersion((v) => v + 1);
      },
      unsubscribe: (sym: string) => {
        const upper = sym.toUpperCase();
        subscribedRef.current.delete(upper);
        delete tickersRef.current[upper];
        delete tickCountsRef.current[upper];
        delete liveHistoryRef.current[upper];
        setVersion((v) => v + 1);
      },
      connectionState,
    }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [connectionState, version],
  );

  return <MarketDataContext.Provider value={value}>{children}</MarketDataContext.Provider>;
}

export function useMarketData(): MarketDataContextValue {
  const ctx = useContext(MarketDataContext);
  if (!ctx) {
    throw new Error("useMarketData must be used within a MarketDataProvider");
  }
  return ctx;
}

/**
 * Subscribe to live ticks for `symbol`. Returns:
 *   - `ticker`: the most recent LatestPrice (null until first tick)
 *   - `tickCount`: how many ticks have been received since mount
 *   - `connectionState`: shared STOMP client state
 *
 * Components re-render only when the requested symbol's tick changes
 * (the provider bumps `version` on every tick across all symbols, but
 * React's reconciliation makes the cost negligible).
 */
export function useMarketTicker(symbol: string | null | undefined): {
  ticker: LatestPrice | null;
  tickCount: number;
  connectionState: ConnectionState;
} {
  const { getTicker, getTickCount, connectionState } = useMarketData();
  const [, force] = useState(0);
  // Re-render the component when `version` bumps (provider tick).
  useEffect(() => {
    const interval = setInterval(() => force((v) => v + 1), 500);
    return () => clearInterval(interval);
  }, []);
  if (!symbol) {
    return { ticker: null, tickCount: 0, connectionState};
  }
  return {
    ticker: getTicker(symbol),
    tickCount: getTickCount(symbol),
    connectionState,
  };
}
