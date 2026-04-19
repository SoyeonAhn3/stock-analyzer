import { useNavigate } from 'react-router-dom';
import { useTheme } from '../theme/ThemeProvider';
import { FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';
import { useApi, usePolling } from '../hooks/useApi';
import { useBreakpoint } from '../hooks/useBreakpoint';
import LoadingSkeleton from '../components/LoadingSkeleton';
import ErrorBanner from '../components/ErrorBanner';
import Tooltip from '../components/Tooltip';

interface Mover {
  ticker: string;
  name: string;
  change_pct: number;
  price: number;
  volume: number;
}

interface MoversResponse {
  gainers: Mover[];
  losers: Mover[];
}

interface NewsItem {
  headline: string;
  source: string;
  url: string;
  datetime: number;
}

export default function MarketOverview() {
  const { theme } = useTheme();
  const navigate = useNavigate();
  const bp = useBreakpoint();
  const movers = useApi<MoversResponse>('/market/movers');
  const news = usePolling<NewsItem[]>('/market/news', 300_000);

  const cardStyle: React.CSSProperties = {
    background: theme.bg_card,
    border: `1px solid ${theme.border}`,
    borderRadius: RADIUS.card,
    padding: SPACING.lg,
  };

  return (
    <div>
      {/* Welcome */}
      <div style={{ marginBottom: SPACING.xl }}>
        <h1 style={{ color: theme.text_primary, fontSize: FONT_SIZES['2xl'], fontWeight: 700, marginBottom: SPACING.xs }}>
          Welcome to QuantAI
        </h1>
        <p style={{ color: theme.text_muted, fontSize: FONT_SIZES.sm }}>
          Real-time US stock analysis dashboard powered by Multi-Agent AI
        </p>
      </div>

      {movers.error && <ErrorBanner message="Failed to load market movers" onRetry={movers.refetch} />}
      {news.error && <ErrorBanner message="Failed to load market news" onRetry={news.refetch} />}

      {/* Responsive grid */}
      <div style={{ display: 'grid', gridTemplateColumns: bp === 'mobile' ? '1fr' : '1fr 1fr', gap: SPACING.lg }}>
        {/* Movers */}
        <div style={cardStyle}>
          <div style={{ display: 'flex', alignItems: 'center', gap: SPACING.sm, color: theme.text_muted, fontSize: FONT_SIZES.xs, fontWeight: 600, letterSpacing: '0.05em', marginBottom: SPACING.md }}>
            TODAY'S MOVERS
            <Tooltip text="Mid-cap and above (Market Cap $2B+). Ranked by daily price change %. Data from Finviz, refreshed every 5 min." />
          </div>

          {movers.loading && <LoadingSkeleton height="24px" count={5} />}

          {movers.data && (
            <>
              {/* Gainers */}
              <div style={{ marginBottom: SPACING.lg }}>
                <div style={{ color: theme.up, fontSize: FONT_SIZES.xs, fontWeight: 600, marginBottom: SPACING.sm }}>
                  GAINERS
                </div>
                {movers.data.gainers.map((m) => (
                  <button
                    key={m.ticker}
                    onClick={() => navigate(`/quick-look/${m.ticker}`)}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      width: '100%',
                      padding: `${SPACING.sm} 0`,
                      borderBottom: `1px solid ${theme.border}`,
                      color: theme.text_primary,
                      fontSize: FONT_SIZES.sm,
                    }}
                  >
                    <span style={{ fontWeight: 600 }}>{m.ticker}</span>
                    <span style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, flex: 1, marginLeft: SPACING.sm, textAlign: 'left' }}>
                      {m.name}
                    </span>
                    <span className="numeric" style={{ color: theme.up, fontWeight: 600 }}>
                      +{typeof m.change_pct === 'number' ? m.change_pct.toFixed(2) : m.change_pct}%
                    </span>
                    <span className="numeric" style={{ color: theme.text_secondary, marginLeft: SPACING.md, minWidth: 70, textAlign: 'right' }}>
                      ${m.price?.toFixed(2)}
                    </span>
                  </button>
                ))}
                {movers.data.gainers.length === 0 && (
                  <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs }}>No gainers data</div>
                )}
              </div>

              {/* Losers */}
              <div>
                <div style={{ color: theme.down, fontSize: FONT_SIZES.xs, fontWeight: 600, marginBottom: SPACING.sm }}>
                  LOSERS
                </div>
                {movers.data.losers.map((m) => (
                  <button
                    key={m.ticker}
                    onClick={() => navigate(`/quick-look/${m.ticker}`)}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      width: '100%',
                      padding: `${SPACING.sm} 0`,
                      borderBottom: `1px solid ${theme.border}`,
                      color: theme.text_primary,
                      fontSize: FONT_SIZES.sm,
                    }}
                  >
                    <span style={{ fontWeight: 600 }}>{m.ticker}</span>
                    <span style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, flex: 1, marginLeft: SPACING.sm, textAlign: 'left' }}>
                      {m.name}
                    </span>
                    <span className="numeric" style={{ color: theme.down, fontWeight: 600 }}>
                      {typeof m.change_pct === 'number' ? m.change_pct.toFixed(2) : m.change_pct}%
                    </span>
                    <span className="numeric" style={{ color: theme.text_secondary, marginLeft: SPACING.md, minWidth: 70, textAlign: 'right' }}>
                      ${m.price?.toFixed(2)}
                    </span>
                  </button>
                ))}
                {movers.data.losers.length === 0 && (
                  <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs }}>No losers data</div>
                )}
              </div>
            </>
          )}
        </div>

        {/* News */}
        <div style={cardStyle}>
          <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, fontWeight: 600, letterSpacing: '0.05em', marginBottom: SPACING.md }}>
            MARKET NEWS
          </div>

          {news.loading && <LoadingSkeleton height="60px" count={4} />}

          {news.data?.map((n, i) => (
            <a
              key={i}
              href={n.url}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'block',
                padding: `${SPACING.md} 0`,
                borderBottom: i < (news.data?.length ?? 0) - 1 ? `1px solid ${theme.border}` : 'none',
              }}
            >
              <div style={{ color: theme.text_primary, fontSize: FONT_SIZES.sm, fontWeight: 500, marginBottom: SPACING.xs, lineHeight: 1.4 }}>
                {n.headline}
              </div>
              <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs }}>
                {n.source}
                {n.datetime && ` · ${new Date(n.datetime * 1000).toLocaleDateString()}`}
              </div>
            </a>
          ))}

          {news.data?.length === 0 && (
            <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs }}>No news available</div>
          )}
        </div>
      </div>
    </div>
  );
}
