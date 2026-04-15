import { useState, useEffect } from 'react';
import { useTheme } from '../theme/ThemeProvider';
import { FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';
import { API_BASE } from '../config';

interface Props {
  ticker: string;
}

export default function WatchlistButton({ ticker }: Props) {
  const { theme } = useTheme();
  const [inWatchlist, setInWatchlist] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!ticker) return;
    fetch(`${API_BASE}/watchlist`)
      .then((r) => r.json())
      .then((data) => {
        setInWatchlist(data.tickers?.includes(ticker.toUpperCase()) ?? false);
      })
      .catch(() => {});
  }, [ticker]);

  const toggle = () => {
    const upper = ticker.toUpperCase();
    const willAdd = !inWatchlist;

    // Optimistic update
    setInWatchlist(willAdd);
    setLoading(true);

    const url = `${API_BASE}/watchlist/${upper}`;
    const method = willAdd ? 'POST' : 'DELETE';

    fetch(url, { method })
      .then((r) => {
        if (!r.ok) throw new Error();
      })
      .catch(() => {
        // Rollback on failure
        setInWatchlist(!willAdd);
      })
      .finally(() => setLoading(false));
  };

  return (
    <button
      onClick={toggle}
      disabled={loading}
      title={inWatchlist ? 'Remove from Watchlist' : 'Add to Watchlist'}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: SPACING.xs,
        padding: `${SPACING.xs} ${SPACING.sm}`,
        borderRadius: RADIUS.button,
        fontSize: FONT_SIZES.sm,
        fontWeight: 600,
        color: inWatchlist ? theme.warning : theme.text_muted,
        background: inWatchlist ? `${theme.warning}15` : 'transparent',
        border: `1px solid ${inWatchlist ? theme.warning : theme.border}`,
        cursor: loading ? 'not-allowed' : 'pointer',
        transition: 'all 0.15s ease',
      }}
    >
      <span style={{ fontSize: FONT_SIZES.lg }}>{inWatchlist ? '★' : '☆'}</span>
      {inWatchlist ? 'Watching' : 'Watch'}
    </button>
  );
}
