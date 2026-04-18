import { useState, useEffect, useCallback } from 'react';
import { API_BASE } from '../config';

interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/** GET 요청 공통 hook — 마운트 시 자동 호출 */
export function useApi<T>(path: string): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(() => {
    setLoading(true);
    setError(null);
    fetch(`${API_BASE}${path}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [path]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

/** POST 요청 hook — trigger()로 수동 호출 */
export function usePost<T, B = unknown>(path: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const trigger = useCallback(
    (body?: B) => {
      setLoading(true);
      setError(null);
      return fetch(`${API_BASE}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: body ? JSON.stringify(body) : undefined,
      })
        .then((res) => {
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          return res.json();
        })
        .then((d) => {
          setData(d);
          return d as T;
        })
        .catch((e) => {
          setError(e.message);
          return null;
        })
        .finally(() => setLoading(false));
    },
    [path],
  );

  return { data, loading, error, trigger };
}

/** 주기적 폴링 hook — listenEvent 지정 시 해당 이벤트 발생 때도 즉시 재조회 */
export function usePolling<T>(path: string, intervalMs: number, listenEvent?: string): UseApiResult<T> {
  const result = useApi<T>(path);

  useEffect(() => {
    const id = setInterval(result.refetch, intervalMs);
    return () => clearInterval(id);
  }, [result.refetch, intervalMs]);

  useEffect(() => {
    if (!listenEvent) return;
    const handler = () => result.refetch();
    window.addEventListener(listenEvent, handler);
    return () => window.removeEventListener(listenEvent, handler);
  }, [listenEvent, result.refetch]);

  return result;
}
