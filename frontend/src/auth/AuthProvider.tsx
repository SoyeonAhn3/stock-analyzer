import { createContext, useContext, useState, useMemo, useCallback } from 'react';
import type { ReactNode } from 'react';
import { googleLogout } from '@react-oauth/google';

/**
 * Phase 14 무료체험 인증 — Google ID 토큰 보관/디코드.
 *
 * 로그인 시 받은 Google ID 토큰(credential, JWT)을 localStorage에 보관하고,
 * API 호출 시 `Authorization: Bearer <token>`로 전송한다. 토큰은 백엔드에서
 * 검증하므로 프론트는 표시용으로만 payload를 디코드한다(서명 검증 안 함).
 */

const TOKEN_KEY = 'quantai_token';

export interface AuthUser {
  sub: string;
  email?: string;
  name?: string;
  picture?: string;
}

interface AuthContextValue {
  token: string | null;
  user: AuthUser | null;
  isLoggedIn: boolean;
  login: (credential: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

/** JWT payload 디코드 (base64url + UTF-8). 표시용 — 검증은 백엔드가 한다. */
function decodeJwt(token: string): Record<string, any> | null {
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    const json = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + c.charCodeAt(0).toString(16).padStart(2, '0'))
        .join('')
    );
    return JSON.parse(json);
  } catch {
    return null;
  }
}

/** localStorage에서 만료되지 않은 토큰만 로드. 만료/손상 시 제거. */
function loadValidToken(): string | null {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return null;
  const payload = decodeJwt(token);
  if (!payload || (payload.exp && payload.exp * 1000 < Date.now())) {
    localStorage.removeItem(TOKEN_KEY);
    return null;
  }
  return token;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(loadValidToken);

  const login = useCallback((credential: string) => {
    localStorage.setItem(TOKEN_KEY, credential);
    setToken(credential);
  }, []);

  const logout = useCallback(() => {
    googleLogout();
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
  }, []);

  const user = useMemo<AuthUser | null>(() => {
    if (!token) return null;
    const p = decodeJwt(token);
    if (!p) return null;
    return { sub: p.sub, email: p.email, name: p.name, picture: p.picture };
  }, [token]);

  const value = useMemo<AuthContextValue>(
    () => ({ token, user, isLoggedIn: !!token, login, logout }),
    [token, user, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/** 어디서든 인증 상태 접근: const { user, token, isLoggedIn, login, logout } = useAuth() */
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
