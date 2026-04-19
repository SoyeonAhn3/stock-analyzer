import { useState, useCallback, useEffect } from 'react';
import type { AnalysisResult, FullAnalysisResponse } from '../types/api';
import { API_BASE } from '../config';

/** AI 분석 hook — 캐시 자동 조회 + 수동 trigger/재분석 지원 */
export function useAnalysis(ticker: string | undefined) {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [fullResponse, setFullResponse] = useState<FullAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cachedAt, setCachedAt] = useState<string | null>(null);

  const applyResponse = useCallback((data: any) => {
    const analyst = data?.analyst ?? data;
    setResult(analyst);
    if (data?.agent_results) {
      setFullResponse(data as FullAnalysisResponse);
    }
    setCachedAt(data?.cached_at ?? null);
  }, []);

  const trigger = useCallback((force = false) => {
    if (!ticker) return;
    setLoading(true);
    setError(null);
    if (force) {
      setResult(null);
      setFullResponse(null);
    }

    const url = force
      ? `${API_BASE}/analysis/${ticker}?force=true`
      : `${API_BASE}/analysis/${ticker}`;

    fetch(url, { method: 'POST' })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(applyResponse)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [ticker, applyResponse]);

  // 캐시 자동 조회 (GET) — ticker 변경 시 캐시된 결과가 있으면 바로 표시
  useEffect(() => {
    if (!ticker) return;
    setResult(null);
    setFullResponse(null);
    setCachedAt(null);
    setError(null);

    fetch(`${API_BASE}/analysis/${ticker}/cache`)
      .then((r) => {
        if (!r.ok) return null;
        return r.json();
      })
      .then((data) => {
        if (data) applyResponse(data);
      })
      .catch(() => {});
  }, [ticker, applyResponse]);

  return { result, fullResponse, loading, error, trigger, cachedAt };
}
