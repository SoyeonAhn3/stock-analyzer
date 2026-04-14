import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTheme } from '../theme/ThemeProvider';
import { FONT_SIZES, SPACING, RADIUS, SIDEBAR_WIDTH } from '../theme/tokens';
import { usePolling } from '../hooks/useApi';
import { useAlerts } from '../hooks/useAlerts';
import type { WatchlistResponse } from '../types/api';
import SearchAutocomplete from './SearchAutocomplete';
import AlertModal from './AlertModal';

const MENU_ITEMS = [
  { label: 'Market Overview', path: '/' },
  { label: 'Quick Look', path: '/quick-look' },
  { label: 'Compare Mode', path: '/compare' },
  { label: 'Sector Screening', path: '/sector' },
  { label: "Beginner's Guide", path: '/guide' },
];

export default function Sidebar() {
  const { theme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [alertTicker, setAlertTicker] = useState<string | null>(null);

  const { data: watchlist } = usePolling<WatchlistResponse>('/watchlist', 60_000);
  const { createAlert } = useAlerts();

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <>
    <aside
      style={{
        width: SIDEBAR_WIDTH,
        minWidth: SIDEBAR_WIDTH,
        height: '100vh',
        background: theme.bg_card,
        borderRight: `1px solid ${theme.border}`,
        display: 'flex',
        flexDirection: 'column',
        padding: `${SPACING.lg} 0`,
        position: 'fixed',
        left: 0,
        top: 0,
        zIndex: 100,
        overflowY: 'auto',
      }}
    >
      {/* Logo */}
      <div style={{ padding: `0 ${SPACING.lg}`, marginBottom: SPACING.lg }}>
        <div style={{ color: theme.accent, fontSize: FONT_SIZES.xl, fontWeight: 700 }}>
          QuantAI
        </div>
        <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs }}>
          Institutional Grade
        </div>
      </div>

      {/* Search */}
      <div style={{ padding: `0 ${SPACING.lg}`, marginBottom: SPACING.lg }}>
        <SearchAutocomplete />
      </div>

      {/* Menu */}
      <nav style={{ marginBottom: SPACING.lg }}>
        {MENU_ITEMS.map((item) => (
          <button
            key={item.path}
            onClick={() => navigate(item.path)}
            style={{
              display: 'flex',
              alignItems: 'center',
              width: '100%',
              padding: `${SPACING.sm} ${SPACING.lg}`,
              color: isActive(item.path) ? theme.accent : theme.text_secondary,
              fontSize: FONT_SIZES.sm,
              fontWeight: isActive(item.path) ? 600 : 400,
              borderLeft: isActive(item.path) ? `3px solid ${theme.accent}` : '3px solid transparent',
              transition: 'all 0.15s ease',
            }}
          >
            {item.label}
          </button>
        ))}
      </nav>

      {/* Watchlist */}
      <div style={{ padding: `0 ${SPACING.lg}`, flex: 1 }}>
        <div
          style={{
            color: theme.text_muted,
            fontSize: FONT_SIZES.xs,
            fontWeight: 600,
            letterSpacing: '0.05em',
            marginBottom: SPACING.sm,
          }}
        >
          REAL-TIME WATCHLIST
        </div>
        {watchlist?.quotes?.map((q) => (
          <div
            key={q.ticker}
            style={{
              display: 'flex',
              alignItems: 'center',
              width: '100%',
              padding: `${SPACING.xs} 0`,
              fontSize: FONT_SIZES.sm,
            }}
          >
            <button
              onClick={() => navigate(`/quick-look/${q.ticker}`)}
              style={{ color: theme.text_primary, fontWeight: 500, flex: 1, textAlign: 'left' }}
            >
              {q.ticker}
            </button>
            <span
              className="numeric"
              style={{
                color: (q.change_percent ?? 0) >= 0 ? theme.up : theme.down,
                marginRight: SPACING.xs,
              }}
            >
              {(q.change_percent ?? 0) >= 0 ? '+' : ''}
              {q.change_percent?.toFixed(2)}%
            </span>
            <button
              onClick={() => setAlertTicker(q.ticker)}
              title="Set price alert"
              style={{
                color: theme.text_muted,
                fontSize: FONT_SIZES.xs,
                padding: '2px',
                borderRadius: RADIUS.badge,
                opacity: 0.6,
              }}
            >
              🔔
            </button>
          </div>
        ))}
        {(!watchlist?.quotes || watchlist.quotes.length === 0) && (
          <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs }}>
            No tickers yet
          </div>
        )}
      </div>

      {/* Bottom: AI Usage + Settings */}
      <div style={{ padding: `0 ${SPACING.lg}`, marginTop: 'auto' }}>
        {/* AI Usage */}
        <div style={{ marginBottom: SPACING.md }}>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              color: theme.text_muted,
              fontSize: FONT_SIZES.xs,
              marginBottom: SPACING.xs,
            }}
          >
            <span>AI USAGE</span>
            <span className="numeric">0/100</span>
          </div>
          <div
            style={{
              height: '4px',
              background: theme.border,
              borderRadius: RADIUS.pill,
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                width: '0%',
                height: '100%',
                background: theme.accent,
                borderRadius: RADIUS.pill,
                transition: 'width 0.3s ease',
              }}
            />
          </div>
        </div>

        {/* Settings */}
        <button
          onClick={() => navigate('/settings')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: SPACING.sm,
            color: theme.text_secondary,
            fontSize: FONT_SIZES.sm,
            padding: `${SPACING.sm} 0`,
          }}
        >
          Settings
        </button>
      </div>
    </aside>

    {/* Alert Modal */}
    {alertTicker && (
      <AlertModal
        ticker={alertTicker}
        onClose={() => setAlertTicker(null)}
        onCreate={createAlert}
      />
    )}
    </>
  );
}
