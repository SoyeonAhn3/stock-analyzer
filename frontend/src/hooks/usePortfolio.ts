import { useState, useEffect, useCallback, useMemo } from 'react';
import type { Holding, QuoteInfo } from '../services/portfolioApi';
import { loadHoldings, saveHoldings, fetchQuotes } from '../services/portfolioApi';

interface HoldingSummary {
  ticker: string;
  shares: number;
  avg_cost: number;
  current_price: number | null;
  market_value: number | null;
  cost_basis: number;
  pnl: number | null;
  pnl_pct: number | null;
  weight: number | null;
  sector?: string;
}

interface PortfolioSummary {
  total_market_value: number;
  total_cost_basis: number;
  total_pnl: number;
  total_pnl_pct: number;
  best: HoldingSummary | null;
  worst: HoldingSummary | null;
}

export function usePortfolio() {
  const [holdings, setHoldings] = useState<Holding[]>(loadHoldings);
  const [quotes, setQuotes] = useState<Record<string, QuoteInfo>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshQuotes = useCallback(async () => {
    if (holdings.length === 0) {
      setQuotes({});
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const tickers = holdings.map((h) => h.ticker);
      const data = await fetchQuotes(tickers);
      setQuotes(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch quotes');
    } finally {
      setLoading(false);
    }
  }, [holdings]);

  useEffect(() => {
    refreshQuotes();
  }, [refreshQuotes]);

  // 60초 자동 갱신
  useEffect(() => {
    if (holdings.length === 0) return;
    const id = setInterval(refreshQuotes, 60_000);
    return () => clearInterval(id);
  }, [holdings.length, refreshQuotes]);

  const holdingSummaries: HoldingSummary[] = useMemo(() => {
    const items = holdings.map((h) => {
      const q = quotes[h.ticker];
      const price = q?.price ?? null;
      const cost_basis = h.avg_cost * h.shares;
      const market_value = price !== null ? price * h.shares : null;
      const pnl = market_value !== null ? market_value - cost_basis : null;
      const pnl_pct = pnl !== null && cost_basis > 0 ? (pnl / cost_basis) * 100 : null;

      return {
        ticker: h.ticker,
        shares: h.shares,
        avg_cost: h.avg_cost,
        current_price: price,
        market_value,
        cost_basis,
        pnl,
        pnl_pct,
        weight: null as number | null,
      };
    });

    const totalMV = items.reduce((s, i) => s + (i.market_value ?? 0), 0);
    for (const item of items) {
      if (item.market_value !== null && totalMV > 0) {
        item.weight = (item.market_value / totalMV) * 100;
      }
    }
    return items;
  }, [holdings, quotes]);

  const summary: PortfolioSummary = useMemo(() => {
    const totalMV = holdingSummaries.reduce((s, i) => s + (i.market_value ?? 0), 0);
    const totalCost = holdingSummaries.reduce((s, i) => s + i.cost_basis, 0);
    const totalPnl = totalMV - totalCost;
    const totalPnlPct = totalCost > 0 ? (totalPnl / totalCost) * 100 : 0;

    const withPnl = holdingSummaries.filter((h) => h.pnl_pct !== null);
    const best = withPnl.length > 0
      ? withPnl.reduce((a, b) => ((a.pnl_pct ?? 0) > (b.pnl_pct ?? 0) ? a : b))
      : null;
    const worst = withPnl.length > 0
      ? withPnl.reduce((a, b) => ((a.pnl_pct ?? 0) < (b.pnl_pct ?? 0) ? a : b))
      : null;

    return {
      total_market_value: totalMV,
      total_cost_basis: totalCost,
      total_pnl: totalPnl,
      total_pnl_pct: totalPnlPct,
      best,
      worst,
    };
  }, [holdingSummaries]);

  const addHolding = useCallback((h: Omit<Holding, 'id' | 'created_at'>) => {
    const newHolding: Holding = {
      ...h,
      id: crypto.randomUUID(),
      created_at: new Date().toISOString(),
    };
    setHoldings((prev) => {
      const next = [...prev, newHolding];
      saveHoldings(next);
      return next;
    });
  }, []);

  const updateHolding = useCallback((id: string, updates: Partial<Holding>) => {
    setHoldings((prev) => {
      const next = prev.map((h) => (h.id === id ? { ...h, ...updates } : h));
      saveHoldings(next);
      return next;
    });
  }, []);

  const removeHolding = useCallback((id: string) => {
    setHoldings((prev) => {
      const next = prev.filter((h) => h.id !== id);
      saveHoldings(next);
      return next;
    });
  }, []);

  return {
    holdings,
    quotes,
    holdingSummaries,
    summary,
    loading,
    error,
    addHolding,
    updateHolding,
    removeHolding,
    refreshQuotes,
  };
}
