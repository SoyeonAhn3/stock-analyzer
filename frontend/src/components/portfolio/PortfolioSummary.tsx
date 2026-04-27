import { useTheme } from '../../theme/ThemeProvider';
import { FONTS, FONT_SIZES, SPACING, RADIUS } from '../../theme/tokens';
import { useBreakpoint } from '../../hooks/useBreakpoint';

interface Props {
  totalMarketValue: number;
  totalCostBasis: number;
  totalPnl: number;
  totalPnlPct: number;
  best: { ticker: string; pnl_pct: number | null } | null;
  worst: { ticker: string; pnl_pct: number | null } | null;
  holdingsCount: number;
}

function fmt(n: number): string {
  return n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export default function PortfolioSummary({
  totalMarketValue,
  totalCostBasis,
  totalPnl,
  totalPnlPct,
  best,
  worst,
  holdingsCount,
}: Props) {
  const { theme } = useTheme();
  const bp = useBreakpoint();
  const isMobile = bp === 'mobile';

  const pnlColor = totalPnl >= 0 ? theme.up : theme.down;
  const pnlSign = totalPnl >= 0 ? '+' : '';

  const cardBase: React.CSSProperties = {
    background: theme.bg_card,
    border: `1px solid ${theme.border}`,
    borderRadius: RADIUS.card,
    padding: SPACING.lg,
  };

  return (
    <div style={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: SPACING.md, marginBottom: SPACING.lg }}>
      {/* 좌측: 총 평가금액 + 수익 */}
      <div style={{ ...cardBase, flex: 1 }}>
        <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginBottom: SPACING.xs, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
          Total Market Value
        </div>
        <div style={{ fontFamily: FONTS.numeric, fontSize: FONT_SIZES['3xl'], fontWeight: 700, color: theme.text_primary }}>
          ${fmt(totalMarketValue)}
        </div>
        <div style={{ fontFamily: FONTS.numeric, fontSize: FONT_SIZES.md, color: pnlColor, marginTop: SPACING.xs }}>
          {pnlSign}${fmt(Math.abs(totalPnl))} ({pnlSign}{totalPnlPct.toFixed(2)}%)
        </div>
        <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginTop: SPACING.sm }}>
          {holdingsCount} position{holdingsCount !== 1 ? 's' : ''}
        </div>
      </div>

      {/* 우측: 투자원금 + Best/Worst */}
      <div style={{ ...cardBase, flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        <div>
          <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Cost Basis
          </div>
          <div style={{ fontFamily: FONTS.numeric, fontSize: FONT_SIZES['2xl'], fontWeight: 600, color: theme.text_primary, marginTop: SPACING.xs }}>
            ${fmt(totalCostBasis)}
          </div>
        </div>

        <div style={{ marginTop: SPACING.md }}>
          <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Unrealized P&L
          </div>
          <div style={{ fontFamily: FONTS.numeric, fontSize: FONT_SIZES.lg, fontWeight: 600, color: pnlColor, marginTop: SPACING.xs }}>
            {pnlSign}${fmt(Math.abs(totalPnl))} {pnlSign}{totalPnlPct.toFixed(2)}%
          </div>
        </div>

        {(best || worst) && (
          <div style={{ display: 'flex', gap: SPACING.lg, marginTop: SPACING.md, fontSize: FONT_SIZES.xs }}>
            {best && best.pnl_pct !== null && (
              <div>
                <span style={{ color: theme.text_muted }}>BEST </span>
                <span style={{ color: theme.up, fontFamily: FONTS.numeric, fontWeight: 600 }}>
                  {best.ticker} +{best.pnl_pct.toFixed(2)}%
                </span>
              </div>
            )}
            {worst && worst.pnl_pct !== null && (
              <div>
                <span style={{ color: theme.text_muted }}>WORST </span>
                <span style={{ color: theme.down, fontFamily: FONTS.numeric, fontWeight: 600 }}>
                  {worst.ticker} {worst.pnl_pct.toFixed(2)}%
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
