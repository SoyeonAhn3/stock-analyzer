import { useTheme } from '../theme/ThemeProvider';
import { FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';

interface Props {
  message: string;
  onRetry?: () => void;
}

export default function ErrorBanner({ message, onRetry }: Props) {
  const { theme } = useTheme();

  return (
    <div
      style={{
        background: `${theme.warning}15`,
        border: `1px solid ${theme.warning}`,
        borderRadius: RADIUS.card,
        padding: SPACING.md,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: SPACING.lg,
      }}
    >
      <span style={{ color: theme.warning, fontSize: FONT_SIZES.sm }}>
        {message}
      </span>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            color: theme.warning,
            fontSize: FONT_SIZES.xs,
            fontWeight: 600,
            padding: `${SPACING.xs} ${SPACING.sm}`,
            border: `1px solid ${theme.warning}`,
            borderRadius: RADIUS.button,
          }}
        >
          Retry
        </button>
      )}
    </div>
  );
}
