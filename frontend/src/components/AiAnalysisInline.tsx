import { useTheme } from '../theme/ThemeProvider';
import { FONTS, FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';
import { useBreakpoint } from '../hooks/useBreakpoint';
import AgentDetailSection from './AgentDetailSection';
import type { AnalysisResult, FullAnalysisResponse } from '../types/api';

interface Props {
  result: AnalysisResult | null;
  fullResponse: FullAnalysisResponse | null;
  loading: boolean;
  error: string | null;
  cachedAt: string | null;
  onTrigger: (force?: boolean) => void;
}

function timeAgo(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

const AGENTS = ['News Agent', 'Data Agent', 'Macro Agent', 'Cross-validation', 'Analyst Agent'];

export default function AiAnalysisInline({ result, fullResponse, loading, error, cachedAt, onTrigger }: Props) {
  const { theme } = useTheme();
  const bp = useBreakpoint();

  const verdictColor: Record<string, string> = { BUY: theme.up, HOLD: theme.warning, SELL: theme.down };
  const confidenceColor: Record<string, string> = { high: theme.accent, medium: theme.warning, low: theme.text_muted };

  const cardStyle: React.CSSProperties = {
    background: theme.bg_card,
    border: `1px solid ${theme.border}`,
    borderRadius: RADIUS.card,
    padding: SPACING.lg,
    marginBottom: SPACING.lg,
  };

  const sectionLabel: React.CSSProperties = {
    color: theme.text_muted,
    fontSize: FONT_SIZES.xs,
    fontWeight: 600,
    letterSpacing: '0.05em',
    marginBottom: SPACING.sm,
  };

  return (
    <div style={{ marginTop: SPACING.lg, borderTop: `1px solid ${theme.border}`, paddingTop: SPACING.lg }}>
      {/* Section header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: SPACING.md }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: SPACING.sm }}>
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: RADIUS.pill,
              background: `${theme.accent}20`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: FONT_SIZES.sm,
              fontWeight: 700,
              color: theme.accent,
            }}
          >
            AI
          </div>
          <span style={{ color: theme.text_primary, fontSize: FONT_SIZES.xl, fontWeight: 700 }}>
            AI Deep Analysis
          </span>
        </div>

        {/* Re-analyze button (shown when result exists) */}
        {result && !loading && (
          <button
            onClick={() => {
              if (window.confirm('AI 호출 5회가 발생합니다 (일일 한도 차감). 진행할까요?')) {
                onTrigger(true);
              }
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: SPACING.xs,
              padding: `${SPACING.xs} ${SPACING.md}`,
              background: 'transparent',
              border: `1px solid ${theme.border}`,
              borderRadius: RADIUS.button,
              color: theme.text_secondary,
              fontSize: FONT_SIZES.sm,
              cursor: 'pointer',
            }}
          >
            ↻ Re-analyze
          </button>
        )}
      </div>

      {/* Trigger button — only when no result and not loading */}
      {!result && !loading && (
        <button
          onClick={() => onTrigger(false)}
          style={{
            width: '100%',
            padding: SPACING.lg,
            background: theme.accent,
            color: '#FFFFFF',
            borderRadius: RADIUS.button,
            fontSize: FONT_SIZES.lg,
            fontWeight: 700,
            cursor: 'pointer',
          }}
        >
          Start AI Analysis
        </button>
      )}

      {/* Loading */}
      {loading && (
        <div style={cardStyle}>
          <div style={sectionLabel}>AGENT PROGRESS</div>
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
          {/* Verdict + Confidence */}
          <div style={{ ...cardStyle, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
              <div style={sectionLabel}>KEY FACTORS</div>
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
            <div style={sectionLabel}>ACTION SUMMARY</div>
            <p style={{ color: theme.text_primary, fontSize: FONT_SIZES.md, lineHeight: 1.6 }}>
              {result.summary}
            </p>
          </div>

          {/* Agent Details (#3) */}
          {fullResponse && <AgentDetailSection data={fullResponse} />}

          {/* Last analyzed + Disclaimer */}
          <div style={{ borderTop: `1px solid ${theme.border}`, paddingTop: SPACING.md, textAlign: 'center' }}>
            {cachedAt && (
              <p style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginBottom: SPACING.xs }}>
                Last analyzed: {timeAgo(cachedAt)}
              </p>
            )}
            <p style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, lineHeight: 1.6 }}>
              {result.disclaimer ?? 'AI-generated reference only. Not financial advice. Do your own research before making investment decisions.'}
            </p>
          </div>
        </>
      )}
    </div>
  );
}
