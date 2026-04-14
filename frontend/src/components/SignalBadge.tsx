import { useTheme } from '../theme/ThemeProvider';
import { FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';

interface Props {
  signal: string; // "bullish" | "bearish" | "neutral"
  label?: string;
}

export default function SignalBadge({ signal, label }: Props) {
  const { theme } = useTheme();

  const colorMap: Record<string, string> = {
    bullish: theme.up,
    bearish: theme.down,
    neutral: theme.text_muted,
  };
  const color = colorMap[signal] ?? theme.text_muted;
  const text = label ?? signal.toUpperCase();

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: SPACING.xs,
        fontSize: FONT_SIZES.xs,
        fontWeight: 600,
        color,
      }}
    >
      <span style={{ width: 8, height: 8, borderRadius: RADIUS.pill, background: color }} />
      {text}
    </span>
  );
}
