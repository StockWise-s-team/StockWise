"use client";

import { useEffect, useRef, useState } from "react";
import { Client, IMessage, IFrame } from "@stomp/stompjs";
import type { LatestPrice } from "@/lib/types";
import { getAccessToken } from "@/lib/tokenStore";

const WS_BASE_URL =
  process.env.NEXT_PUBLIC_WS_URL ||
  process.env.NEXT_PUBLIC_API_URL?.replace(/^http/, "ws") ||
  "ws://localhost:18082";

export type PriceUpdateCallback = (price: LatestPrice) => void;

interface UseMarketWebSocketOptions {
  symbols?: string[];
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Error) => void;
}

interface UseMarketWebSocketReturn {
  connect: () => void;
  disconnect: () => void;
  subscribe: (symbols: string | string[]) => void;
  unsubscribe: (symbol: string) => void;
  isConnected: boolean;
}

/**
 * Hook for connecting to the Market Service WebSocket endpoint.
 *
 * ```tsx
 * const { connect, subscribe, isConnected } = useMarketWebSocket({
 *   symbols: ["FPT", "VCB"],
 * });
 * useEffect(() => { connect(); }, []);
 * ```
 */
export function useMarketWebSocket(
  options: UseMarketWebSocketOptions = {}
): UseMarketWebSocketReturn {
  const { symbols = [], onConnect, onDisconnect, onError } = options;

  const [isConnected, setIsConnected] = useState(false);
  const clientRef = useRef<Client | null>(null);
  const subscriptionsRef = useRef<Map<string, string>>(new Map());
  const callbacksRef = useRef<Map<string, PriceUpdateCallback>>(new Map());

  // Stable ref to the subscribe function so it can be called from onConnect
  const subscribeFnRef = useRef<(client: Client, syms: string[]) => void>(
    () => {}
  );

  const connect = () => {
    if (clientRef.current?.connected) return;

    const token = getAccessToken();
    if (!token) {
      onError?.(new Error("No access token available"));
      return;
    }

    const client = new Client({
      brokerURL: `${WS_BASE_URL}/ws/market/websocket?token=${token}`,
      connectHeaders: { token },
      onConnect: () => {
        setIsConnected(true);
        onConnect?.();
        if (symbols.length > 0) {
          subscribeFnRef.current(client, symbols);
        }
      },
      onDisconnect: () => {
        setIsConnected(false);
        subscriptionsRef.current.clear();
        onDisconnect?.();
      },
      onStompError: (frame: IFrame) => {
        onError?.(new Error(`STOMP error: ${frame.headers.message}`));
      },
      onWebSocketError: (event: Event) => {
        onError?.(new Error(`WebSocket error: ${event.type}`));
      },
      reconnectDelay: 3000,
      heartbeatIncoming: 10000,
      heartbeatOutgoing: 10000,
    });

    client.activate();
    clientRef.current = client;
  };

  const subscribe = (syms: string | string[]) => {
    const symbolList = Array.isArray(syms) ? syms : [syms];
    const client = clientRef.current;
    if (!client || !client.connected) return;
    subscribeFnRef.current(client, symbolList);
  };

  const unsubscribe = (symbol: string) => {
    const sym = symbol.trim().toUpperCase();
    const client = clientRef.current;
    if (!client) return;

    const subId = subscriptionsRef.current.get(sym);
    if (subId) {
      client.unsubscribe(subId);
      subscriptionsRef.current.delete(sym);
      callbacksRef.current.delete(sym);
    }
  };

  const disconnect = () => {
    if (clientRef.current) {
      clientRef.current.deactivate();
      clientRef.current = null;
      setIsConnected(false);
      subscriptionsRef.current.clear();
      callbacksRef.current.clear();
    }
  };

  // Register the subscribe function once
  subscribeFnRef.current = (client: Client, syms: string[]) => {
    for (const sym of syms) {
      const symbol = sym.trim().toUpperCase();
      if (subscriptionsRef.current.has(symbol)) continue;

      const subscription = client.subscribe(
        `/topic/price/${symbol}`,
        (message: IMessage) => {
          try {
            const price: LatestPrice = JSON.parse(message.body);
            callbacksRef.current.get(symbol)?.(price);
          } catch {
            // ignore parse errors
          }
        }
      );

      subscriptionsRef.current.set(symbol, subscription.id);

      client.publish({
        destination: `/app/subscribe/${symbol}`,
        body: "",
        headers: { symbol },
      });
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { connect, disconnect, subscribe, unsubscribe, isConnected };
}

/** Simple hook: subscribe one symbol and receive live price updates. */
export function useLivePrice(
  symbol: string | null,
  onPrice: PriceUpdateCallback
): { isConnected: boolean; reconnect: () => void } {
  const [isConnected, setIsConnected] = useState(false);
  const clientRef = useRef<Client | null>(null);
  const subIdRef = useRef<string | null>(null);
  const reconnectingRef = useRef(false);
  const symbolRef = useRef<string | null>(null);

  useEffect(() => {
    symbolRef.current = symbol;
  }, [symbol]);

  const connectClient = (sym: string) => {
    const token = getAccessToken();
    if (!token || !sym) return;

    if (clientRef.current?.connected && subIdRef.current) {
      try {
        clientRef.current.unsubscribe(subIdRef.current);
      } catch {
        // ignore
      }
      subIdRef.current = null;
    }

    if (clientRef.current && !clientRef.current.connected) {
      clientRef.current.activate();
      return;
    }

    const client = new Client({
      brokerURL: `${WS_BASE_URL}/ws/market/websocket?token=${token}`,
      connectHeaders: { token },
      onConnect: () => {
        setIsConnected(true);
        reconnectingRef.current = false;
        const sub = client.subscribe(
          `/topic/price/${sym}`,
          (message: IMessage) => {
            try {
              onPrice(JSON.parse(message.body) as LatestPrice);
            } catch {
              // ignore
            }
          }
        );
        subIdRef.current = sub.id;

        // Register session in the server-side registry so MarketDataConsumer
        // knows this session is subscribed and will forward price updates.
        client.publish({
          destination: `/app/subscribe/${sym}`,
          body: "",
          headers: { symbol: sym },
        });
      },
      onDisconnect: () => {
        setIsConnected(false);
        subIdRef.current = null;
      },
      reconnectDelay: 3000,
    });

    client.activate();
    clientRef.current = client;
  };

  const disconnectAll = () => {
    if (clientRef.current) {
      if (subIdRef.current) {
        try {
          clientRef.current.unsubscribe(subIdRef.current);
        } catch {
          // ignore
        }
        subIdRef.current = null;
      }
      clientRef.current.deactivate();
      clientRef.current = null;
    }
    setIsConnected(false);
  };

  const reconnect = () => {
    const sym = symbolRef.current;
    if (sym && !reconnectingRef.current) {
      reconnectingRef.current = true;
      disconnectAll();
      setTimeout(() => connectClient(sym), 500);
    }
  };

  useEffect(() => {
    if (symbol) {
      connectClient(symbol);
    }
    return () => {
      disconnectAll();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [symbol]);

  return { isConnected, reconnect };
}
