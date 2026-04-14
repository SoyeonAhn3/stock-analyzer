import { useState, useEffect } from 'react';
import type { QuoteResponse, FundamentalsResponse, TechnicalsResponse } from '../types/api';

const API = '/api';

interface UseQuoteResult {
  quote: QuoteResponse | null;
  fundamentals: FundamentalsResponse | null;
  technicals: TechnicalsResponse | null;
  loading: boolean;
  error: string | null;
}

/** Quick Look 데이터 3종을 병렬 호출 */
export function useQuote(ticker: string | undefined): UseQuoteResult {
  const [quote, setQuote] = useState<QuoteResponse | null>(null);
  const [fundamentals, setFundamentals] = useState<FundamentalsResponse | null>(null);
  const [technicals, setTechnicals] = useState<TechnicalsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!ticker) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    const fetchJson = (path: string) =>
      fetch(`${API}${path}`).then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      });

    Promise.all([
      fetchJson(`/quote/${ticker}`).catch(() => null),
      fetchJson(`/fundamentals/${ticker}`).catch(() => null),
      fetchJson(`/technicals/${ticker}`).catch(() => null),
    ])
      .then(([q, f, t]) => {
        setQuote(q);
        setFundamentals(f);
        setTechnicals(t);
        if (!q) setError('Failed to load quote data');
      })
      .finally(() => setLoading(false));
  }, [ticker]);

  return { quote, fundamentals, technicals, loading, error };
}
