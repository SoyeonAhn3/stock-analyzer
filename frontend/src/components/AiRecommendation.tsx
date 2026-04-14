import { useTheme } from '../theme/ThemeProvider';
import { FONTS, FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';
import type { AnalysisResult } from '../types/api';

interface Props {
  result: AnalysisResult | null;
  loading: boolean;
  onTrigger: () => void;
}

export default function AiRecommendation({ result, loading, onTrigger }: Props) {
  const { theme } = useTheme();

  const verdictColor: Record<string, string> = {
    BUY: theme.up,
    HOLD: theme.warning,
    SELL: theme.down,
  };

  const confidenceColor: Record<string, string> = {
    high: theme.accent,
    medium: theme.warning,
    low: theme.text_muted,
  };

  return (
    <div
      style={{
        background: theme.bg_card,
        border: `1px solid ${theme.border}`,
        borderRadius: RADIUS.card,
        padding: SPACING.lg,
      }}
    >
      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: SPACING.md }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: SPACING.md }}>
          {/* AI Icon */}
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: RADIUS.pill,
              background: `${theme.accent}20`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: FONT_SIZES.xl,
            }}
          >
            AI
          </div>
          <span style={{ color: theme.text_primary, fontSize: FONT_SIZES.xl, fontWeight: 700 }}>
            AI Recommendation
          </span>
          {result?.verdict && (
            <span
              style={{
                background: verdictColor[result.verdict] ?? theme.text_muted,
                color: '#FFFFFF',
                padding: `${SPACING.xs} ${SPACING.sm}`,
                borderRadius: RADIUS.badge,
                fontSize: FONT_SIZES.xs,
                fontWeight: 700,
                fontFamily: FONTS.numeric,
              }}
            >
              {result.verdict}
            </span>
          )}
        </div>

        {/* Confidence */}
        {result?.confidence && (
          <div style={{ textAlign: 'right' }}>
            <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginBottom: SPACING.xs }}>
              CONFIDENCE
            </div>
            <span
              style={{
                color: confidenceColor[result.confidence] ?? theme.text_muted,
                fontSize: FONT_SIZES['2xl'],
                fontWeight: 700,
                fontFamily: FONTS.numeric,
              }}
            >
              {result.confidence}
            </span>
          </div>
        )}
      </div>

      {/* Summary */}
      {result?.summary && (
        <p style={{ color: theme.text_secondary, fontSize: FONT_SIZES.md, lineHeight: 1.6, marginBottom: SPACING.md }}>
          {result.summary}
        </p>
      )}

      {/* Trigger button */}
      <button
        onClick={onTrigger}
        disabled={loading}
        style={{
          width: '100%',
          padding: `${SPACING.md} ${SPACING.lg}`,
          background: loading ? theme.text_muted : theme.accent,
          color: '#FFFFFF',
          borderRadius: RADIUS.button,
          fontSize: FONT_SIZES.md,
          fontWeight: 700,
          cursor: loading ? 'not-allowed' : 'pointer',
          transition: 'background 0.15s ease',
        }}
      >
        {loading ? 'Analyzing... (1~2 min)' : 'AI Deep Analysis'}
      </button>

      {/* Disclaimer */}
      {result && (
        <p style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginTop: SPACING.md, textAlign: 'center' }}>
          AI-generated reference. Not financial advice.
        </p>
      )}
    </div>
  );
}
