import { useParams, useNavigate } from 'react-router-dom';
import { useTheme } from '../theme/ThemeProvider';
import { FONT_SIZES, SPACING } from '../theme/tokens';
import { useQuote } from '../hooks/useQuote';
import { useAnalysis } from '../hooks/useAnalysis';
import PriceHeader from '../components/PriceHeader';
import KpiCard from '../components/KpiCard';
import Chart from '../components/Chart';
import TechCards from '../components/TechCard';
import AiRecommendation from '../components/AiRecommendation';
import WatchlistButton from '../components/WatchlistButton';

function formatMarketCap(v: number | null | undefined): string {
  if (!v) return '--';
  if (v >= 1e12) return '$' + (v / 1e12).toFixed(2) + 'T';
  if (v >= 1e9) return '$' + (v / 1e9).toFixed(1) + 'B';
  if (v >= 1e6) return '$' + (v / 1e6).toFixed(0) + 'M';
  return '$' + v.toLocaleString();
}

export default function QuickLook() {
  const { ticker } = useParams<{ ticker: string }>();
  const navigate = useNavigate();
  const { theme } = useTheme();
  const upperTicker = ticker?.toUpperCase();
  const { quote, fundamentals, technicals, loading, error } = useQuote(upperTicker);
  const analysis = useAnalysis(upperTicker);

  if (!ticker) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
        <h1 style={{ color: theme.text_primary, fontSize: FONT_SIZES['2xl'], marginBottom: SPACING.sm }}>
          Quick Look
        </h1>
        <p style={{ color: theme.text_muted, fontSize: FONT_SIZES.sm }}>
          Search a ticker in the sidebar to get started
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.sm, padding: SPACING.xl }}>
        Loading {upperTicker} data...
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          background: `${theme.warning}15`,
          border: `1px solid ${theme.warning}`,
          borderRadius: '8px',
          padding: SPACING.lg,
          color: theme.warning,
          fontSize: FONT_SIZES.sm,
          margin: SPACING.lg,
        }}
      >
        Failed to load data for {upperTicker}: {error}
      </div>
    );
  }

  return (
    <div>
      {/* Price Header + Watchlist */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: SPACING.md }}>
        <PriceHeader ticker={upperTicker!} quote={quote} fundamentals={fundamentals} />
        <WatchlistButton ticker={upperTicker!} />
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'flex', gap: SPACING.md, marginBottom: SPACING.lg, flexWrap: 'wrap' }}>
        <KpiCard label="Market Cap" value={formatMarketCap(fundamentals?.market_cap)} />
        <KpiCard label="P/E Ratio (TTM)" value={fundamentals?.pe?.toFixed(2) ?? '--'} />
        <KpiCard label="EPS (Diluted)" value={fundamentals?.eps ? `$${fundamentals.eps.toFixed(2)}` : '--'} />
        <KpiCard label="Forward P/E" value={fundamentals?.forward_pe?.toFixed(2) ?? '--'} />
      </div>

      {/* Chart + Tech Cards row */}
      <div style={{ display: 'flex', gap: SPACING.lg, marginBottom: SPACING.lg }}>
        <Chart ticker={upperTicker!} />
        <TechCards technicals={technicals} currentPrice={quote?.price} />
      </div>

      {/* AI Recommendation */}
      <AiRecommendation
        result={analysis.result}
        loading={analysis.loading}
        onTrigger={() => {
          analysis.trigger();
          navigate(`/analysis/${upperTicker}`);
        }}
      />
    </div>
  );
}
