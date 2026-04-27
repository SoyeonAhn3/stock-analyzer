import { useTheme } from '../theme/ThemeProvider';
import { FONT_SIZES, SPACING, TICKER_BAR_HEIGHT, SIDEBAR_WIDTH } from '../theme/tokens';
import { usePolling } from '../hooks/useApi';
import LoadingSkeleton from './LoadingSkeleton';
import type { MarketIndex } from '../types/api';

interface Props {
  compact?: boolean;
}

export default function TickerBar({ compact = false }: Props) {
  const { theme } = useTheme();
  const { data } = usePolling<MarketIndex[]>('/market/indices', 60_000);

  // Mobile: show only 3 key indices
  const displayData = compact ? data?.slice(0, 3) : data;

  return (
    <div
      style={{
        position: 'fixed',
        bottom: 0,
        left: compact ? 0 : SIDEBAR_WIDTH,
        right: 0,
        height: TICKER_BAR_HEIGHT,
        background: theme.bg_card,
        borderTop: `1px solid ${theme.border}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: compact ? 'space-around' : 'flex-start',
        gap: compact ? SPACING.sm : SPACING.lg,
        padding: `0 ${compact ? SPACING.sm : SPACING.lg}`,
        overflowX: 'auto',
        zIndex: 100,
      }}
    >
      {displayData?.map((idx) => (
        <div
          key={idx.symbol}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: SPACING.sm,
            whiteSpace: 'nowrap',
            fontSize: FONT_SIZES.xs,
          }}
        >
          <span style={{ color: theme.text_secondary, fontWeight: 600 }}>
            {idx.symbol}
          </span>
          {!compact && (
            <span className="numeric" style={{ color: theme.text_primary }}>
              {idx.price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          )}
          <span
            className="numeric"
            style={{
              color: (idx.change_percent ?? 0) >= 0 ? theme.up : theme.down,
            }}
          >
            ({(idx.change_percent ?? 0) >= 0 ? '+' : ''}
            {idx.change_percent?.toFixed(2)}%)
          </span>
        </div>
      ))}
      {!data && (
        <div style={{ display: 'flex', gap: SPACING.lg, alignItems: 'center', flex: 1 }}>
          <LoadingSkeleton width="80px" height="16px" count={1} />
          <LoadingSkeleton width="80px" height="16px" count={1} />
          <LoadingSkeleton width="80px" height="16px" count={1} />
        </div>
      )}
    </div>
  );
}
