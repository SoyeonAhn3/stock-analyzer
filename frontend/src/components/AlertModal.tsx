import { useState } from 'react';
import { useTheme } from '../theme/ThemeProvider';
import { FONTS, FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';

interface Props {
  ticker: string;
  onClose: () => void;
  onCreate: (ticker: string, targetPrice: number, direction: string) => Promise<void>;
}

export default function AlertModal({ ticker, onClose, onCreate }: Props) {
  const { theme } = useTheme();
  const [price, setPrice] = useState('');
  const [direction, setDirection] = useState<'above' | 'below'>('above');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = () => {
    const target = parseFloat(price);
    if (isNaN(target) || target <= 0) return;

    setSubmitting(true);
    onCreate(ticker, target, direction)
      .then(onClose)
      .finally(() => setSubmitting(false));
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 300,
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: theme.bg_card,
          border: `1px solid ${theme.border}`,
          borderRadius: RADIUS.card,
          padding: SPACING.xl,
          width: 340,
        }}
      >
        <div style={{ color: theme.text_primary, fontSize: FONT_SIZES.lg, fontWeight: 700, marginBottom: SPACING.lg }}>
          Price Alert — {ticker}
        </div>

        {/* Target Price */}
        <div style={{ marginBottom: SPACING.md }}>
          <label style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, fontWeight: 600, display: 'block', marginBottom: SPACING.xs }}>
            TARGET PRICE
          </label>
          <input
            type="number"
            step="0.01"
            placeholder="e.g. 150.00"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            style={{
              width: '100%',
              padding: `${SPACING.sm} ${SPACING.md}`,
              background: theme.bg_primary,
              color: theme.text_primary,
              border: `1px solid ${theme.border}`,
              borderRadius: RADIUS.button,
              fontSize: FONT_SIZES.md,
              fontFamily: FONTS.numeric,
            }}
          />
        </div>

        {/* Direction */}
        <div style={{ marginBottom: SPACING.lg }}>
          <label style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, fontWeight: 600, display: 'block', marginBottom: SPACING.xs }}>
            DIRECTION
          </label>
          <div style={{ display: 'flex', gap: SPACING.sm }}>
            {(['above', 'below'] as const).map((d) => (
              <button
                key={d}
                onClick={() => setDirection(d)}
                style={{
                  flex: 1,
                  padding: SPACING.sm,
                  borderRadius: RADIUS.button,
                  fontSize: FONT_SIZES.sm,
                  fontWeight: 600,
                  background: direction === d ? (d === 'above' ? theme.up : theme.down) : 'transparent',
                  color: direction === d ? '#FFFFFF' : theme.text_secondary,
                  border: `1px solid ${direction === d ? (d === 'above' ? theme.up : theme.down) : theme.border}`,
                }}
              >
                {d === 'above' ? 'Above (rises to)' : 'Below (drops to)'}
              </button>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', gap: SPACING.sm }}>
          <button
            onClick={handleSubmit}
            disabled={submitting || !price || parseFloat(price) <= 0}
            style={{
              flex: 1,
              padding: SPACING.md,
              background: theme.accent,
              color: '#FFFFFF',
              borderRadius: RADIUS.button,
              fontSize: FONT_SIZES.sm,
              fontWeight: 700,
              opacity: submitting || !price ? 0.5 : 1,
            }}
          >
            {submitting ? 'Setting...' : 'Set Alert'}
          </button>
          <button
            onClick={onClose}
            style={{
              padding: `${SPACING.md} ${SPACING.lg}`,
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
    </div>
  );
}
