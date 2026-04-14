import { useEffect } from 'react';
import { useTheme } from '../theme/ThemeProvider';
import { FONTS, FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';

interface TriggeredAlert {
  ticker: string;
  target_price: number;
  direction: string;
  current_price: number;
}

interface Props {
  alerts: TriggeredAlert[];
  onDismiss: (index: number) => void;
}

export default function AlertToast({ alerts, onDismiss }: Props) {
  const { theme } = useTheme();

  // Auto-dismiss after 8 seconds
  useEffect(() => {
    if (alerts.length === 0) return;
    const timer = setTimeout(() => onDismiss(0), 8000);
    return () => clearTimeout(timer);
  }, [alerts, onDismiss]);

  if (alerts.length === 0) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: SPACING.lg,
        right: SPACING.lg,
        zIndex: 400,
        display: 'flex',
        flexDirection: 'column',
        gap: SPACING.sm,
        maxWidth: 320,
      }}
    >
      {alerts.slice(0, 3).map((alert, i) => (
        <div
          key={`${alert.ticker}-${i}`}
          style={{
            background: theme.bg_card,
            border: `1px solid ${alert.direction === 'above' ? theme.up : theme.down}`,
            borderRadius: RADIUS.card,
            padding: SPACING.md,
            boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
            animation: 'slideIn 0.3s ease-out',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: SPACING.xs }}>
            <span style={{ color: alert.direction === 'above' ? theme.up : theme.down, fontSize: FONT_SIZES.sm, fontWeight: 700 }}>
              Price Alert
            </span>
            <button
              onClick={() => onDismiss(i)}
              style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, padding: '2px 6px' }}
            >
              Dismiss
            </button>
          </div>
          <div style={{ color: theme.text_primary, fontSize: FONT_SIZES.md, fontWeight: 700, fontFamily: FONTS.numeric }}>
            {alert.ticker} reached ${alert.current_price.toFixed(2)}
          </div>
          <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginTop: SPACING.xs }}>
            Target: {alert.direction} ${alert.target_price.toFixed(2)}
          </div>
        </div>
      ))}
      <style>{`
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `}</style>
    </div>
  );
}
