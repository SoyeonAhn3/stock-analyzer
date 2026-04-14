import { useTheme } from '../theme/ThemeProvider';
import { RADIUS, SPACING } from '../theme/tokens';

interface Props {
  width?: string;
  height?: string;
  count?: number;
}

export default function LoadingSkeleton({ width = '100%', height = '20px', count = 1 }: Props) {
  const { theme } = useTheme();

  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          style={{
            width,
            height,
            background: `linear-gradient(90deg, ${theme.bg_card} 25%, ${theme.bg_card_hover} 50%, ${theme.bg_card} 75%)`,
            backgroundSize: '200% 100%',
            borderRadius: RADIUS.card,
            marginBottom: i < count - 1 ? SPACING.sm : 0,
            animation: 'shimmer 1.5s infinite',
          }}
        />
      ))}
      <style>{`
        @keyframes shimmer {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
      `}</style>
    </>
  );
}
