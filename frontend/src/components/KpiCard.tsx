import { useTheme } from '../theme/ThemeProvider';
import { FONTS, FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';

interface Props {
  label: string;
  value: string;
}

export default function KpiCard({ label, value }: Props) {
  const { theme } = useTheme();

  return (
    <div
      style={{
        background: theme.bg_card,
        border: `1px solid ${theme.border}`,
        borderRadius: RADIUS.card,
        padding: SPACING.md,
      }}
    >
      <div
        style={{
          color: theme.text_secondary,
          fontSize: FONT_SIZES.xs,
          fontWeight: 600,
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          marginBottom: SPACING.xs,
        }}
      >
        {label}
      </div>
      <div
        style={{
          color: theme.text_primary,
          fontSize: FONT_SIZES['2xl'],
          fontWeight: 700,
          fontFamily: FONTS.numeric,
        }}
      >
        {value}
      </div>
    </div>
  );
}
