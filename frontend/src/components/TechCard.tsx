import { useTheme } from '../theme/ThemeProvider';
import { FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';
import SignalBadge from './SignalBadge';
import type { TechnicalsResponse } from '../types/api';

interface Props {
  technicals: TechnicalsResponse | null;
  currentPrice?: number;
}

export default function TechCards({ technicals, currentPrice }: Props) {
  const { theme } = useTheme();
  if (!technicals) return null;

  const cardStyle: React.CSSProperties = {
    background: theme.bg_card,
    border: `1px solid ${theme.border}`,
    borderRadius: RADIUS.card,
    padding: SPACING.md,
    flex: 1,
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: SPACING.md, minWidth: 220 }}>
      {/* RSI */}
      {technicals.rsi && (
        <div style={cardStyle}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: SPACING.sm }}>
            <span style={{ color: theme.text_secondary, fontSize: FONT_SIZES.xs, fontWeight: 600 }}>RSI (14)</span>
            <SignalBadge signal={technicals.rsi.signal} />
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: SPACING.sm, marginBottom: SPACING.sm }}>
            <span className="numeric" style={{ color: theme.text_primary, fontSize: FONT_SIZES['2xl'], fontWeight: 700 }}>
              {technicals.rsi.value.toFixed(1)}
            </span>
            <span style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs }}>
              {technicals.rsi.value >= 70 ? 'OVERBOUGHT' : technicals.rsi.value <= 30 ? 'OVERSOLD' : 'NEUTRAL-BULL'}
            </span>
          </div>
          {/* Gauge bar */}
          <div style={{ height: 4, background: theme.border, borderRadius: RADIUS.pill, position: 'relative' }}>
            <div
              style={{
                position: 'absolute',
                left: 0,
                top: 0,
                height: '100%',
                width: `${Math.min(technicals.rsi.value, 100)}%`,
                background: `linear-gradient(90deg, ${theme.up}, ${theme.warning}, ${theme.down})`,
                borderRadius: RADIUS.pill,
              }}
            />
            <div
              style={{
                position: 'absolute',
                left: `${Math.min(technicals.rsi.value, 100)}%`,
                top: -3,
                width: 10,
                height: 10,
                borderRadius: RADIUS.pill,
                background: theme.accent,
                transform: 'translateX(-50%)',
              }}
            />
          </div>
        </div>
      )}

      {/* MACD */}
      {technicals.macd && (
        <div style={cardStyle}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: SPACING.sm }}>
            <span style={{ color: theme.text_secondary, fontSize: FONT_SIZES.xs, fontWeight: 600 }}>MACD</span>
            <SignalBadge signal={technicals.macd.signal} />
          </div>
          <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginBottom: SPACING.xs }}>HISTOGRAM</div>
          <span
            className="numeric"
            style={{
              color: technicals.macd.histogram >= 0 ? theme.up : theme.down,
              fontSize: FONT_SIZES.xl,
              fontWeight: 700,
            }}
          >
            {technicals.macd.histogram >= 0 ? 'Positive' : 'Negative'}
          </span>
        </div>
      )}

      {/* Bollinger Bands */}
      {technicals.bollinger && (
        <div style={cardStyle}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: SPACING.sm }}>
            <span style={{ color: theme.text_secondary, fontSize: FONT_SIZES.xs, fontWeight: 600 }}>BOLLINGER BANDS</span>
            <SignalBadge signal={technicals.bollinger.signal} />
          </div>
          {(['upper', 'middle', 'lower'] as const).map((band) => {
            const val = technicals.bollinger![band];
            const isClosest =
              currentPrice &&
              Math.abs(currentPrice - val) ===
                Math.min(
                  Math.abs(currentPrice - technicals.bollinger!.upper),
                  Math.abs(currentPrice - technicals.bollinger!.middle),
                  Math.abs(currentPrice - technicals.bollinger!.lower),
                );
            return (
              <div
                key={band}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  padding: `${SPACING.xs} 0`,
                }}
              >
                <span style={{ color: isClosest ? theme.accent : theme.text_secondary, fontSize: FONT_SIZES.sm, textTransform: 'capitalize' }}>
                  {band}
                </span>
                <span
                  className="numeric"
                  style={{
                    color: isClosest ? theme.accent : theme.text_primary,
                    fontSize: FONT_SIZES.sm,
                    fontWeight: isClosest ? 700 : 400,
                  }}
                >
                  {val.toFixed(2)}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
