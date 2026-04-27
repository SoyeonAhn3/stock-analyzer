import { useTheme } from '../../theme/ThemeProvider';
import { FONTS, FONT_SIZES, SPACING, RADIUS } from '../../theme/tokens';
import { useBreakpoint } from '../../hooks/useBreakpoint';

interface Props {
  ticker: string;
  shares: number;
  avgCost: number;
  currentPrice: number | null;
  marketValue: number | null;
  costBasis: number;
  pnl: number | null;
  pnlPct: number | null;
  weight: number | null;
  onEdit?: () => void;
  onDelete?: () => void;
}

function fmt(n: number): string {
  return n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export default function HoldingCard({
  ticker,
  shares,
  avgCost,
  currentPrice,
  marketValue,
  costBasis,
  pnl,
  pnlPct,
  weight,
  onEdit,
  onDelete,
}: Props) {
  const { theme } = useTheme();
  const bp = useBreakpoint();
  const isMobile = bp === 'mobile';

  const pnlColor = (pnl ?? 0) >= 0 ? theme.up : theme.down;
  const pnlSign = (pnl ?? 0) >= 0 ? '+' : '';

  return (
    <div
      style={{
        background: theme.bg_card,
        border: `1px solid ${theme.border}`,
        borderRadius: RADIUS.card,
        padding: isMobile ? SPACING.md : SPACING.lg,
        display: 'flex',
        flexDirection: isMobile ? 'column' : 'row',
        alignItems: isMobile ? 'stretch' : 'center',
        gap: isMobile ? SPACING.sm : SPACING.lg,
        marginBottom: SPACING.sm,
      }}
    >
      {/* 티커 + 수량 */}
      <div style={{ minWidth: isMobile ? 'auto' : 100 }}>
        <div style={{ fontSize: FONT_SIZES.lg, fontWeight: 700, color: theme.accent }}>{ticker}</div>
        <div style={{ fontSize: FONT_SIZES.xs, color: theme.text_muted, fontFamily: FONTS.numeric }}>
          {shares} shares @ ${fmt(avgCost)}
        </div>
      </div>

      {/* 현재가 + 평가금액 */}
      <div style={{ flex: 1, display: 'flex', flexDirection: isMobile ? 'row' : 'column', justifyContent: isMobile ? 'space-between' : 'center', gap: isMobile ? 0 : '2px' }}>
        {currentPrice !== null ? (
          <>
            <div style={{ fontSize: FONT_SIZES.md, fontFamily: FONTS.numeric, color: theme.text_primary, fontWeight: 600 }}>
              ${fmt(currentPrice)}
            </div>
            <div style={{ fontSize: FONT_SIZES.xs, fontFamily: FONTS.numeric, color: theme.text_muted }}>
              MV ${fmt(marketValue ?? 0)}
            </div>
          </>
        ) : (
          <div style={{ fontSize: FONT_SIZES.sm, color: theme.text_muted }}>Price unavailable</div>
        )}
      </div>

      {/* 수익/손실 */}
      <div style={{ minWidth: isMobile ? 'auto' : 120, textAlign: isMobile ? 'left' : 'right' }}>
        {pnl !== null ? (
          <>
            <div style={{ fontSize: FONT_SIZES.md, fontFamily: FONTS.numeric, fontWeight: 600, color: pnlColor }}>
              {pnlSign}${fmt(Math.abs(pnl))}
            </div>
            <div style={{ fontSize: FONT_SIZES.xs, fontFamily: FONTS.numeric, color: pnlColor }}>
              {pnlSign}{(pnlPct ?? 0).toFixed(2)}%
            </div>
          </>
        ) : (
          <div style={{ fontSize: FONT_SIZES.sm, color: theme.text_muted }}>—</div>
        )}
      </div>

      {/* 비중 */}
      <div style={{ minWidth: isMobile ? 'auto' : 60, textAlign: isMobile ? 'left' : 'right' }}>
        {weight !== null && (
          <div style={{ fontSize: FONT_SIZES.xs, fontFamily: FONTS.numeric, color: theme.text_secondary }}>
            {weight.toFixed(1)}%
          </div>
        )}
      </div>

      {/* 수정/삭제 버튼 */}
      <div style={{ display: 'flex', gap: SPACING.xs, flexShrink: 0 }}>
        {onEdit && (
          <button
            onClick={onEdit}
            style={{
              padding: `${SPACING.xs} ${SPACING.sm}`,
              fontSize: FONT_SIZES.xs,
              color: theme.text_secondary,
              border: `1px solid ${theme.border}`,
              borderRadius: RADIUS.button,
              background: 'transparent',
              cursor: 'pointer',
            }}
          >
            Edit
          </button>
        )}
        {onDelete && (
          <button
            onClick={onDelete}
            style={{
              padding: `${SPACING.xs} ${SPACING.sm}`,
              fontSize: FONT_SIZES.xs,
              color: theme.down,
              border: `1px solid ${theme.border}`,
              borderRadius: RADIUS.button,
              background: 'transparent',
              cursor: 'pointer',
            }}
          >
            Del
          </button>
        )}
      </div>
    </div>
  );
}
