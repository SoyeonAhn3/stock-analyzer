import { useState, useEffect, useCallback } from 'react';
import { API_BASE } from '../config';

interface Alert {
  id: number;
  ticker: string;
  target_price: number;
  direction: string;
  created_at?: string;
}

interface TriggeredAlert extends Alert {
  current_price: number;
  triggered_at: string;
}

export function useAlerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [triggered, setTriggered] = useState<TriggeredAlert[]>([]);

  const fetchAlerts = useCallback(() => {
    fetch(`${API_BASE}/alerts`)
      .then((r) => r.json())
      .then((data) => setAlerts(data.alerts ?? []))
      .catch(() => {});
  }, []);

  const checkTriggered = useCallback(() => {
    fetch(`${API_BASE}/alerts/triggered`)
      .then((r) => r.json())
      .then((data) => {
        const newTriggered = data.triggered ?? [];
        if (newTriggered.length > 0) {
          setTriggered((prev) => [...newTriggered, ...prev]);
          fetchAlerts(); // Refresh active alerts
        }
      })
      .catch(() => {});
  }, [fetchAlerts]);

  // Initial fetch
  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  // Poll for triggered alerts every 30s
  useEffect(() => {
    const interval = setInterval(checkTriggered, 30_000);
    return () => clearInterval(interval);
  }, [checkTriggered]);

  const createAlert = (ticker: string, target_price: number, direction: string) => {
    return fetch(`${API_BASE}/alerts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticker, target_price, direction }),
    })
      .then((r) => {
        if (!r.ok) throw new Error();
        fetchAlerts();
      });
  };

  const deleteAlert = (id: number) => {
    return fetch(`${API_BASE}/alerts/${id}`, { method: 'DELETE' })
      .then((r) => {
        if (!r.ok) throw new Error();
        fetchAlerts();
      });
  };

  const dismissTriggered = (index: number) => {
    setTriggered((prev) => prev.filter((_, i) => i !== index));
  };

  return { alerts, triggered, createAlert, deleteAlert, dismissTriggered };
}
