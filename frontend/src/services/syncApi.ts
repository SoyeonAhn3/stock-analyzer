import { API_BASE } from '../config';

const SESSION_KEY = 'portfolio_session';
const REMEMBER_KEY = 'portfolio_remember';

export function saveSession(code: string, pin: string): void {
  sessionStorage.setItem(SESSION_KEY, JSON.stringify({ code, pin }));
}

export function loadSession(): { code: string; pin: string } | null {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function clearSession(): void {
  sessionStorage.removeItem(SESSION_KEY);
}

export function saveRememberedCode(code: string): void {
  localStorage.setItem(REMEMBER_KEY, JSON.stringify({ code }));
}

export function loadRememberedCode(): string | null {
  try {
    const raw = localStorage.getItem(REMEMBER_KEY);
    return raw ? JSON.parse(raw).code : null;
  } catch {
    return null;
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
