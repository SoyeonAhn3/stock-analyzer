import { useNavigate, useLocation } from 'react-router-dom';
import { useTheme } from '../theme/ThemeProvider';
import { FONT_SIZES, SPACING } from '../theme/tokens';

const TABS = [
  { label: 'Home', icon: '🏠', path: '/' },
  { label: 'Analysis', icon: '📊', path: '/quick-look' },
  { label: 'Portfolio', icon: '💼', path: '/portfolio' },
  { label: 'Sector', icon: '🔍', path: '/sector' },
  { label: 'Settings', icon: '⚙', path: '/settings' },
] as const;

export default function BottomTabBar() {
  const { theme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <nav
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        height: 56,
        background: theme.bg_card,
        borderTop: `1px solid ${theme.border}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-around',
        zIndex: 200,
      }}
    >
      {TABS.map((tab) => {
        const active = isActive(tab.path);
        return (
          <button
            key={tab.path}
            onClick={() => navigate(tab.path)}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 2,
              padding: SPACING.xs,
              minWidth: 56,
              minHeight: 44,
              color: active ? theme.accent : theme.text_muted,
              transition: 'color 0.15s ease',
            }}
          >
            <span style={{ fontSize: '18px', lineHeight: 1 }}>{tab.icon}</span>
            <span style={{ fontSize: FONT_SIZES.xs, fontWeight: active ? 600 : 400 }}>
              {tab.label}
            </span>
          </button>
        );
      })}
    </nav>
  );
}
