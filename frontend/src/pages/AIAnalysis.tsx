import { useParams } from 'react-router-dom';
import { useTheme } from '../theme/ThemeProvider';
import { FONTS, FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';
import { useAnalysis } from '../hooks/useAnalysis';
import { useBreakpoint } from '../hooks/useBreakpoint';

const AGENTS = ['News Agent', 'Data Agent', 'Macro Agent', 'Cross-validation', 'Analyst Agent'];

export default function AIAnalysis() {
  const { ticker } = useParams<{ ticker: string }>();
  const { theme } = useTheme();
  const upperTicker = ticker?.toUpperCase();
  const bp = useBreakpoint();
  const { result, loading, error, trigger } = useAnalysis(upperTicker);

  const verdictColor: Record<string, string> = { BUY: theme.up, HOLD: theme.warning, SELL: theme.down };
  const confidenceColor: Record<string, string> = { high: theme.accent, medium: theme.warning, low: theme.text_muted };

  const cardStyle: React.CSSProperties = {
    background: theme.bg_card,
    border: `1px solid ${theme.border}`,
    borderRadius: RADIUS.card,
    padding: SPACING.lg,
    marginBottom: SPACING.lg,
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <h1 style={{ color: theme.text_primary, fontSize: FONT_SIZES['2xl'], marginBottom: SPACING.lg }}>
        AI Deep Analysis — {upperTicker}
      </h1>

      {/* Start button if not yet triggered */}
      {!result && !loading && (
        <button
          onClick={trigger}
          style={{
            width: '100%',
            padding: SPACING.lg,
            background: theme.accent,
            color: '#FFFFFF',
            borderRadius: RADIUS.button,
            fontSize: FONT_SIZES.lg,
            fontWeight: 700,
            marginBottom: SPACING.lg,
          }}
        >
          Start AI Analysis
        </button>
      )}

      {/* Agent Progress */}
      {loading && (
        <div style={cardStyle}>
          <div style={{ color: theme.text_secondary, fontSize: FONT_SIZES.xs, fontWeight: 600, letterSpacing: '0.05em', marginBottom: SPACING.md }}>
            AGENT PROGRESS
          </div>
          {AGENTS.map((agent, i) => (
            <div
              key={agent}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: SPACING.sm,
                padding: `${SPACING.xs} 0`,
                color: theme.text_secondary,
                fontSize: FONT_SIZES.sm,
              }}
            >
              <span style={{ color: i < 3 ? theme.accent : theme.text_muted }}>
                {i < 3 ? '⟳' : '○'}
              </span>
              {agent}
              <span style={{ marginLeft: 'auto', color: theme.text_muted, fontSize: FONT_SIZES.xs }}>
                {i < 3 ? 'Running...' : 'Waiting'}
              </span>
            </div>
          ))}
          <p style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginTop: SPACING.md }}>
            This may take 1~2 minutes...
          </p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div
          style={{
            background: `${theme.warning}15`,
            border: `1px solid ${theme.warning}`,
            borderRadius: RADIUS.card,
            padding: SPACING.lg,
            color: theme.warning,
            fontSize: FONT_SIZES.sm,
            marginBottom: SPACING.lg,
          }}
        >
          Analysis failed: {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <>
          {/* Verdict */}
          <div style={{ ...cardStyle, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: SPACING.md }}>
              <span
                style={{
                  background: verdictColor[result.verdict] ?? theme.text_muted,
                  color: '#FFFFFF',
                  padding: `${SPACING.sm} ${SPACING.lg}`,
                  borderRadius: RADIUS.badge,
                  fontSize: FONT_SIZES['2xl'],
                  fontWeight: 700,
                  fontFamily: FONTS.numeric,
                }}
              >
                {result.verdict}
              </span>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs }}>CONFIDENCE</div>
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
          </div>

          {/* Bull / Bear Case */}
          {(result.bull_case || result.bear_case) && (
            <div style={{ display: 'grid', gridTemplateColumns: bp === 'mobile' ? '1fr' : '1fr 1fr', gap: SPACING.md, marginBottom: SPACING.lg }}>
              <div style={{ ...cardStyle, borderLeft: `3px solid ${theme.up}`, marginBottom: 0 }}>
                <div style={{ color: theme.up, fontSize: FONT_SIZES.xs, fontWeight: 600, marginBottom: SPACING.sm }}>BULL CASE</div>
                <p style={{ color: theme.text_primary, fontSize: FONT_SIZES.sm, lineHeight: 1.6 }}>
                  {result.bull_case ?? '--'}
                </p>
              </div>
              <div style={{ ...cardStyle, borderLeft: `3px solid ${theme.down}`, marginBottom: 0 }}>
                <div style={{ color: theme.down, fontSize: FONT_SIZES.xs, fontWeight: 600, marginBottom: SPACING.sm }}>BEAR CASE</div>
                <p style={{ color: theme.text_primary, fontSize: FONT_SIZES.sm, lineHeight: 1.6 }}>
                  {result.bear_case ?? '--'}
                </p>
              </div>
            </div>
          )}

          {/* Key Factors */}
          {result.key_factors && result.key_factors.length > 0 && (
            <div style={cardStyle}>
              <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, fontWeight: 600, letterSpacing: '0.05em', marginBottom: SPACING.sm }}>
                KEY FACTORS
              </div>
              <ul style={{ paddingLeft: SPACING.lg }}>
                {result.key_factors.map((f, i) => (
                  <li key={i} style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm, marginBottom: SPACING.xs, listStyle: 'disc' }}>
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Summary */}
          <div style={cardStyle}>
            <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, fontWeight: 600, letterSpacing: '0.05em', marginBottom: SPACING.sm }}>
              ACTION SUMMARY
            </div>
            <p style={{ color: theme.text_primary, fontSize: FONT_SIZES.md, lineHeight: 1.6 }}>
              {result.summary}
            </p>
          </div>

          {/* Disclaimer */}
          <div style={{ borderTop: `1px solid ${theme.border}`, paddingTop: SPACING.md, textAlign: 'center' }}>
            <p style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, lineHeight: 1.6 }}>
              {result.disclaimer ?? 'AI-generated reference only. Not financial advice. Do your own research before making investment decisions.'}
            </p>
          </div>
        </>
      )}
    </div>
  );
}
