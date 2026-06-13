"use client";

import { useCallback, useEffect, useState } from "react";
import type { PortfolioView } from "@/lib/types";
import { extractErrorMessage } from "@/lib/apiError";
import { portfolioGateway, marketPriceProvider } from "@/lib/portfolio/gateway";
import { loadPortfolioView, type PortfolioDataSource } from "@/lib/portfolio/loadPortfolioView";

interface UsePortfolioResult {
  data: PortfolioView | null;
  loading: boolean;
  error: string | null;
  reload: () => Promise<void>;
}

// Default wiring to the live HTTP backends; a different source can be injected
// (e.g. in tests) without touching this hook.
const defaultSource: PortfolioDataSource = {
  gateway: portfolioGateway,
  prices: marketPriceProvider,
};

// Thin React adapter: owns only loading/error/data state and delegates all data
// access and money math to the injected source + loadPortfolioView orchestrator.
export function usePortfolio(
  userId: string | undefined,
  source: PortfolioDataSource = defaultSource
): UsePortfolioResult {
  const [data, setData] = useState<PortfolioView | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!userId) return;
    setLoading(true);
    setError(null);
    try {
      setData(await loadPortfolioView(source));
    } catch (e) {
      setError(extractErrorMessage(e, "Không tải được portfolio."));
    } finally {
      setLoading(false);
    }
  }, [userId, source]);

  useEffect(() => {
    load();
  }, [load]);

  return { data, loading, error, reload: load };
}
