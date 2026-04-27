import { API_BASE } from '../config';

const LS_SYNC_KEY = 'portfolio_sync';

export interface SyncState {
  code: string;
  pin: string;
  last_synced: string | null;
}

export function loadSyncState(): SyncState | null {
  try {
    const raw = localStorage.getItem(LS_SYNC_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function saveSyncState(state: SyncState | null) {
  if (state) {
    localStorage.setItem(LS_SYNC_KEY, JSON.stringify(state));
  } else {
    localStorage.removeItem(LS_SYNC_KEY);
  }
}

async function handleResponse(res: Response) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function createSync(pin: string): Promise<{ code: string }> {
  const res = await fetch(`${API_BASE}/sync/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pin }),
  });
  return handleResponse(res);
}

export async function connectSync(code: string, pin: string): Promise<{ success: boolean }> {
  const res = await fetch(`${API_BASE}/sync/connect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, pin }),
  });
  return handleResponse(res);
}

export async function pushSync(code: string, pin: string, data: string): Promise<{ success: boolean; updated_at: string }> {
  const res = await fetch(`${API_BASE}/sync/push`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, pin, data }),
  });
  return handleResponse(res);
}

export async function pullSync(code: string, pin: string): Promise<{ success: boolean; data: string; updated_at: string }> {
  const res = await fetch(`${API_BASE}/sync/pull`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, pin }),
  });
  return handleResponse(res);
}

export async function disconnectSync(code: string, pin: string): Promise<{ success: boolean }> {
  const res = await fetch(`${API_BASE}/sync/disconnect`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, pin }),
  });
  return handleResponse(res);
}
