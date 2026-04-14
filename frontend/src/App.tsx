import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider, useTheme } from './theme/ThemeProvider';
import { SIDEBAR_WIDTH, TICKER_BAR_HEIGHT, SPACING } from './theme/tokens';
import Sidebar from './components/Sidebar';
import TickerBar from './components/TickerBar';
import AlertToast from './components/AlertToast';
import { useAlerts } from './hooks/useAlerts';
import { useBreakpoint } from './hooks/useBreakpoint';
import Settings from './pages/Settings';
import QuickLook from './pages/QuickLook';
import AIAnalysis from './pages/AIAnalysis';
import MarketOverview from './pages/MarketOverview';
import CompareMode from './pages/CompareMode';
import SectorScreening from './pages/SectorScreening';
import Guide from './pages/Guide';

function AppLayout() {
  const { theme } = useTheme();
  const { triggered, dismissTriggered } = useAlerts();
  const bp = useBreakpoint();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const isMobile = bp === 'mobile';
  const isTablet = bp === 'tablet';
  const showOverlay = (isMobile || isTablet) && sidebarOpen;

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: theme.bg_primary }}>
      {/* Mobile header */}
      {(isMobile || isTablet) && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            height: 48,
            background: theme.bg_card,
            borderBottom: `1px solid ${theme.border}`,
            display: 'flex',
            alignItems: 'center',
            padding: `0 ${SPACING.md}`,
            zIndex: 150,
          }}
        >
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            style={{ color: theme.text_primary, fontSize: '20px', padding: SPACING.xs, marginRight: SPACING.sm }}
          >
            ☰
          </button>
          <span style={{ color: theme.accent, fontSize: '16px', fontWeight: 700 }}>QuantAI</span>
        </div>
      )}

      {/* Overlay backdrop */}
      {showOverlay && (
        <div
          onClick={() => setSidebarOpen(false)}
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.5)',
            zIndex: 99,
          }}
        />
      )}

      {/* Sidebar - always visible on desktop, drawer on mobile/tablet */}
      <div
        style={{
          position: 'fixed',
          left: (isMobile || isTablet) && !sidebarOpen ? `-${SIDEBAR_WIDTH}` : '0',
          top: 0,
          zIndex: (isMobile || isTablet) ? 200 : 100,
          transition: 'left 0.25s ease',
        }}
      >
        <Sidebar />
      </div>

      <AlertToast alerts={triggered} onDismiss={dismissTriggered} />

      <main
        style={{
          marginLeft: (isMobile || isTablet) ? 0 : SIDEBAR_WIDTH,
          flex: 1,
          minHeight: '100vh',
          padding: (isMobile || isTablet)
            ? `calc(48px + ${SPACING.md}) ${SPACING.md} calc(${TICKER_BAR_HEIGHT} + ${SPACING.md})`
            : `${SPACING.lg} ${SPACING.lg} calc(${TICKER_BAR_HEIGHT} + ${SPACING.lg})`,
        }}
      >
        <Routes>
          <Route path="/" element={<MarketOverview />} />
          <Route path="/quick-look" element={<QuickLook />} />
          <Route path="/quick-look/:ticker" element={<QuickLook />} />
          <Route path="/analysis/:ticker" element={<AIAnalysis />} />
          <Route path="/compare" element={<CompareMode />} />
          <Route path="/sector" element={<SectorScreening />} />
          <Route path="/guide" element={<Guide />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>

      <TickerBar compact={isMobile} />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AppLayout />
      </ThemeProvider>
    </BrowserRouter>
  );
}
