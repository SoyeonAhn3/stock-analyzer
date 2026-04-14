import { useTheme } from '../theme/ThemeProvider';
import { FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';

export default function Settings() {
  const { theme, mode, toggleTheme } = useTheme();

  return (
    <div style={{ padding: SPACING.lg }}>
      <h1 style={{ color: theme.text_primary, fontSize: FONT_SIZES['2xl'], marginBottom: SPACING.xl }}>
        Settings
      </h1>

      {/* Theme Toggle */}
      <div
        style={{
          background: theme.bg_card,
          border: `1px solid ${theme.border}`,
          borderRadius: RADIUS.card,
          padding: SPACING.lg,
          marginBottom: SPACING.lg,
        }}
      >
        <div
          style={{
            color: theme.text_muted,
            fontSize: FONT_SIZES.xs,
            fontWeight: 600,
            letterSpacing: '0.05em',
            marginBottom: SPACING.md,
          }}
        >
          THEME
        </div>
        <div style={{ display: 'flex', gap: SPACING.sm }}>
          {(['dark', 'light'] as const).map((m) => (
            <button
              key={m}
              onClick={mode !== m ? toggleTheme : undefined}
              style={{
                padding: `${SPACING.sm} ${SPACING.lg}`,
                borderRadius: RADIUS.button,
                fontSize: FONT_SIZES.sm,
                fontWeight: 600,
                background: mode === m ? theme.accent : 'transparent',
                color: mode === m ? '#FFFFFF' : theme.text_secondary,
                border: `1px solid ${mode === m ? theme.accent : theme.border}`,
                transition: 'all 0.15s ease',
              }}
            >
              {m === 'dark' ? 'Dark' : 'Light'}
            </button>
          ))}
        </div>
      </div>

      {/* AI Usage */}
      <div
        style={{
          background: theme.bg_card,
          border: `1px solid ${theme.border}`,
          borderRadius: RADIUS.card,
          padding: SPACING.lg,
          marginBottom: SPACING.lg,
        }}
      >
        <div
          style={{
            color: theme.text_muted,
            fontSize: FONT_SIZES.xs,
            fontWeight: 600,
            letterSpacing: '0.05em',
            marginBottom: SPACING.md,
          }}
        >
          AI USAGE
        </div>
        <div style={{ color: theme.text_primary, fontSize: FONT_SIZES.lg }}>
          <span className="numeric">0</span> / <span className="numeric">100</span> today
        </div>
        <div
          style={{
            height: '6px',
            background: theme.border,
            borderRadius: RADIUS.pill,
            marginTop: SPACING.sm,
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: '0%',
              height: '100%',
              background: theme.accent,
              borderRadius: RADIUS.pill,
            }}
          />
        </div>
      </div>

      {/* Disclaimer */}
      <div
        style={{
          background: theme.bg_card,
          border: `1px solid ${theme.border}`,
          borderRadius: RADIUS.card,
          padding: SPACING.lg,
        }}
      >
        <div
          style={{
            color: theme.text_muted,
            fontSize: FONT_SIZES.xs,
            fontWeight: 600,
            letterSpacing: '0.05em',
            marginBottom: SPACING.md,
          }}
        >
          DISCLAIMER
        </div>
        <p style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm, lineHeight: 1.6 }}>
          AI-generated reference only. Not financial advice. All data is provided
          for informational purposes. Do your own research before making any
          investment decisions. Past performance does not guarantee future results.
        </p>
      </div>
    </div>
  );
}
