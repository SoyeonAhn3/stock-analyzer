import { useTheme } from '../theme/ThemeProvider';
import { FONTS, FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';
import { useBreakpoint } from '../hooks/useBreakpoint';
import type { QuoteResponse, FundamentalsResponse } from '../types/api';

interface Props {
  ticker: string;
  quote: QuoteResponse | null;
  fundamentals: FundamentalsResponse | null;
}

function formatVolume(v: number | null): string {
  if (!v) return '--';
  if (v >= 1e9) return (v / 1e9).toFixed(1) + 'B';
  if (v >= 1e6) return (v / 1e6).toFixed(1) + 'M';
  if (v >= 1e3) return (v / 1e3).toFixed(1) + 'K';
  return v.toString();
}

export default function PriceHeader({ ticker, quote, fundamentals }: Props) {
  const { theme } = useTheme();
  const bp = useBreakpoint();
  const isMobile = bp === 'mobile';
  const price = quote?.price;
  const change = quote?.change ?? 0;
  const changePct = quote?.change_percent ?? 0;
  const isUp = changePct >= 0;
  const w52High = fundamentals?.week52_high;
  const w52Low = fundamentals?.week52_low;
  const rangePos =
    price && w52High && w52Low && w52High !== w52Low
      ? ((price - w52Low) / (w52High - w52Low)) * 100
      : 50;

  return (
    <div style={{ marginBottom: SPACING.lg }}>
      {/* Breadcrumb */}
      <div style={{ fontSize: FONT_SIZES.xs, marginBottom: SPACING.sm, display: 'flex', gap: SPACING.xs }}>
        <span style={{ color: theme.text_muted }}>EQUITIES</span>
        <span style={{ color: theme.text_muted }}>&rsaquo;</span>
        <span style={{ color: theme.text_muted }}>{fundamentals?.sector ?? '--'}</span>
        <span style={{ color: theme.text_muted }}>&rsaquo;</span>
        <span style={{ color: theme.accent }}>{fundamentals?.industry ?? '--'}</span>
      </div>

      {/* Ticker + Price row */}
      <div style={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', justifyContent: 'space-between', alignItems: isMobile ? 'flex-start' : 'flex-start', flexWrap: 'wrap', gap: SPACING.md }}>
        {/* Left: ticker + price */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: SPACING.sm, marginBottom: SPACING.xs }}>
            <span
              style={{
                background: theme.bg_card_hover,
                color: theme.text_primary,
                padding: `${SPACING.xs} ${SPACING.sm}`,
                borderRadius: RADIUS.badge,
                fontSize: FONT_SIZES.sm,
                fontWeight: 700,
                fontFamily: FONTS.numeric,
              }}
            >
              {ticker}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: SPACING.sm, flexWrap: 'wrap' }}>
            <span
              className="numeric"
              style={{ color: theme.text_primary, fontSize: isMobile ? FONT_SIZES['2xl'] : FONT_SIZES['4xl'], fontWeight: 700 }}
            >
              ${price?.toFixed(2) ?? '--'}
            </span>
            <span
              className="numeric"
              style={{ color: isUp ? theme.up : theme.down, fontSize: isMobile ? FONT_SIZES.md : FONT_SIZES.lg, fontWeight: 600 }}
            >
              {isUp ? '+' : ''}
              {changePct.toFixed(2)}% ({isUp ? '+' : ''}${Math.abs(change).toFixed(2)})
            </span>
          </div>
        </div>

        {/* Right: 52W Range + Volume */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: isMobile ? SPACING.md : SPACING.xl, alignItems: 'flex-start' }}>
          {/* 52W Range */}
          <div>
            <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginBottom: SPACING.xs }}>
              52W RANGE
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: SPACING.sm }}>
              <span className="numeric" style={{ color: theme.text_secondary, fontSize: FONT_SIZES.xs }}>
                ${w52Low?.toFixed(2) ?? '--'}
              </span>
              <div
                style={{
                  width: 100,
                  height: 4,
                  background: theme.border,
                  borderRadius: RADIUS.pill,
                  position: 'relative',
                }}
              >
                <div
                  style={{
                    position: 'absolute',
                    left: `${rangePos}%`,
                    top: -3,
                    width: 10,
                    height: 10,
                    borderRadius: RADIUS.pill,
                    background: theme.accent,
                    transform: 'translateX(-50%)',
                  }}
                />
              </div>
              <span className="numeric" style={{ color: theme.text_secondary, fontSize: FONT_SIZES.xs }}>
                ${w52High?.toFixed(2) ?? '--'}
              </span>
            </div>
          </div>

          {/* Volume */}
          <div>
            <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginBottom: SPACING.xs }}>
              VOLUME
            </div>
            <span className="numeric" style={{ color: theme.text_primary, fontSize: isMobile ? FONT_SIZES.md : FONT_SIZES.lg, fontWeight: 700 }}>
              {formatVolume(quote?.volume ?? null)}
            </span>
          </div>

          {/* Data Delayed */}
          <div
            style={{
              background: `${theme.warning}20`,
              color: theme.warning,
              padding: `${SPACING.xs} ${SPACING.sm}`,
              borderRadius: RADIUS.badge,
              fontSize: FONT_SIZES.xs,
              fontWeight: 600,
              whiteSpace: 'nowrap',
              alignSelf: 'center',
            }}
          >
            Data Delayed ~15 min
          </div>
        </div>
      </div>
    </div>
  );
}
