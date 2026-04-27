/** design-spec.md 4~5장 — 폰트, 크기, 간격, 보더 라디우스 */

export const FONTS = {
  body: "'Inter', 'Pretendard', sans-serif",
  numeric: "'JetBrains Mono', 'IBM Plex Mono', monospace",
} as const;

export const FONT_SIZES = {
  xs: '11px',
  sm: '13px',
  md: '14px',
  lg: '16px',
  xl: '20px',
  '2xl': '24px',
  '3xl': '32px',
  '4xl': '40px',
} as const;

export const SPACING = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  '2xl': '48px',
} as const;

export const RADIUS = {
  card: '8px',
  button: '6px',
  badge: '4px',
  pill: '9999px',
} as const;

export const SIDEBAR_WIDTH = '240px';
export const TICKER_BAR_HEIGHT = '36px';
export const BOTTOM_TAB_HEIGHT = '56px';
