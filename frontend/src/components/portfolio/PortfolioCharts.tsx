import React from 'react';
import { useTheme } from '../../theme/ThemeProvider';
import { FONTS, FONT_SIZES, SPACING, RADIUS } from '../../theme/tokens';
import { useBreakpoint } from '../../hooks/useBreakpoint';

interface HoldingData {
  ticker: string;
  weight: number | null;
  pnl_pct: number | null;
}

interface Props {
  holdings: HoldingData[];
}

const CHART_COLORS = [
  '#00D4FF', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
  '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1',
];

function DonutChart({ holdings }: { holdings: HoldingData[] }) {
  const { theme } = useTheme();
  const size = 180;
  const cx = size / 2;
  const cy = size / 2;
  const outerR = 80;
  const innerR = 52;

  const items = holdings.filter((h) => h.weight !== null && h.weight > 0);
  if (items.length === 0) return null;

  const paths: React.ReactElement[] = [];
  let cumAngle = -90;

  items.forEach((item, i) => {
    const angle = ((item.weight ?? 0) / 100) * 360;
    const startRad = (cumAngle * Math.PI) / 180;
    const endRad = ((cumAngle + angle) * Math.PI) / 180;
    const largeArc = angle > 180 ? 1 : 0;
    const color = CHART_COLORS[i % CHART_COLORS.length];

    if (items.length === 1) {
      paths.push(
        <circle key={i} cx={cx} cy={cy} r={outerR} fill={color} />,
        <circle key={`inner-${i}`} cx={cx} cy={cy} r={innerR} fill={theme.bg_card} />,
      );
    } else {
      const x1o = cx + outerR * Math.cos(startRad);
      const y1o = cy + outerR * Math.sin(startRad);
      const x2o = cx + outerR * Math.cos(endRad);
      const y2o = cy + outerR * Math.sin(endRad);
      const x1i = cx + innerR * Math.cos(endRad);
      const y1i = cy + innerR * Math.sin(endRad);
      const x2i = cx + innerR * Math.cos(startRad);
      const y2i = cy + innerR * Math.sin(startRad);

      const d = [
        `M ${x1o} ${y1o}`,
        `A ${outerR} ${outerR} 0 ${largeArc} 1 ${x2o} ${y2o}`,
        `L ${x1i} ${y1i}`,
        `A ${innerR} ${innerR} 0 ${largeArc} 0 ${x2i} ${y2i}`,
        'Z',
      ].join(' ');

      paths.push(<path key={i} d={d} fill={color} />);
    }
    cumAngle += angle;
  });

  return (
    <div style={{ textAlign: 'center' }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {paths}
        <text x={cx} y={cy - 6} textAnchor="middle" fill={theme.text_primary} fontSize="20" fontWeight="700" fontFamily={FONTS.numeric}>
          {items.length}
        </text>
        <text x={cx} y={cy + 14} textAnchor="middle" fill={theme.text_muted} fontSize="11">
          positions
        </text>
      </svg>
      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: SPACING.sm, marginTop: SPACING.sm }}>
        {items.map((item, i) => (
          <div key={item.ticker} style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: FONT_SIZES.xs }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: CHART_COLORS[i % CHART_COLORS.length] }} />
            <span style={{ color: theme.text_secondary }}>{item.ticker}</span>
            <span style={{ color: theme.text_muted, fontFamily: FONTS.numeric }}>{(item.weight ?? 0).toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function ReturnBars({ holdings }: { holdings: HoldingData[] }) {
  const { theme } = useTheme();

  const items = holdings
    .filter((h) => h.pnl_pct !== null)
    .sort((a, b) => (b.pnl_pct ?? 0) - (a.pnl_pct ?? 0));

  if (items.length === 0) return null;

  const maxAbs = Math.max(...items.map((h) => Math.abs(h.pnl_pct ?? 0)), 1);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: SPACING.sm }}>
      {items.map((item) => {
        const pct = item.pnl_pct ?? 0;
        const isPositive = pct >= 0;
        const barWidth = Math.max((Math.abs(pct) / maxAbs) * 100, 2);
        const color = isPositive ? theme.up : theme.down;
        const sign = isPositive ? '+' : '';

        return (
          <div key={item.ticker} style={{ display: 'flex', alignItems: 'center', gap: SPACING.sm }}>
            <span style={{ width: 48, fontSize: FONT_SIZES.xs, color: theme.text_secondary, textAlign: 'right', flexShrink: 0 }}>
              {item.ticker}
            </span>
            <div style={{ flex: 1, height: 20, background: theme.bg_primary, borderRadius: RADIUS.badge, overflow: 'hidden' }}>
              <div
                style={{
                  width: `${barWidth}%`,
                  height: '100%',
                  background: color,
                  borderRadius: RADIUS.badge,
                  opacity: 0.8,
                }}
              />
            </div>
            <span style={{ width: 64, fontSize: FONT_SIZES.xs, fontFamily: FONTS.numeric, color, textAlign: 'right', flexShrink: 0 }}>
              {sign}{pct.toFixed(2)}%
            </span>
          </div>
        );
      })}
    </div>
  );
}

export default function PortfolioCharts({ holdings }: Props) {
  const { theme } = useTheme();
  const bp = useBreakpoint();
  const isMobile = bp === 'mobile';

  const cardBase: React.CSSProperties = {
    background: theme.bg_card,
    border: `1px solid ${theme.border}`,
    borderRadius: RADIUS.card,
    padding: SPACING.lg,
  };

  const labelStyle: React.CSSProperties = {
    color: theme.text_muted,
    fontSize: FONT_SIZES.xs,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    marginBottom: SPACING.md,
  };

  return (
    <div style={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: SPACING.md, marginBottom: SPACING.lg }}>
      <div style={{ ...cardBase, flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ ...labelStyle, alignSelf: 'flex-start' }}>Position Weight</div>
        <DonutChart holdings={holdings} />
      </div>
      <div style={{ ...cardBase, flex: 1 }}>
        <div style={labelStyle}>Return by Position</div>
        <ReturnBars holdings={holdings} />
      </div>
    </div>
  );
}
