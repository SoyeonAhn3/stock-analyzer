import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../theme/ThemeProvider';
import { FONTS, FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';
import { useApi } from '../hooks/useApi';
import LoadingSkeleton from '../components/LoadingSkeleton';
import ErrorBanner from '../components/ErrorBanner';

const GICS_SECTORS = [
  'Information Technology', 'Health Care', 'Financials', 'Energy',
  'Consumer Discretionary', 'Industrials', 'Materials', 'Utilities',
  'Real Estate', 'Communication Services', 'Consumer Staples',
];

interface ThemesResponse {
  themes: Record<string, { tickers: string[]; preset: string }>;
  names: string[];
}

interface ScreeningResult {
  sector: string;
  filter_applied: string;
  relaxed: boolean;
  relaxation_message: string | null;
  top5: Array<{ ticker: string; score: number; reason: string }>;
}

export default function SectorScreening() {
  const { theme } = useTheme();
  const navigate = useNavigate();
  const themes = useApi<ThemesResponse>('/themes');
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [result, setResult] = useState<ScreeningResult | null>(null);
  const [screenLoading, setScreenLoading] = useState(false);
  const [screenStage, setScreenStage] = useState(0);

  // Theme creation state
  const [showThemeForm, setShowThemeForm] = useState(false);
  const [newThemeName, setNewThemeName] = useState('');
  const [newThemeTickers, setNewThemeTickers] = useState('');
  const [themeCreating, setThemeCreating] = useState(false);

  const handleScreening = (name: string) => {
    setResult(null);
    setScreenLoading(true);
    setScreenStage(1);
    setSelected(new Set());

    // Simulate stage progression
    const stageTimer = setTimeout(() => setScreenStage(2), 8000);

    fetch(`/api/sector/${name}`, { method: 'POST' })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setResult)
      .catch(() => setResult(null))
      .finally(() => {
        clearTimeout(stageTimer);
        setScreenLoading(false);
        setScreenStage(0);
      });
  };

  const handleCreateTheme = () => {
    const name = newThemeName.trim();
    const tickers = newThemeTickers.split(',').map((t) => t.trim().toUpperCase()).filter(Boolean);
    if (!name || tickers.length === 0) return;

    setThemeCreating(true);
    fetch('/api/themes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, tickers, preset: name }),
    })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        setNewThemeName('');
        setNewThemeTickers('');
        setShowThemeForm(false);
        themes.refetch();
      })
      .finally(() => setThemeCreating(false));
  };

  const handleDeleteTheme = (name: string) => {
    fetch(`/api/themes/${name}`, { method: 'DELETE' })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        themes.refetch();
      });
  };

  const toggleSelect = (ticker: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(ticker)) next.delete(ticker);
      else next.add(ticker);
      return next;
    });
  };

  const btnStyle = (active?: boolean): React.CSSProperties => ({
    padding: `${SPACING.sm} ${SPACING.md}`,
    borderRadius: RADIUS.button,
    fontSize: FONT_SIZES.xs,
    fontWeight: 600,
    background: active ? theme.accent : 'transparent',
    color: active ? '#FFFFFF' : theme.text_secondary,
    border: `1px solid ${active ? theme.accent : theme.border}`,
    transition: 'all 0.15s ease',
  });

  return (
    <div>
      <h1 style={{ color: theme.text_primary, fontSize: FONT_SIZES['2xl'], fontWeight: 700, marginBottom: SPACING.xl }}>
        Sector Screening
      </h1>

      {/* GICS Sectors */}
      <div style={{ marginBottom: SPACING.lg }}>
        <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, fontWeight: 600, letterSpacing: '0.05em', marginBottom: SPACING.sm }}>
          GICS SECTORS
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: SPACING.sm }}>
          {GICS_SECTORS.map((s) => (
            <button key={s} onClick={() => handleScreening(s)} style={btnStyle()} disabled={screenLoading}>
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Custom Themes */}
      <div style={{ marginBottom: SPACING.xl }}>
        <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, fontWeight: 600, letterSpacing: '0.05em', marginBottom: SPACING.sm }}>
          CUSTOM THEMES
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: SPACING.sm, alignItems: 'center' }}>
          {themes.loading && <LoadingSkeleton width="100px" height="32px" count={3} />}
          {themes.data?.names.map((name) => (
            <span key={name} style={{ display: 'inline-flex', alignItems: 'center', gap: 2 }}>
              <button onClick={() => handleScreening(name)} style={btnStyle()} disabled={screenLoading}>
                {name}
              </button>
              <button
                onClick={() => handleDeleteTheme(name)}
                style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, padding: '2px 4px', opacity: 0.6 }}
                title={`Delete ${name}`}
              >
                x
              </button>
            </span>
          ))}
          <button
            onClick={() => setShowThemeForm(!showThemeForm)}
            style={{
              ...btnStyle(),
              borderStyle: 'dashed',
              color: theme.accent,
            }}
          >
            + New Theme
          </button>
        </div>

        {/* Theme creation form */}
        {showThemeForm && (
          <div
            style={{
              marginTop: SPACING.md,
              background: theme.bg_card,
              border: `1px solid ${theme.border}`,
              borderRadius: RADIUS.card,
              padding: SPACING.lg,
              display: 'flex',
              flexDirection: 'column',
              gap: SPACING.sm,
            }}
          >
            <input
              placeholder="Theme name (e.g. AI/반도체)"
              value={newThemeName}
              onChange={(e) => setNewThemeName(e.target.value)}
              style={{
                background: theme.bg_primary,
                color: theme.text_primary,
                border: `1px solid ${theme.border}`,
                borderRadius: RADIUS.button,
                padding: `${SPACING.sm} ${SPACING.md}`,
                fontSize: FONT_SIZES.sm,
              }}
            />
            <input
              placeholder="Tickers (comma separated, e.g. NVDA, AMD, AVGO)"
              value={newThemeTickers}
              onChange={(e) => setNewThemeTickers(e.target.value)}
              style={{
                background: theme.bg_primary,
                color: theme.text_primary,
                border: `1px solid ${theme.border}`,
                borderRadius: RADIUS.button,
                padding: `${SPACING.sm} ${SPACING.md}`,
                fontSize: FONT_SIZES.sm,
              }}
            />
            <div style={{ display: 'flex', gap: SPACING.sm }}>
              <button
                onClick={handleCreateTheme}
                disabled={themeCreating || !newThemeName.trim() || !newThemeTickers.trim()}
                style={{
                  padding: `${SPACING.sm} ${SPACING.lg}`,
                  background: theme.accent,
                  color: '#FFFFFF',
                  borderRadius: RADIUS.button,
                  fontSize: FONT_SIZES.sm,
                  fontWeight: 600,
                  opacity: themeCreating || !newThemeName.trim() || !newThemeTickers.trim() ? 0.5 : 1,
                }}
              >
                {themeCreating ? 'Creating...' : 'Create'}
              </button>
              <button
                onClick={() => { setShowThemeForm(false); setNewThemeName(''); setNewThemeTickers(''); }}
                style={{
                  padding: `${SPACING.sm} ${SPACING.lg}`,
                  color: theme.text_secondary,
                  borderRadius: RADIUS.button,
                  fontSize: FONT_SIZES.sm,
                  border: `1px solid ${theme.border}`,
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Loading with stages */}
      {screenLoading && (
        <div
          style={{
            background: theme.bg_card,
            border: `1px solid ${theme.border}`,
            borderRadius: RADIUS.card,
            padding: SPACING.xl,
            marginBottom: SPACING.lg,
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: SPACING.sm }}>
            {[
              { stage: 1, label: 'Data Collection & Filtering' },
              { stage: 2, label: 'AI Analysis & Scoring' },
            ].map(({ stage, label }) => (
              <div
                key={stage}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: SPACING.sm,
                  color: screenStage >= stage ? theme.accent : theme.text_muted,
                  fontSize: FONT_SIZES.sm,
                }}
              >
                <span>{screenStage > stage ? '✓' : screenStage === stage ? '⟳' : '○'}</span>
                <span>Stage {stage}/2: {label}</span>
                {screenStage === stage && (
                  <span style={{ marginLeft: 'auto', fontSize: FONT_SIZES.xs, color: theme.text_muted }}>
                    Running...
                  </span>
                )}
              </div>
            ))}
          </div>
          <p style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginTop: SPACING.md, textAlign: 'center' }}>
            This may take 2~3 minutes
          </p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div
          style={{
            background: theme.bg_card,
            border: `1px solid ${theme.border}`,
            borderRadius: RADIUS.card,
            padding: SPACING.lg,
          }}
        >
          {/* Relaxation warning */}
          {result.relaxed && result.relaxation_message && (
            <ErrorBanner message={result.relaxation_message} />
          )}

          <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, fontWeight: 600, letterSpacing: '0.05em', marginBottom: SPACING.md }}>
            TOP 5 RESULTS — {result.sector} ({result.filter_applied})
          </div>

          {result.top5.map((stock, i) => (
            <div
              key={stock.ticker}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: SPACING.md,
                padding: `${SPACING.md} 0`,
                borderBottom: i < result.top5.length - 1 ? `1px solid ${theme.border}` : 'none',
              }}
            >
              {/* Rank */}
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: RADIUS.pill,
                  background: `${theme.accent}20`,
                  color: theme.accent,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: FONT_SIZES.sm,
                  fontWeight: 700,
                  fontFamily: FONTS.numeric,
                  flexShrink: 0,
                }}
              >
                {i + 1}
              </div>

              {/* Checkbox */}
              <input
                type="checkbox"
                checked={selected.has(stock.ticker)}
                onChange={() => toggleSelect(stock.ticker)}
                style={{ accentColor: theme.accent }}
              />

              {/* Ticker */}
              <button
                onClick={() => navigate(`/quick-look/${stock.ticker}`)}
                style={{ color: theme.text_primary, fontSize: FONT_SIZES.md, fontWeight: 700, minWidth: 60 }}
              >
                {stock.ticker}
              </button>

              {/* Score */}
              <span className="numeric" style={{ color: theme.accent, fontSize: FONT_SIZES.sm, fontWeight: 600 }}>
                Score: {stock.score}
              </span>

              {/* Reason */}
              <span style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm, flex: 1 }}>
                "{stock.reason}"
              </span>
            </div>
          ))}

          {/* Compare Selected */}
          {selected.size >= 2 && (
            <button
              onClick={() => navigate(`/compare?tickers=${Array.from(selected).join(',')}`)}
              style={{
                width: '100%',
                marginTop: SPACING.lg,
                padding: SPACING.md,
                background: theme.accent,
                color: '#FFFFFF',
                borderRadius: RADIUS.button,
                fontSize: FONT_SIZES.sm,
                fontWeight: 700,
              }}
            >
              Compare Selected ({selected.size})
            </button>
          )}

          {/* Disclaimer */}
          <p style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginTop: SPACING.lg, textAlign: 'center' }}>
            AI-generated reference. Not financial advice.
          </p>
        </div>
      )}
    </div>
  );
}
