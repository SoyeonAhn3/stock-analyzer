import { useTheme } from '../theme/ThemeProvider';
import { RADIUS, SPACING } from '../theme/tokens';

interface Props {
  width?: string;
  height?: string;
  count?: number;
}

const SHIMMER_CSS = `
  @keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }
`;

export default function LoadingSkeleton({ width = '100%', height = '20px', count = 1 }: Props) {
  const { theme } = useTheme();

  const shimmerBg = `linear-gradient(90deg, ${theme.bg_card} 25%, ${theme.bg_card_hover} 50%, ${theme.bg_card} 75%)`;

  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          style={{
            width,
            height,
            background: shimmerBg,
            backgroundSize: '200% 100%',
            borderRadius: RADIUS.card,
            marginBottom: i < count - 1 ? SPACING.sm : 0,
            animation: 'shimmer 1.5s infinite',
          }}
        />
      ))}
      <style>{SHIMMER_CSS}</style>
    </>
  );
}

export function SkeletonText({ lines = 3, widths }: { lines?: number; widths?: string[] }) {
  const { theme } = useTheme();
  const shimmerBg = `linear-gradient(90deg, ${theme.bg_card} 25%, ${theme.bg_card_hover} 50%, ${theme.bg_card} 75%)`;
  const defaultWidths = ['100%', '85%', '70%', '90%', '60%'];

  return (
    <>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          style={{
            width: widths?.[i] ?? defaultWidths[i % defaultWidths.length],
            height: 14,
            background: shimmerBg,
            backgroundSize: '200% 100%',
            borderRadius: RADIUS.badge,
            marginBottom: SPACING.sm,
            animation: 'shimmer 1.5s infinite',
          }}
        />
      ))}
      <style>{SHIMMER_CSS}</style>
    </>
  );
}

export function SkeletonCard({ count = 1 }: { count?: number }) {
  const { theme } = useTheme();
  const shimmerBg = `linear-gradient(90deg, ${theme.bg_card} 25%, ${theme.bg_card_hover} 50%, ${theme.bg_card} 75%)`;

  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          style={{
            background: theme.bg_card,
            border: `1px solid ${theme.border}`,
            borderRadius: RADIUS.card,
            padding: SPACING.md,
            marginBottom: SPACING.sm,
          }}
        >
          <div style={{ width: '40%', height: 12, background: shimmerBg, backgroundSize: '200% 100%', borderRadius: RADIUS.badge, marginBottom: SPACING.md, animation: 'shimmer 1.5s infinite' }} />
          <div style={{ width: '60%', height: 24, background: shimmerBg, backgroundSize: '200% 100%', borderRadius: RADIUS.badge, animation: 'shimmer 1.5s infinite' }} />
        </div>
      ))}
      <style>{SHIMMER_CSS}</style>
    </>
  );
}

export function SkeletonChart() {
  const { theme } = useTheme();
  const shimmerBg = `linear-gradient(90deg, ${theme.bg_card} 25%, ${theme.bg_card_hover} 50%, ${theme.bg_card} 75%)`;

  return (
    <>
      <div
        style={{
          width: '100%',
          height: 250,
          background: shimmerBg,
          backgroundSize: '200% 100%',
          borderRadius: RADIUS.card,
          animation: 'shimmer 1.5s infinite',
        }}
      />
      <style>{SHIMMER_CSS}</style>
    </>
  );
}

export function SkeletonTable({ rows = 5, cols = 3 }: { rows?: number; cols?: number }) {
  const { theme } = useTheme();
  const shimmerBg = `linear-gradient(90deg, ${theme.bg_card} 25%, ${theme.bg_card_hover} 50%, ${theme.bg_card} 75%)`;

  return (
    <>
      <div style={{ background: theme.bg_card, border: `1px solid ${theme.border}`, borderRadius: RADIUS.card, padding: SPACING.md }}>
        {/* Header */}
        <div style={{ display: 'flex', gap: SPACING.md, marginBottom: SPACING.md }}>
          {Array.from({ length: cols }).map((_, c) => (
            <div key={c} style={{ flex: 1, height: 14, background: shimmerBg, backgroundSize: '200% 100%', borderRadius: RADIUS.badge, animation: 'shimmer 1.5s infinite' }} />
          ))}
        </div>
        {/* Rows */}
        {Array.from({ length: rows }).map((_, r) => (
          <div key={r} style={{ display: 'flex', gap: SPACING.md, marginBottom: SPACING.sm }}>
            {Array.from({ length: cols }).map((_, c) => (
              <div key={c} style={{ flex: 1, height: 16, background: shimmerBg, backgroundSize: '200% 100%', borderRadius: RADIUS.badge, animation: 'shimmer 1.5s infinite', opacity: 0.7 }} />
            ))}
          </div>
        ))}
      </div>
      <style>{SHIMMER_CSS}</style>
    </>
  );
}
