import { useState, useCallback } from 'react';
import type { AnalysisResult } from '../types/api';

/** AI 분석 수동 실행 hook — trigger()로 호출 */
export function useAnalysis(ticker: string | undefined) {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const trigger = useCallback(() => {
    if (!ticker) return;
    setLoading(true);
    setError(null);
    setResult(null);

    fetch(`/api/analysis/${ticker}`, { method: 'POST' })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data) => {
        // orchestrator 응답에서 analyst 결과 추출
        const analyst = data?.analyst ?? data;
        setResult(analyst);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [ticker]);

  return { result, loading, error, trigger };
}
