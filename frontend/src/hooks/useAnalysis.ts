import { useState, useCallback, useEffect } from 'react';
import type { AnalysisResult, FullAnalysisResponse } from '../types/api';
import { API_BASE } from '../config';
import { useAuth } from '../auth/AuthProvider';

/** AI 분석 hook — 캐시 자동 조회 + 수동 trigger/재분석 지원 (Phase 14 무료체험 게이트 포함) */
export function useAnalysis(ticker: string | undefined) {
  const { token } = useAuth();
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [fullResponse, setFullResponse] = useState<FullAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cachedAt, setCachedAt] = useState<string | null>(null);
  const [trialBlocked, setTrialBlocked] = useState(false);

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
    setTrialBlocked(false);
    if (force) {
      setResult(null);
      setFullResponse(null);
    }

    const url = force
      ? `${API_BASE}/analysis/${ticker}?force=true`
      : `${API_BASE}/analysis/${ticker}`;

    // 무료체험 게이트: 검증된 Google 토큰 + 멱등성 키
    const headers: Record<string, string> = { 'X-Request-Id': crypto.randomUUID() };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    fetch(url, { method: 'POST', headers })
      .then((r) => {
        if (r.status === 429) {
          setTrialBlocked(true); // 무료 한도 소진 → 모달
          return null;
        }
        if (r.status === 401) {
          setError('세션이 만료되었습니다. 다시 로그인해주세요.');
          return null;
        }
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data) => {
        if (!data) return;
        applyResponse(data);
        window.dispatchEvent(new Event('trial-changed')); // 사이드바 잔여 횟수 갱신
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [ticker, applyResponse, token]);

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

  return {
    result,
    fullResponse,
    loading,
    error,
    trigger,
    cachedAt,
    trialBlocked,
    clearTrialBlocked: () => setTrialBlocked(false),
  };
}
