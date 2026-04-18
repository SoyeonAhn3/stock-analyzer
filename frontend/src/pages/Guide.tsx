import { useState } from 'react';
import { useTheme, type ThemeColors } from '../theme/ThemeProvider';
import { FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';
import { useApi } from '../hooks/useApi';
import LoadingSkeleton from '../components/LoadingSkeleton';
import Chart, { type ChartMarker } from '../components/Chart';

interface ChartExample {
  ticker: string;
  period: string;
  description: string;
  markers?: ChartMarker[];
}

interface Topic {
  title: string;
  level: string;
  what: string;
  how: string;
  when: string;
  example: string;
  chart_example?: ChartExample;
}

interface CategoryData {
  category: string;
  topics: Topic[];
}

const CATEGORY_LABELS: Record<string, string> = {
  chart_basics: 'Chart Basics',
  key_metrics: 'Key Metrics',
  technicals: 'Technical Indicators',
  market_concepts: 'Market Concepts',
  investment_styles: 'Investment Styles',
  us_market_basics: 'US Market Basics',
  psychology: 'Psychology & Mental',
};

function LevelBadge({ level, theme }: { level: string; theme: ThemeColors }) {
  const colorMap: Record<string, string> = {
    beginner: theme.up,
    intermediate: theme.warning,
    advanced: theme.accent,
  };
  const color = colorMap[level] ?? theme.text_muted;

  return (
    <span
      style={{
        background: `${color}20`,
        color,
        padding: `2px ${SPACING.sm}`,
        borderRadius: RADIUS.badge,
        fontSize: FONT_SIZES.xs,
        fontWeight: 600,
      }}
    >
      {level}
    </span>
  );
}

function CategorySection({ categoryKey }: { categoryKey: string }) {
  const { theme } = useTheme();
  const [open, setOpen] = useState(false);
  const { data, loading } = useApi<CategoryData>(`/guide/${categoryKey}`);

  return (
    <div
      style={{
        background: theme.bg_card,
        border: `1px solid ${theme.border}`,
        borderRadius: RADIUS.card,
        marginBottom: SPACING.md,
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <button
        onClick={() => setOpen(!open)}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: SPACING.lg,
          color: theme.text_primary,
          fontSize: FONT_SIZES.lg,
          fontWeight: 600,
        }}
      >
        <span>{open ? '▼' : '▶'} {CATEGORY_LABELS[categoryKey] ?? categoryKey}</span>
        {data && (
          <span style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs }}>
            {data.topics.length} topics
          </span>
        )}
      </button>

      {/* Expanded content */}
      {open && (
        <div style={{ padding: `0 ${SPACING.lg} ${SPACING.lg}` }}>
          {loading && <LoadingSkeleton height="40px" count={3} />}
          {data?.topics.map((topic, idx) => (
            <TopicItem key={idx} topic={topic} theme={theme} />
          ))}
        </div>
      )}
    </div>
  );
}

function TopicItem({ topic, theme }: { topic: Topic; theme: ThemeColors }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      style={{
        borderLeft: `3px solid ${theme.accent}`,
        marginBottom: SPACING.md,
        paddingLeft: SPACING.md,
      }}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: SPACING.sm,
          width: '100%',
          padding: `${SPACING.sm} 0`,
          color: theme.text_primary,
          fontSize: FONT_SIZES.sm,
          fontWeight: 500,
        }}
      >
        <LevelBadge level={topic.level} theme={theme} />
        <span>{topic.title}</span>
        <span style={{ marginLeft: 'auto', color: theme.text_muted, fontSize: FONT_SIZES.xs }}>
          {expanded ? '−' : '+'}
        </span>
      </button>

      {expanded && (
        <div style={{ padding: `${SPACING.sm} 0` }}>
          {(['what', 'how', 'when', 'example'] as const).map((key) => (
            <div key={key} style={{ marginBottom: SPACING.md }}>
              <div
                style={{
                  color: theme.accent,
                  fontSize: FONT_SIZES.xs,
                  fontWeight: 600,
                  letterSpacing: '0.05em',
                  textTransform: 'uppercase',
                  marginBottom: SPACING.xs,
                }}
              >
                {key}
              </div>
              <p style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm, lineHeight: 1.6 }}>
                {topic[key]}
              </p>
            </div>
          ))}

          {/* Chart Example */}
          {topic.chart_example && (
            <div style={{ marginTop: SPACING.md }}>
              <div
                style={{
                  color: theme.accent,
                  fontSize: FONT_SIZES.xs,
                  fontWeight: 600,
                  letterSpacing: '0.05em',
                  textTransform: 'uppercase',
                  marginBottom: SPACING.sm,
                }}
              >
                LIVE CHART
              </div>
              <div
                style={{
                  background: theme.bg_primary,
                  border: `1px solid ${theme.border}`,
                  borderRadius: RADIUS.card,
                  padding: SPACING.md,
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: SPACING.sm,
                    marginBottom: SPACING.sm,
                  }}
                >
                  <span
                    style={{
                      background: `${theme.accent}20`,
                      color: theme.accent,
                      padding: `2px ${SPACING.sm}`,
                      borderRadius: RADIUS.badge,
                      fontSize: FONT_SIZES.xs,
                      fontWeight: 700,
                    }}
                  >
                    {topic.chart_example.ticker}
                  </span>
                  <span style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs }}>
                    {topic.chart_example.period}
                  </span>
                </div>
                <Chart
                  ticker={topic.chart_example.ticker}
                  markers={topic.chart_example.markers}
                  initialPeriod={topic.chart_example.period}
                />
                <p
                  style={{
                    color: theme.warning,
                    fontSize: FONT_SIZES.xs,
                    marginTop: SPACING.sm,
                    lineHeight: 1.5,
                  }}
                >
                  {topic.chart_example.description}
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function Guide() {
  const { theme } = useTheme();
  const { data: categories, loading } = useApi<{ categories: string[] }>('/guide/categories');

  return (
    <div>
      <h1 style={{ color: theme.text_primary, fontSize: FONT_SIZES['2xl'], fontWeight: 700, marginBottom: SPACING.sm }}>
        Beginner's Guide
      </h1>
      <p style={{ color: theme.text_muted, fontSize: FONT_SIZES.sm, marginBottom: SPACING.xl }}>
        Learn stock market basics — charts, metrics, indicators, and investment styles
      </p>

      {loading && <LoadingSkeleton height="60px" count={5} />}

      {categories?.categories.map((cat) => (
        <CategorySection key={cat} categoryKey={cat} />
      ))}
    </div>
  );
}
