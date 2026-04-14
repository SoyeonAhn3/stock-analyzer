import { useState } from 'react';
import { useTheme } from '../theme/ThemeProvider';
import { FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';

interface Props {
  text: string;
}

export default function Tooltip({ text }: Props) {
  const { theme } = useTheme();
  const [show, setShow] = useState(false);

  return (
    <span
      style={{ position: 'relative', display: 'inline-block', cursor: 'help' }}
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
    >
      <span style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs }}>(i)</span>
      {show && (
        <div
          style={{
            position: 'absolute',
            bottom: '120%',
            left: '50%',
            transform: 'translateX(-50%)',
            width: 250,
            padding: SPACING.sm,
            background: theme.bg_card_hover,
            border: `1px solid ${theme.border}`,
            borderRadius: RADIUS.card,
            color: theme.text_primary,
            fontSize: FONT_SIZES.xs,
            lineHeight: 1.5,
            zIndex: 200,
            whiteSpace: 'normal',
          }}
        >
          {text}
        </div>
      )}
    </span>
  );
}
