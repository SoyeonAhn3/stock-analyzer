import { useTheme } from '../theme/ThemeProvider';
import { FONTS, FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';
import type { FullAnalysisResponse } from '../types/api';

interface Props {
  data: FullAnalysisResponse;
}

type Sentiment = 'bullish' | 'positive' | 'bearish' | 'negative' | 'neutral' | 'mixed';

export default function AgentDetailSection({ data }: Props) {
  const { theme } = useTheme();

  const sentimentColor = (val: string | undefined): string => {
    if (!val) return theme.text_muted;
    const v = val.toLowerCase() as Sentiment;
    if (v === 'bullish' || v === 'positive') return theme.up;
    if (v === 'bearish' || v === 'negative') return theme.down;
    return theme.warning;
  };

  const sentimentLabel = (val: string | undefined): string => {
    if (!val) return '--';
    const v = val.toLowerCase();
    if (v === 'bullish' || v === 'positive') return 'Bullish';
    if (v === 'bearish' || v === 'negative') return 'Bearish';
    if (v === 'mixed') return 'Mixed';
    return 'Neutral';
  };

  const { agent_results, cross_validation } = data;
  const news = agent_results?.news;
  const dataAgent = agent_results?.data;
  const macro = agent_results?.macro;

  const cardStyle: React.CSSProperties = {
    background: theme.bg_card,
    border: `1px solid ${theme.border}`,
    borderRadius: RADIUS.card,
    padding: SPACING.lg,
    marginBottom: SPACING.md,
  };

  const labelStyle: React.CSSProperties = {
    color: theme.text_muted,
    fontSize: FONT_SIZES.xs,
    fontWeight: 600,
    letterSpacing: '0.05em',
    marginBottom: SPACING.sm,
  };

  const conflicts = cross_validation?.conflicts ?? [];
  const conflictCount = conflicts.length;

  return (
    <div style={{ marginTop: SPACING.lg }}>
      <div style={labelStyle}>AGENT ANALYSIS DETAILS</div>

      {/* News Agent */}
      <div style={cardStyle}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: SPACING.sm }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: SPACING.sm }}>
            <span style={{ fontSize: FONT_SIZES.lg }}>📰</span>
            <span style={{ color: theme.text_primary, fontSize: FONT_SIZES.md, fontWeight: 600 }}>News Analysis</span>
          </div>
          <SentimentBadge
            label={sentimentLabel(news?.overall_sentiment)}
            color={sentimentColor(news?.overall_sentiment)}
          />
        </div>
        <p style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm, lineHeight: 1.6, margin: 0 }}>
          {news?.summary ?? 'No data available'}
        </p>
      </div>

      {/* Data Agent */}
      <div style={cardStyle}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: SPACING.sm }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: SPACING.sm }}>
            <span style={{ fontSize: FONT_SIZES.lg }}>📊</span>
            <span style={{ color: theme.text_primary, fontSize: FONT_SIZES.md, fontWeight: 600 }}>Financial / Technical Analysis</span>
          </div>
          <SentimentBadge
            label={sentimentLabel(dataAgent?.technicals_summary?.trend)}
            color={sentimentColor(dataAgent?.technicals_summary?.trend)}
          />
        </div>
        <p style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm, lineHeight: 1.6, margin: 0 }}>
          {dataAgent?.summary ?? 'No data available'}
        </p>
      </div>

      {/* Macro Agent */}
      <div style={cardStyle}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: SPACING.sm }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: SPACING.sm }}>
            <span style={{ fontSize: FONT_SIZES.lg }}>🌐</span>
            <span style={{ color: theme.text_primary, fontSize: FONT_SIZES.md, fontWeight: 600 }}>Macro Economy Analysis</span>
          </div>
          <SentimentBadge
            label={sentimentLabel(macro?.market_sentiment)}
            color={sentimentColor(macro?.market_sentiment)}
          />
        </div>
        <p style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm, lineHeight: 1.6, margin: 0 }}>
          {macro?.summary ?? 'No data available'}
        </p>
      </div>

      {/* Cross Validation */}
      {cross_validation && (
        <div style={cardStyle}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: SPACING.sm }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: SPACING.sm }}>
              <span style={{ fontSize: FONT_SIZES.lg }}>⚖️</span>
              <span style={{ color: theme.text_primary, fontSize: FONT_SIZES.md, fontWeight: 600 }}>Cross Validation</span>
            </div>
            <span
              style={{
                color: conflictCount > 0 ? theme.warning : theme.up,
                fontSize: FONT_SIZES.sm,
                fontWeight: 600,
                fontFamily: FONTS.numeric,
              }}
            >
              {conflictCount > 0 ? `${conflictCount} conflict${conflictCount > 1 ? 's' : ''}` : 'No conflicts'}
            </span>
          </div>

          {/* Conflict list */}
          {conflictCount > 0 && (
            <div style={{ marginBottom: SPACING.sm }}>
              {conflicts.map((c, i) => (
                <div
                  key={i}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: SPACING.sm,
                    padding: `${SPACING.xs} 0`,
                    borderBottom: i < conflictCount - 1 ? `1px solid ${theme.border}` : 'none',
                  }}
                >
                  <span
                    style={{
                      fontSize: FONT_SIZES.xs,
                      fontWeight: 600,
                      color: c.severity === 'high' ? theme.down : c.severity === 'medium' ? theme.warning : theme.text_muted,
                      textTransform: 'uppercase',
                      flexShrink: 0,
                      minWidth: 48,
                    }}
                  >
                    {c.severity}
                  </span>
                  <span style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm }}>
                    <strong style={{ color: theme.text_primary }}>{c.topic}</strong> — {c.detail}
                  </span>
                </div>
              ))}
            </div>
          )}

          <p style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm, lineHeight: 1.6, margin: 0 }}>
            {cross_validation.notes ?? '--'}
          </p>
        </div>
      )}
    </div>
  );
}

function SentimentBadge({ label, color }: { label: string; color: string }) {
  return (
    <span
      style={{
        background: `${color}20`,
        color,
        padding: `2px ${SPACING.sm}`,
        borderRadius: RADIUS.badge,
        fontSize: FONT_SIZES.xs,
        fontWeight: 700,
      }}
    >
      {label}
    </span>
  );
}
