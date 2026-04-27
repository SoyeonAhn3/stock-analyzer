import { useState, useEffect, useCallback } from 'react';
import { useTheme } from '../theme/ThemeProvider';
import { FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';
import { useBreakpoint } from '../hooks/useBreakpoint';
import { usePortfolio } from '../hooks/usePortfolio';
import PortfolioSummary from '../components/portfolio/PortfolioSummary';
import PortfolioCharts from '../components/portfolio/PortfolioCharts';
import HoldingCard from '../components/portfolio/HoldingCard';
import AddStockModal from '../components/portfolio/AddStockModal';
import PortfolioAnalysis from '../components/portfolio/PortfolioAnalysis';
import LoadingSkeleton, { SkeletonCard } from '../components/LoadingSkeleton';
import ErrorBanner from '../components/ErrorBanner';
import type { AnalysisResult, Holding } from '../services/portfolioApi';
import { fetchAnalysis } from '../services/portfolioApi';

export default function Portfolio() {
  const { theme } = useTheme();
  const bp = useBreakpoint();
  const isMobile = bp === 'mobile';

  const {
    holdings,
    holdingSummaries,
    summary,
    loading,
    error,
    addHolding,
    updateHolding,
    removeHolding,
    refreshQuotes,
  } = usePortfolio();

  const [modalOpen, setModalOpen] = useState(false);
  const [editingHolding, setEditingHolding] = useState<Holding | null>(null);

  const openAdd = useCallback(() => {
    setEditingHolding(null);
    setModalOpen(true);
  }, []);

  const openEdit = useCallback((e: Event) => {
    const detail = (e as CustomEvent).detail as Holding;
    setEditingHolding(detail);
    setModalOpen(true);
  }, []);

  useEffect(() => {
    window.addEventListener('portfolio-add-stock', openAdd);
    window.addEventListener('portfolio-edit-stock', openEdit);
    return () => {
      window.removeEventListener('portfolio-add-stock', openAdd);
      window.removeEventListener('portfolio-edit-stock', openEdit);
    };
  }, [openAdd, openEdit]);

  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    setAnalysisLoading(true);
    setAnalysisError(null);
    try {
      const result = await fetchAnalysis(holdings);
      setAnalysisResult(result);
    } catch (e) {
      setAnalysisError(e instanceof Error ? e.message : 'Analysis failed');
    } finally {
      setAnalysisLoading(false);
    }
  };

  const modal = modalOpen && (
    <AddStockModal
      editing={editingHolding}
      onSave={addHolding}
      onUpdate={updateHolding}
      onClose={() => setModalOpen(false)}
    />
  );

  // ── 빈 상태 ──
  if (holdings.length === 0) {
    return (
      <div style={{ maxWidth: 800, margin: '0 auto' }}>
        <h1 style={{ color: theme.text_primary, fontSize: FONT_SIZES['2xl'], fontWeight: 700, marginBottom: SPACING.lg }}>
          Portfolio
        </h1>
        <div
          style={{
            background: theme.bg_card,
            border: `1px solid ${theme.border}`,
            borderRadius: RADIUS.card,
            padding: SPACING['2xl'],
            textAlign: 'center',
          }}
        >
          <div style={{ color: theme.text_primary, fontSize: FONT_SIZES.lg, fontWeight: 600, marginBottom: SPACING.sm }}>
            아직 추가된 종목이 없습니다.
          </div>
          <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.sm, marginBottom: SPACING.lg }}>
            첫 종목을 추가해서 포트폴리오 분석을 시작하세요.
          </div>
          <button
            onClick={() => window.dispatchEvent(new CustomEvent('portfolio-add-stock'))}
            style={{
              padding: `${SPACING.sm} ${SPACING.lg}`,
              fontSize: FONT_SIZES.md,
              fontWeight: 600,
              color: theme.bg_primary,
              background: theme.accent,
              border: 'none',
              borderRadius: RADIUS.button,
              cursor: 'pointer',
            }}
          >
            + Add Your First Stock
          </button>
        </div>
        {modal}
      </div>
    );
  }

  // ── 메인 화면 ──
  return (
    <div style={{ maxWidth: 1000, margin: '0 auto' }}>
      {/* 헤더 */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: SPACING.lg,
          flexWrap: 'wrap',
          gap: SPACING.sm,
        }}
      >
        <h1 style={{ color: theme.text_primary, fontSize: FONT_SIZES['2xl'], fontWeight: 700, margin: 0 }}>
          Portfolio
        </h1>
        <div style={{ display: 'flex', gap: SPACING.sm }}>
          <button
            onClick={refreshQuotes}
            style={{
              padding: `${SPACING.xs} ${SPACING.sm}`,
              fontSize: FONT_SIZES.sm,
              color: theme.text_secondary,
              border: `1px solid ${theme.border}`,
              borderRadius: RADIUS.button,
              background: 'transparent',
              cursor: 'pointer',
            }}
          >
            ⟳ Refresh
          </button>
          <button
            onClick={() => window.dispatchEvent(new CustomEvent('portfolio-add-stock'))}
            style={{
              padding: `${SPACING.xs} ${SPACING.md}`,
              fontSize: FONT_SIZES.sm,
              fontWeight: 600,
              color: theme.bg_primary,
              background: theme.accent,
              border: 'none',
              borderRadius: RADIUS.button,
              cursor: 'pointer',
            }}
          >
            + Add Stock
          </button>
        </div>
      </div>

      {error && <ErrorBanner message={error} onRetry={refreshQuotes} />}

      {/* 로딩 */}
      {loading && holdingSummaries.every((h) => h.current_price === null) ? (
        <>
          <div style={{ display: 'flex', gap: SPACING.md, marginBottom: SPACING.lg, flexDirection: isMobile ? 'column' : 'row' }}>
            <LoadingSkeleton height="140px" />
            <LoadingSkeleton height="140px" />
          </div>
          <SkeletonCard count={holdings.length} />
        </>
      ) : (
        <>
          {/* 요약 카드 */}
          <PortfolioSummary
            totalMarketValue={summary.total_market_value}
            totalCostBasis={summary.total_cost_basis}
            totalPnl={summary.total_pnl}
            totalPnlPct={summary.total_pnl_pct}
            best={summary.best}
            worst={summary.worst}
            holdingsCount={holdings.length}
          />

          {/* 차트 */}
          <PortfolioCharts holdings={holdingSummaries} />

          {/* 보유 종목 리스트 */}
          <div style={{ marginBottom: SPACING.lg }}>
            <div
              style={{
                color: theme.text_muted,
                fontSize: FONT_SIZES.xs,
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: SPACING.md,
              }}
            >
              Holdings ({holdings.length})
            </div>
            {holdingSummaries.map((h, i) => (
              <HoldingCard
                key={holdings[i].id}
                ticker={h.ticker}
                shares={h.shares}
                avgCost={h.avg_cost}
                currentPrice={h.current_price}
                marketValue={h.market_value}
                costBasis={h.cost_basis}
                pnl={h.pnl}
                pnlPct={h.pnl_pct}
                weight={h.weight}
                onEdit={() => window.dispatchEvent(new CustomEvent('portfolio-edit-stock', { detail: holdings[i] }))}
                onDelete={() => removeHolding(holdings[i].id)}
              />
            ))}
          </div>

          {/* AI 분석 영역 */}
          {analysisError && (
            <div style={{ color: theme.down, fontSize: FONT_SIZES.sm, marginBottom: SPACING.md }}>
              {analysisError}
            </div>
          )}

          {analysisResult ? (
            <PortfolioAnalysis
              analysis={analysisResult.analysis}
              aiReport={analysisResult.ai_report}
              onReanalyze={handleAnalyze}
              loading={analysisLoading}
            />
          ) : (
            <div
              style={{
                background: theme.bg_card,
                border: `1px solid ${theme.border}`,
                borderRadius: RADIUS.card,
                padding: SPACING.lg,
                textAlign: 'center',
              }}
            >
              <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.sm, marginBottom: SPACING.md }}>
                {holdings.length < 2
                  ? '2개 이상의 종목이 필요합니다.'
                  : 'AI가 포트폴리오를 종합 분석하고 리밸런싱을 제안합니다.'}
              </div>
              <button
                onClick={handleAnalyze}
                disabled={analysisLoading || holdings.length < 1}
                style={{
                  padding: `${SPACING.sm} ${SPACING.xl}`,
                  fontSize: FONT_SIZES.md,
                  fontWeight: 600,
                  color: theme.bg_primary,
                  background: theme.accent,
                  border: 'none',
                  borderRadius: RADIUS.button,
                  cursor: holdings.length < 1 ? 'not-allowed' : 'pointer',
                  opacity: analysisLoading || holdings.length < 1 ? 0.5 : 1,
                }}
              >
                {analysisLoading ? 'Analyzing...' : 'Analyze My Portfolio'}
              </button>
            </div>
          )}
        </>
      )}
      {modal}
    </div>
  );
}
