import { API_BASE } from '../config';

export interface Holding {
  id: string;
  ticker: string;
  shares: number;
  avg_cost: number;
  currency: string;
  purchase_date: string | null;
  memo: string;
  created_at: string;
}

export interface QuoteInfo {
  price: number;
  change: number;
  change_pct: number;
  prev_close: number;
  name?: string;
}

export interface AnalysisResult {
  summary: {
    total_market_value: number;
    total_cost_basis: number;
    total_pnl: number;
    total_pnl_pct: number;
    holdings_count: number;
  };
  analysis: Record<string, unknown>;
  ai_report: Record<string, unknown> | null;
}

const LS_KEY = 'portfolio_holdings';

export function loadHoldings(): Holding[] {
  try {
    const raw = localStorage.getItem(LS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveHoldings(holdings: Holding[]) {
  localStorage.setItem(LS_KEY, JSON.stringify(holdings));
}

export async function fetchQuotes(tickers: string[]): Promise<Record<string, QuoteInfo>> {
  const res = await fetch(`${API_BASE}/portfolio/quotes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tickers }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return data.quotes;
}

export async function fetchAnalysis(holdings: Holding[]): Promise<AnalysisResult> {
  const body = {
    holdings: holdings.map((h) => ({
      ticker: h.ticker,
      shares: h.shares,
      avg_cost: h.avg_cost,
      currency: h.currency,
      purchase_date: h.purchase_date,
      memo: h.memo,
    })),
  };
  const res = await fetch(`${API_BASE}/portfolio/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function validateTicker(ticker: string): Promise<{ valid: boolean; name?: string }> {
  const res = await fetch(`${API_BASE}/portfolio/validate/${ticker.toUpperCase()}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
