import { useState, useEffect, useCallback } from 'react';
import { useTheme } from '../theme/ThemeProvider';
import { FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';
import { API_BASE } from '../config';
import { useAuth } from '../auth/AuthProvider';
import LoginButton from './LoginButton';

/**
 * 사이드바 무료체험 배너 — Phase 14.
 *
 * 비로그인: 로그인 유도 + Google 로그인 버튼.
 * 로그인: 유저 + 잔여 무료 횟수 + 프로그레스바 + 로그아웃.
 * 분석 성공 시 useAnalysis가 'trial-changed' 이벤트를 dispatch → 잔여 횟수 갱신.
 */

const FREE_TOTAL = 3; // 계정당 무료 제공량 (백엔드 INITIAL_CREDITS)

interface TrialStatus {
  balance: number;
  held: number;
  available: number;
}

export default function TrialBanner() {
  const { theme } = useTheme();
  const { token, user, isLoggedIn, logout } = useAuth();
  const [status, setStatus] = useState<TrialStatus | null>(null);

  const refresh = useCallback(() => {
    if (!token) {
      setStatus(null);
      return;
    }
    fetch(`${API_BASE}/trial/status`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (d) setStatus(d);
      })
      .catch(() => {});
  }, [token]);

  useEffect(() => {
    refresh();
    window.addEventListener('trial-changed', refresh);
    return () => window.removeEventListener('trial-changed', refresh);
  }, [refresh]);

  // ── 비로그인 ──
  if (!isLoggedIn) {
    return (
      <div style={{ marginBottom: SPACING.md }}>
        <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginBottom: SPACING.sm, lineHeight: 1.5 }}>
          Sign in for <strong style={{ color: theme.text_secondary }}>3 free</strong> AI analyses
        </div>
        <LoginButton size="medium" />
      </div>
    );
  }

  // ── 로그인 ──
  const remaining = status?.available ?? FREE_TOTAL;
  const pct = Math.max(0, Math.min(100, (remaining / FREE_TOTAL) * 100));

  return (
    <div style={{ marginBottom: SPACING.md }}>
      {/* User row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: SPACING.sm, marginBottom: SPACING.sm }}>
        {user?.picture && (
          <img src={user.picture} alt="" referrerPolicy="no-referrer" style={{ width: 24, height: 24, borderRadius: '50%' }} />
        )}
        <div
          style={{
            flex: 1,
            minWidth: 0,
            color: theme.text_primary,
            fontSize: FONT_SIZES.sm,
            fontWeight: 600,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
          title={user?.email}
        >
          {user?.name ?? user?.email ?? 'Signed in'}
        </div>
        <button
          onClick={logout}
          title="Sign out"
          style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, padding: SPACING.xs }}
        >
          Logout
        </button>
      </div>

      {/* Remaining count */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          color: theme.text_muted,
          fontSize: FONT_SIZES.xs,
          marginBottom: SPACING.xs,
        }}
      >
        <span>FREE TRIAL</span>
        <span className="numeric">{remaining}/{FREE_TOTAL} left</span>
      </div>
      <div style={{ height: '4px', background: theme.border, borderRadius: RADIUS.pill, overflow: 'hidden' }}>
        <div
          style={{
            width: `${pct}%`,
            height: '100%',
            background: remaining > 0 ? theme.accent : theme.warning,
            borderRadius: RADIUS.pill,
            transition: 'width 0.3s ease',
          }}
        />
      </div>
    </div>
  );
}
