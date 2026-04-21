import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useTheme } from '../theme/ThemeProvider';
import { FONTS, FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';
import { API_BASE } from '../config';
import ErrorBanner from '../components/ErrorBanner';
import CompareChart from '../components/CompareChart';

interface CompareData {
  comparison_type: string;
  data: Record<string, any>;
}

function safeRender(val: any): string {
  if (val == null) return '--';
  if (typeof val === 'string') return val;
  if (typeof val === 'number') return String(val);
  if (typeof val === 'object' && !Array.isArray(val)) {
    return Object.entries(val).map(([k, v]) => `${k}: ${v}`).join('. ');
  }
  return JSON.stringify(val);
}

export default function CompareMode() {
  const { theme } = useTheme();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialTickers = searchParams.get('tickers')?.split(',').filter(Boolean) ?? [];

  const [tickers, setTickers] = useState<string[]>(initialTickers);
  const [input, setInput] = useState('');
  const [compareData, setCompareData] = useState<CompareData | null>(null);
  const [aiResult, setAiResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addTicker = () => {
    const t = input.trim().toUpperCase();
    if (t && !tickers.includes(t) && tickers.length < 3) {
      const next = [...tickers, t];
      setTickers(next);
      setInput('');
      fetchCompare(next);
    }
  };

  const removeTicker = (t: string) => {
    const next = tickers.filter((x) => x !== t);
    setTickers(next);
    setCompareData(null);
    setAiResult(null);
    if (next.length >= 2) fetchCompare(next);
  };

  const fetchCompare = (list: string[]) => {
    if (list.length < 2) return;
    setLoading(true);
    setError(null);
    fetch(`${API_BASE}/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tickers: list }),
    })
      .then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(setCompareData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  const runAiCompare = () => {
    setAiLoading(true);
    fetch(`${API_BASE}/compare/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tickers }),
    })
      .then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(setAiResult)
      .catch((e) => setError(e.message))
      .finally(() => setAiLoading(false));
  };

  // Fetch on mount if initial tickers
  useEffect(() => {
    if (initialTickers.length >= 2) fetchCompare(initialTickers);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const typeColor: Record<string, string> = {
    same_sector: theme.accent,
    cross_sector: theme.warning,
  };

  const cardStyle: React.CSSProperties = {
    background: theme.bg_card,
    border: `1px solid ${theme.border}`,
    borderRadius: RADIUS.card,
    padding: SPACING.lg,
    marginBottom: SPACING.lg,
  };

  return (
    <div>
      <h1 style={{ color: theme.text_primary, fontSize: FONT_SIZES['2xl'], fontWeight: 700, marginBottom: SPACING.lg }}>
        Compare Mode
      </h1>

      {/* Ticker Bar */}
      <div style={{ ...cardStyle, display: 'flex', alignItems: 'center', gap: SPACING.sm, flexWrap: 'wrap' }}>
        {tickers.map((t) => (
          <span
            key={t}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: SPACING.xs,
              background: `${theme.accent}20`,
              color: theme.accent,
              padding: `${SPACING.xs} ${SPACING.sm}`,
              borderRadius: RADIUS.badge,
              fontSize: FONT_SIZES.sm,
              fontWeight: 600,
              fontFamily: FONTS.numeric,
            }}
          >
            {t}
            <button onClick={() => removeTicker(t)} style={{ color: theme.accent, fontSize: FONT_SIZES.xs }}>x</button>
          </span>
        ))}
        {tickers.length < 3 && (
          <input
            placeholder="+ Add ticker"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && addTicker()}
            style={{
              background: 'transparent',
              color: theme.text_primary,
              fontSize: FONT_SIZES.sm,
              padding: `${SPACING.xs} ${SPACING.sm}`,
              border: `1px solid ${theme.border}`,
              borderRadius: RADIUS.button,
              width: 140,
            }}
          />
        )}

        {/* Comparison type badge */}
        {compareData?.comparison_type && (
          <span
            style={{
              marginLeft: 'auto',
              background: `${typeColor[compareData.comparison_type] ?? theme.text_muted}20`,
              color: typeColor[compareData.comparison_type] ?? theme.text_muted,
              padding: `${SPACING.xs} ${SPACING.sm}`,
              borderRadius: RADIUS.badge,
              fontSize: FONT_SIZES.xs,
              fontWeight: 600,
            }}
          >
            {compareData.comparison_type === 'same_sector' ? 'Same Sector' : 'Cross Sector'}
          </span>
        )}
      </div>

      {error && <ErrorBanner message={error} />}

      {loading && <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.sm, marginBottom: SPACING.lg }}>Loading comparison data...</div>}

      {/* Compare Table */}
      {compareData && tickers.length >= 2 && (
        <div style={cardStyle}>
          <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, fontWeight: 600, letterSpacing: '0.05em', marginBottom: SPACING.md }}>
            COMPARISON TABLE
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ textAlign: 'left', padding: SPACING.sm, color: theme.text_muted, fontSize: FONT_SIZES.xs, borderBottom: `1px solid ${theme.border}` }} />
                {tickers.map((t) => (
                  <th
                    key={t}
                    style={{
                      textAlign: 'right',
                      padding: SPACING.sm,
                      color: theme.accent,
                      fontSize: FONT_SIZES.sm,
                      fontWeight: 700,
                      fontFamily: FONTS.numeric,
                      borderBottom: `1px solid ${theme.border}`,
                      cursor: 'pointer',
                    }}
                    onClick={() => navigate(`/quick-look/${t}`)}
                  >
                    {t}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {['price', 'change_percent', 'pe', 'forward_pe', 'eps', 'peg', 'market_cap', 'dividend_yield', 'de_ratio', 'roe', 'profit_margin', 'beta'].map((field) => (
                <tr key={field}>
                  <td style={{ padding: SPACING.sm, color: theme.text_secondary, fontSize: FONT_SIZES.xs, textTransform: 'uppercase', borderBottom: `1px solid ${theme.border}` }}>
                    {field.replace(/_/g, ' ')}
                  </td>
                  {tickers.map((t) => {
                    const d = compareData.data?.data?.[t] ?? compareData.data?.[t];
                    const q = d?.quote ?? d;
                    const f = d?.fundamentals ?? d;
                    let val: any = q?.[field] ?? f?.[field] ?? '--';
                    if (typeof val === 'number') val = val.toLocaleString(undefined, { maximumFractionDigits: 2 });
                    return (
                      <td
                        key={t}
                        className="numeric"
                        style={{
                          textAlign: 'right',
                          padding: SPACING.sm,
                          color: theme.text_primary,
                          fontSize: FONT_SIZES.sm,
                          borderBottom: `1px solid ${theme.border}`,
                        }}
                      >
                        {val}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Normalized Returns Chart */}
      {compareData && tickers.length >= 2 && <CompareChart tickers={tickers} />}

      {/* AI Compare button */}
      {tickers.length >= 2 && !aiResult && (
        <button
          onClick={runAiCompare}
          disabled={aiLoading}
          style={{
            width: '100%',
            padding: SPACING.md,
            background: aiLoading ? theme.text_muted : theme.accent,
            color: '#FFFFFF',
            borderRadius: RADIUS.button,
            fontSize: FONT_SIZES.md,
            fontWeight: 700,
            marginBottom: SPACING.lg,
            cursor: aiLoading ? 'not-allowed' : 'pointer',
          }}
        >
          {aiLoading ? 'AI Analyzing... (1~2 min)' : 'AI Compare Analysis'}
        </button>
      )}

      {/* AI Result */}
      {aiResult && (
        <div style={cardStyle}>
          <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, fontWeight: 600, letterSpacing: '0.05em', marginBottom: SPACING.md }}>
            AI COMPARE ANALYSIS
            {compareData?.comparison_type && (
              <span style={{ marginLeft: SPACING.sm, color: typeColor[compareData.comparison_type] ?? theme.text_muted }}>
                ({compareData.comparison_type === 'same_sector' ? 'Same Sector' : 'Cross Sector'})
              </span>
            )}
          </div>

          {/* Summary */}
          {aiResult.summary && (
            <p style={{ color: theme.text_primary, fontSize: FONT_SIZES.md, lineHeight: 1.6, marginBottom: SPACING.lg }}>
              {aiResult.summary}
            </p>
          )}

          {/* Rankings (same_sector) */}
          {aiResult.analysis?.rankings && (
            <div style={{ marginBottom: SPACING.lg }}>
              <div style={{ color: theme.accent, fontSize: FONT_SIZES.xs, fontWeight: 600, letterSpacing: '0.05em', marginBottom: SPACING.sm }}>
                CATEGORY RANKINGS
              </div>
              {Object.entries(aiResult.analysis.rankings as Record<string, any>).map(([category, ranking]) => (
                <div key={category} style={{ padding: `${SPACING.sm} 0`, borderBottom: `1px solid ${theme.border}` }}>
                  <span style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm, fontWeight: 600 }}>
                    {category}:
                  </span>{' '}
                  <span style={{ color: theme.text_primary, fontSize: FONT_SIZES.sm }}>
                    {safeRender(ranking)}
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* Sector Context (cross_sector) */}
          {aiResult.analysis?.sector_context && (
            <div style={{ marginBottom: SPACING.lg }}>
              <div style={{ color: theme.accent, fontSize: FONT_SIZES.xs, fontWeight: 600, letterSpacing: '0.05em', marginBottom: SPACING.sm }}>
                SECTOR CONTEXT
              </div>
              {Object.entries(aiResult.analysis.sector_context as Record<string, any>).map(([ticker, context]) => (
                <div key={ticker} style={{ padding: `${SPACING.sm} 0`, borderBottom: `1px solid ${theme.border}` }}>
                  <span style={{ color: theme.accent, fontSize: FONT_SIZES.sm, fontWeight: 700, fontFamily: FONTS.numeric }}>{ticker}</span>
                  <p style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm, marginTop: SPACING.xs, lineHeight: 1.5 }}>
                    {safeRender(context)}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Technical Comparison (cross_sector) */}
          {aiResult.analysis?.technical_comparison && (
            <div style={{ marginBottom: SPACING.lg }}>
              <div style={{ color: theme.accent, fontSize: FONT_SIZES.xs, fontWeight: 600, letterSpacing: '0.05em', marginBottom: SPACING.sm }}>
                TECHNICAL COMPARISON
              </div>
              {Object.entries(aiResult.analysis.technical_comparison as Record<string, any>).map(([ticker, analysis]) => (
                <div key={ticker} style={{ padding: `${SPACING.sm} 0`, borderBottom: `1px solid ${theme.border}` }}>
                  <span style={{ color: theme.accent, fontSize: FONT_SIZES.sm, fontWeight: 700, fontFamily: FONTS.numeric }}>{ticker}</span>
                  <p style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm, marginTop: SPACING.xs, lineHeight: 1.5 }}>
                    {safeRender(analysis)}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Key Risks */}
          {aiResult.analysis?.key_risks && (
            <div style={{ marginBottom: SPACING.lg }}>
              <div style={{ color: theme.down, fontSize: FONT_SIZES.xs, fontWeight: 600, letterSpacing: '0.05em', marginBottom: SPACING.sm }}>
                KEY RISKS
              </div>
              <ul style={{ paddingLeft: SPACING.lg }}>
                {(Array.isArray(aiResult.analysis.key_risks)
                  ? aiResult.analysis.key_risks
                  : Object.entries(aiResult.analysis.key_risks).map(([k, v]) => `${k}: ${v}`)
                ).map((risk: string, i: number) => (
                  <li key={i} style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm, marginBottom: SPACING.xs, listStyle: 'disc' }}>
                    {risk}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Macro Scenarios (cross_sector) */}
          {aiResult.analysis?.macro_scenarios && (
            <div style={{ marginBottom: SPACING.lg }}>
              <div style={{ color: theme.warning, fontSize: FONT_SIZES.xs, fontWeight: 600, letterSpacing: '0.05em', marginBottom: SPACING.sm }}>
                MACRO SCENARIOS
              </div>
              {Object.entries(aiResult.analysis.macro_scenarios as Record<string, any>).map(([scenario, impact]) => (
                <div key={scenario} style={{ padding: `${SPACING.sm} 0`, borderBottom: `1px solid ${theme.border}` }}>
                  <span style={{ color: theme.text_primary, fontSize: FONT_SIZES.sm, fontWeight: 600 }}>{scenario}:</span>{' '}
                  <span style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm }}>{safeRender(impact)}</span>
                </div>
              ))}
            </div>
          )}

          {/* Fallback for unknown structures */}
          {aiResult.analysis && !aiResult.analysis.rankings && !aiResult.analysis.sector_context && !aiResult.summary && (
            <pre style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm, lineHeight: 1.6, whiteSpace: 'pre-wrap', fontFamily: FONTS.body }}>
              {typeof aiResult.analysis === 'string' ? aiResult.analysis : JSON.stringify(aiResult.analysis, null, 2)}
            </pre>
          )}

          {/* Fallback for no analysis object */}
          {!aiResult.analysis && !aiResult.summary && (
            <pre style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm, lineHeight: 1.6, whiteSpace: 'pre-wrap', fontFamily: FONTS.body }}>
              {JSON.stringify(aiResult, null, 2)}
            </pre>
          )}

          {/* Analysis Basis */}
          <div style={{
            marginTop: SPACING.lg,
            padding: SPACING.md,
            background: `${theme.text_muted}08`,
            borderRadius: RADIUS.card,
            border: `1px solid ${theme.border}`,
          }}>
            <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, fontWeight: 600, letterSpacing: '0.05em', marginBottom: SPACING.sm }}>
              ANALYSIS BASIS
            </div>
            {[
              { label: 'Quote Data', value: 'Finnhub (real-time quotes)' },
              { label: 'Fundamentals', value: 'Finnhub · yFinance · FMP (PER, EPS, PEG, D/E Ratio)' },
              { label: 'Technicals', value: 'Twelve Data · yFinance (RSI, MACD, Bollinger, MA50/200)' },
              { label: 'AI Engine', value: 'Claude (Anthropic) — cross-validated comparison analysis' },
            ].map(({ label, value }) => (
              <div key={label} style={{ display: 'flex', gap: SPACING.sm, padding: `3px 0`, fontSize: FONT_SIZES.xs }}>
                <span style={{ color: theme.text_muted, minWidth: 90 }}>{label}</span>
                <span style={{ color: theme.text_secondary }}>{value}</span>
              </div>
            ))}
          </div>

          <p style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginTop: SPACING.md, textAlign: 'center' }}>
            AI-generated reference only. Not financial advice. Do your own research before making investment decisions.
          </p>
        </div>
      )}
    </div>
  );
}
