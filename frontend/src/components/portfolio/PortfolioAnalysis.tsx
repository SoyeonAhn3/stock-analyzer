import { useTheme } from '../../theme/ThemeProvider';
import { FONTS, FONT_SIZES, SPACING, RADIUS } from '../../theme/tokens';
import { useBreakpoint } from '../../hooks/useBreakpoint';

interface Props {
  analysis: Record<string, any>;
  aiReport: Record<string, any> | null;
  onReanalyze: () => void;
  loading: boolean;
}

function fmt(n: number | null | undefined, d = 2): string {
  if (n == null) return '—';
  return n.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
}

function pctFmt(n: number | null | undefined): string {
  if (n == null) return '—';
  const sign = n >= 0 ? '+' : '';
  return `${sign}${n.toFixed(2)}%`;
}

export default function PortfolioAnalysis({ analysis, aiReport, onReanalyze, loading }: Props) {
  const { theme } = useTheme();
  const bp = useBreakpoint();
  const isMobile = bp === 'mobile';

  const scores = analysis.scores ?? {};
  const concentration = analysis.concentration ?? {};
  const performance = analysis.performance ?? {};
  const risk = analysis.risk ?? {};
  const style = analysis.style ?? {};
  const macro = analysis.macro ?? {};
  const fundamentals = analysis.fundamentals ?? {};

  const card: React.CSSProperties = {
    background: theme.bg_card,
    border: `1px solid ${theme.border}`,
    borderRadius: RADIUS.card,
    padding: SPACING.lg,
    marginBottom: SPACING.md,
  };

  const sectionLabel: React.CSSProperties = {
    color: theme.text_muted,
    fontSize: FONT_SIZES.xs,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    marginBottom: SPACING.md,
  };

  return (
    <div>
      {/* 1. 헤더 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: SPACING.lg }}>
        <div>
          <span style={{ color: theme.accent, fontSize: FONT_SIZES.md, fontWeight: 700 }}>AI · PORTFOLIO </span>
          <span style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm }}>Risk & Allocation Review</span>
        </div>
        <button
          onClick={onReanalyze}
          disabled={loading}
          style={{
            padding: `${SPACING.xs} ${SPACING.sm}`,
            fontSize: FONT_SIZES.xs,
            color: theme.accent,
            border: `1px solid ${theme.accent}`,
            borderRadius: RADIUS.button,
            background: 'transparent',
            cursor: 'pointer',
            opacity: loading ? 0.5 : 1,
          }}
        >
          {loading ? 'Analyzing...' : '↻ Re-analyze'}
        </button>
      </div>

      {/* 2. 핵심 지표 3개 */}
      <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr 1fr', gap: SPACING.md, marginBottom: SPACING.md }}>
        <KeyMetricCard
          label="CONCENTRATION"
          value={concentration.hhi != null && concentration.hhi > 0.25 ? 'HIGH' : concentration.hhi != null && concentration.hhi > 0.15 ? 'MEDIUM' : 'LOW'}
          valueColor={concentration.hhi > 0.25 ? theme.down : concentration.hhi > 0.15 ? theme.warning : theme.up}
          sub={`HHI ${fmt(concentration.hhi, 4)} · ${fmt(concentration.effective_n, 1)} effective`}
          theme={theme}
        />
        <KeyMetricCard
          label="RISK SCORE"
          value={`${fmt(scores.risk_rating, 1)} / 10`}
          valueColor={scores.risk_rating > 7 ? theme.down : scores.risk_rating > 4 ? theme.warning : theme.up}
          sub={`Volatility ${fmt(risk.volatility ? risk.volatility * 100 : null, 1)}% · Beta ${fmt(risk.portfolio_beta, 2)}`}
          theme={theme}
        />
        <KeyMetricCard
          label="SHARPE RATIO"
          value={fmt(risk.sharpe, 2)}
          valueColor={risk.sharpe >= 1.0 ? theme.up : risk.sharpe >= 0.5 ? theme.warning : theme.down}
          sub={risk.sharpe >= 1.0 ? 'Good (>1.0)' : risk.sharpe >= 0.5 ? 'Fair (>0.5)' : 'Low (<0.5)'}
          theme={theme}
        />
      </div>

      {/* 3. 4대 점수 */}
      <div style={card}>
        <div style={sectionLabel}>Portfolio Scores</div>
        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr 1fr' : '1fr 1fr 1fr 1fr', gap: SPACING.md }}>
          <ScoreGauge label="Diversification" score={scores.diversification} theme={theme} invert={false} />
          <ScoreGauge label="Risk" score={scores.risk} theme={theme} invert={true} />
          <ScoreGauge label="Performance" score={scores.performance} theme={theme} invert={false} />
          <ScoreGauge label="Quality" score={scores.quality} theme={theme} invert={false} />
        </div>
      </div>

      {/* 4. 집중도 상세 */}
      <div style={card}>
        <div style={sectionLabel}>Concentration Analysis</div>
        <div style={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: SPACING.lg }}>
          <div style={{ flex: 1 }}>
            <div style={{ color: theme.text_secondary, fontSize: FONT_SIZES.xs, marginBottom: SPACING.sm }}>종목 집중도</div>
            {concentration.top_1 && (
              <div style={{ fontSize: FONT_SIZES.sm, color: theme.text_primary, marginBottom: '4px' }}>
                Top 1: <span style={{ fontFamily: FONTS.numeric, fontWeight: 600, color: theme.accent }}>{concentration.top_1.ticker} {fmt(concentration.top_1.weight, 1)}%</span>
              </div>
            )}
            <div style={{ fontSize: FONT_SIZES.sm, color: theme.text_primary, marginBottom: '4px' }}>
              Top 3: <span style={{ fontFamily: FONTS.numeric }}>{fmt(concentration.top_3_weight, 1)}%</span>
            </div>
            <div style={{ fontSize: FONT_SIZES.sm, color: theme.text_primary, marginBottom: SPACING.sm }}>
              HHI: <span style={{ fontFamily: FONTS.numeric }}>{fmt(concentration.hhi, 4)}</span>
              {' · '}유효 종목 수: <span style={{ fontFamily: FONTS.numeric }}>{fmt(concentration.effective_n, 1)}</span>
            </div>
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ color: theme.text_secondary, fontSize: FONT_SIZES.xs, marginBottom: SPACING.sm }}>섹터 집중도</div>
            {Object.entries(concentration.sector_weights ?? {}).map(([sector, weight]) => (
              <div key={sector} style={{ display: 'flex', alignItems: 'center', gap: SPACING.sm, marginBottom: '4px' }}>
                <span style={{ fontSize: FONT_SIZES.xs, color: theme.text_secondary, width: 120, flexShrink: 0 }}>{sector}</span>
                <div style={{ flex: 1, height: 8, background: theme.bg_primary, borderRadius: 4, overflow: 'hidden' }}>
                  <div style={{ width: `${Math.min(weight as number, 100)}%`, height: '100%', background: theme.accent, borderRadius: 4 }} />
                </div>
                <span style={{ fontSize: FONT_SIZES.xs, fontFamily: FONTS.numeric, color: theme.text_muted, width: 40, textAlign: 'right' }}>{fmt(weight as number, 1)}%</span>
              </div>
            ))}
            {(concentration.missing_sectors ?? []).length > 0 && (
              <div style={{ fontSize: FONT_SIZES.xs, color: theme.warning, marginTop: SPACING.sm }}>
                미보유 섹터 {concentration.missing_sectors.length}개: {concentration.missing_sectors.join(', ')}
              </div>
            )}
          </div>
        </div>
        {(risk.high_corr_pairs ?? []).length > 0 && (
          <div style={{ marginTop: SPACING.md, padding: SPACING.sm, background: `${theme.warning}10`, borderRadius: RADIUS.badge, border: `1px solid ${theme.warning}30` }}>
            <div style={{ color: theme.warning, fontSize: FONT_SIZES.xs, fontWeight: 600, marginBottom: SPACING.xs }}>동일 베팅 경고</div>
            {risk.high_corr_pairs.map((p: any, i: number) => (
              <div key={i} style={{ fontSize: FONT_SIZES.xs, color: theme.text_secondary }}>
                {p.pair[0]} ↔ {p.pair[1]}: 상관계수 {fmt(p.correlation, 2)}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 5. 성과 분석 */}
      <div style={card}>
        <div style={sectionLabel}>Performance</div>
        <div style={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: SPACING.lg }}>
          <div style={{ flex: 1 }}>
            <MetricRow label="총 투자금액" value={`$${fmt(performance.summary?.total_cost_basis)}`} theme={theme} />
            <MetricRow label="총 평가금액" value={`$${fmt(performance.summary?.total_market_value)}`} theme={theme} />
            <MetricRow label="총 수익" value={`$${fmt(performance.summary?.total_pnl)}`} theme={theme}
              valueColor={(performance.summary?.total_pnl ?? 0) >= 0 ? theme.up : theme.down} />
            <MetricRow label="총 수익률" value={pctFmt(performance.total_return)} theme={theme}
              valueColor={(performance.total_return ?? 0) >= 0 ? theme.up : theme.down} />
          </div>
          <div style={{ flex: 1 }}>
            <MetricRow label="내 포트폴리오" value={pctFmt(performance.total_return)} theme={theme}
              valueColor={(performance.total_return ?? 0) >= 0 ? theme.up : theme.down} />
            <MetricRow label="S&P 500" value={pctFmt(performance.benchmark_return)} theme={theme} />
            <MetricRow label="Alpha (초과수익)" value={`${pctFmt(performance.alpha)}p`} theme={theme}
              valueColor={(performance.alpha ?? 0) >= 0 ? theme.up : theme.down} bold />
          </div>
        </div>
        {(performance.contributions ?? []).length > 0 && (
          <div style={{ marginTop: SPACING.md }}>
            <div style={{ color: theme.text_secondary, fontSize: FONT_SIZES.xs, marginBottom: SPACING.sm }}>종목별 수익 기여도</div>
            {performance.contributions.map((c: any) => {
              const pnl = c.pnl ?? 0;
              const maxContrib = Math.max(...performance.contributions.map((x: any) => Math.abs(x.contribution_pct ?? 0)), 1);
              const barW = Math.max((Math.abs(c.contribution_pct ?? 0) / maxContrib) * 100, 2);
              const color = pnl >= 0 ? theme.up : theme.down;
              return (
                <div key={c.ticker} style={{ display: 'flex', alignItems: 'center', gap: SPACING.sm, marginBottom: '4px' }}>
                  <span style={{ width: 48, fontSize: FONT_SIZES.xs, color: theme.text_secondary, textAlign: 'right', flexShrink: 0 }}>{c.ticker}</span>
                  <div style={{ flex: 1, height: 14, background: theme.bg_primary, borderRadius: RADIUS.badge, overflow: 'hidden' }}>
                    <div style={{ width: `${barW}%`, height: '100%', background: color, borderRadius: RADIUS.badge, opacity: 0.8 }} />
                  </div>
                  <span style={{ width: 80, fontSize: FONT_SIZES.xs, fontFamily: FONTS.numeric, color, textAlign: 'right', flexShrink: 0 }}>
                    {pctFmt(c.contribution_pct)}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 6. 위험 분석 */}
      <div style={card}>
        <div style={sectionLabel}>Risk Metrics</div>
        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr 1fr' : '1fr 1fr 1fr 1fr', gap: SPACING.md, marginBottom: SPACING.md }}>
          <MiniMetric label="연간 변동성" value={risk.volatility != null ? `${(risk.volatility * 100).toFixed(1)}%` : '—'} theme={theme}
            warn={risk.volatility > 0.25} />
          <MiniMetric label="포트폴리오 Beta" value={fmt(risk.portfolio_beta, 2)} theme={theme}
            warn={Math.abs(risk.portfolio_beta ?? 0) > 1.5} />
          <MiniMetric label="최대 낙폭(MDD)" value={risk.mdd != null ? `${(risk.mdd * 100).toFixed(1)}%` : '—'} theme={theme}
            warn={(risk.mdd ?? 0) < -0.2} />
          <MiniMetric label="VaR (95%, 30일)" value={risk.var_95_30d != null ? `$${fmt(Math.abs(risk.var_95_30d))}` : '—'} theme={theme}
            sub={risk.var_95_30d_pct != null ? `평가금액의 ${Math.abs(risk.var_95_30d_pct).toFixed(1)}%` : undefined} />
        </div>

        {/* 상관관계 행렬 */}
        {risk.correlation && typeof risk.correlation === 'object' && Object.keys(risk.correlation).length > 1 && (
          <CorrelationMatrix correlation={risk.correlation} theme={theme} />
        )}
        {risk.avg_correlation != null && (
          <div style={{ fontSize: FONT_SIZES.xs, color: theme.text_muted, marginTop: SPACING.sm }}>
            평균 상관계수: <span style={{ fontFamily: FONTS.numeric }}>{fmt(risk.avg_correlation, 2)}</span>
          </div>
        )}

        {/* 유동성 */}
        {(risk.liquidity ?? []).length > 0 && (
          <div style={{ marginTop: SPACING.md }}>
            <div style={{ color: theme.text_secondary, fontSize: FONT_SIZES.xs, marginBottom: SPACING.sm }}>유동성 리스크</div>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: FONT_SIZES.xs }}>
                <thead>
                  <tr>
                    {['종목', '시총', '평균거래량(20일)', '판정'].map((h) => (
                      <th key={h} style={{ textAlign: 'left', color: theme.text_muted, padding: `${SPACING.xs} ${SPACING.sm}`, borderBottom: `1px solid ${theme.border}` }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {risk.liquidity.map((l: any) => (
                    <tr key={l.ticker}>
                      <td style={{ padding: `${SPACING.xs} ${SPACING.sm}`, color: theme.text_primary, fontWeight: 600 }}>{l.ticker}</td>
                      <td style={{ padding: `${SPACING.xs} ${SPACING.sm}`, color: theme.text_secondary, textTransform: 'capitalize' }}>{l.cap_tier}</td>
                      <td style={{ padding: `${SPACING.xs} ${SPACING.sm}`, color: theme.text_secondary, fontFamily: FONTS.numeric }}>
                        {l.avg_volume_20d ? l.avg_volume_20d.toLocaleString() : '—'}
                      </td>
                      <td style={{ padding: `${SPACING.xs} ${SPACING.sm}` }}>
                        <span style={{ color: l.flag === 'safe' ? theme.up : l.flag === 'caution' ? theme.warning : theme.down }}>
                          {l.flag === 'safe' ? '✓ Safe' : l.flag === 'caution' ? '⚠ Caution' : '⚠ Danger'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* 7. 스타일 분석 */}
      <div style={card}>
        <div style={sectionLabel}>Portfolio Style</div>
        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr', gap: SPACING.md }}>
          <StyleBar label="성장 vs 가치" left="성장" right="가치" leftPct={style.growth_pct} rightPct={style.value_pct} theme={theme} />
          <StyleBar label="시총 규모" left="대형" right="소형" leftPct={style.large_pct} rightPct={style.small_pct} midPct={style.mid_pct} theme={theme} />
          <StyleBar label="배당 여부" left="배당" right="비배당" leftPct={style.dividend_pct} rightPct={style.non_dividend_pct} theme={theme} />
          <StyleBar label="경기 민감도" left="경기민감" right="방어" leftPct={style.cyclical_pct} rightPct={style.defensive_pct} theme={theme} />
        </div>
        {fundamentals.annual_dividend != null && (
          <div style={{ marginTop: SPACING.md, fontSize: FONT_SIZES.xs, color: theme.text_muted }}>
            연간 예상 배당금: <span style={{ fontFamily: FONTS.numeric, color: theme.text_secondary }}>${fmt(fundamentals.annual_dividend)}</span>
            {' · '}Yield on Cost: <span style={{ fontFamily: FONTS.numeric, color: theme.text_secondary }}>{fmt(fundamentals.yield_on_cost, 2)}%</span>
          </div>
        )}
      </div>

      {/* 8. 거시 노출도 */}
      <div style={card}>
        <div style={sectionLabel}>Macro Exposure</div>
        {macro.rate_sensitivity && (
          <div style={{ marginBottom: SPACING.md }}>
            <div style={{ fontSize: FONT_SIZES.sm, color: theme.text_primary, marginBottom: SPACING.xs }}>
              금리 민감도:
              <span style={{
                marginLeft: SPACING.sm,
                fontWeight: 600,
                color: macro.rate_sensitivity.level === 'high' ? theme.down : macro.rate_sensitivity.level === 'medium' ? theme.warning : theme.up,
              }}>
                {macro.rate_sensitivity.level?.toUpperCase()}
              </span>
            </div>
            <div style={{ fontSize: FONT_SIZES.xs, color: theme.text_muted }}>
              PER 30+ 종목 비중: <span style={{ fontFamily: FONTS.numeric }}>{fmt(macro.rate_sensitivity.high_per_weight, 1)}%</span>
            </div>
          </div>
        )}
        {(macro.same_macro_bets ?? []).length > 0 && (
          <div style={{ padding: SPACING.sm, background: `${theme.warning}10`, borderRadius: RADIUS.badge, border: `1px solid ${theme.warning}30`, marginBottom: SPACING.sm }}>
            <div style={{ color: theme.warning, fontSize: FONT_SIZES.xs, fontWeight: 600, marginBottom: SPACING.xs }}>동일 매크로 베팅 감지</div>
            {macro.same_macro_bets.map((bet: any, i: number) => (
              <div key={i} style={{ fontSize: FONT_SIZES.xs, color: theme.text_secondary }}>
                {bet.tickers.join(' + ')} — {bet.sector} (상관계수 {fmt(bet.correlation, 2)})
              </div>
            ))}
          </div>
        )}
        {(macro.sector_clusters ?? []).length > 0 && (
          <div>
            <div style={{ fontSize: FONT_SIZES.xs, color: theme.text_muted, marginBottom: SPACING.xs }}>섹터 클러스터 (3종목 이상 동일 섹터)</div>
            {macro.sector_clusters.map((cl: any, i: number) => (
              <div key={i} style={{ fontSize: FONT_SIZES.xs, color: theme.text_secondary }}>
                {cl.sector}: {cl.tickers.join(', ')} (합산 {fmt(cl.combined_weight, 1)}%)
              </div>
            ))}
          </div>
        )}
        {(macro.same_macro_bets ?? []).length === 0 && (macro.sector_clusters ?? []).length === 0 && macro.rate_sensitivity?.level === 'low' && (
          <div style={{ fontSize: FONT_SIZES.xs, color: theme.up }}>거시 경제 리스크 노출이 낮습니다.</div>
        )}
      </div>

      {/* 9. 펀더멘털 */}
      <div style={card}>
        <div style={sectionLabel}>Portfolio Fundamentals (비중 가중평균)</div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: FONT_SIZES.sm }}>
            <tbody>
              <FundRow label="PER" value={fundamentals.weighted_pe != null ? `${fmt(fundamentals.weighted_pe, 1)}배` : '—'} theme={theme} />
              <FundRow label="ROE" value={fundamentals.weighted_roe != null ? `${(fundamentals.weighted_roe * 100).toFixed(1)}%` : '—'} theme={theme} />
              <FundRow label="부채비율" value={fundamentals.weighted_de_ratio != null ? fmt(fundamentals.weighted_de_ratio, 1) : '—'} theme={theme} />
              <FundRow label="영업이익률" value={fundamentals.weighted_operating_margin != null ? `${(fundamentals.weighted_operating_margin * 100).toFixed(1)}%` : '—'} theme={theme} />
              <FundRow label="배당수익률" value={fundamentals.weighted_dividend_yield != null ? `${(fundamentals.weighted_dividend_yield * 100).toFixed(2)}%` : '—'} theme={theme} />
              <FundRow label="연간 배당금" value={fundamentals.annual_dividend != null ? `$${fmt(fundamentals.annual_dividend)}` : '—'} theme={theme} />
            </tbody>
          </table>
        </div>
      </div>

      {/* 10. AI 종합 리포트 */}
      {aiReport && (
        <div style={card}>
          <div style={sectionLabel}>AI Insights</div>
          {aiReport.summary && (
            <div style={{ color: theme.text_primary, fontSize: FONT_SIZES.md, fontWeight: 600, marginBottom: SPACING.md, lineHeight: '1.5' }}>
              {aiReport.summary as string}
            </div>
          )}

          {(aiReport.strengths as string[] ?? []).length > 0 && (
            <AiSection title="Strengths" items={aiReport.strengths as string[]} color={theme.up} theme={theme} />
          )}

          {(aiReport.risks as string[] ?? []).length > 0 && (
            <AiSection title="Risks" items={aiReport.risks as string[]} color={theme.down} theme={theme} />
          )}

          {(aiReport.rebalancing as any[] ?? []).length > 0 && (
            <div style={{ marginTop: SPACING.md }}>
              <div style={{ color: theme.text_primary, fontSize: FONT_SIZES.sm, fontWeight: 600, marginBottom: SPACING.sm }}>Rebalancing</div>
              {(aiReport.rebalancing as any[]).map((r: any, i: number) => (
                <div key={i} style={{ marginBottom: SPACING.sm, paddingLeft: SPACING.md, borderLeft: `2px solid ${theme.accent}` }}>
                  <div style={{ fontSize: FONT_SIZES.sm, color: theme.text_primary, fontWeight: 600 }}>{r.action}</div>
                  <div style={{ fontSize: FONT_SIZES.xs, color: theme.text_muted }}>{r.reason}</div>
                </div>
              ))}
            </div>
          )}

          {aiReport.rebalancing_comparison && (
            <div style={{ marginTop: SPACING.md, overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: FONT_SIZES.xs }}>
                <thead>
                  <tr>
                    {['', 'Before', 'After'].map((h) => (
                      <th key={h} style={{ textAlign: h ? 'right' : 'left', color: theme.text_muted, padding: `${SPACING.xs} ${SPACING.sm}`, borderBottom: `1px solid ${theme.border}` }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {['tech_pct', 'defensive_pct', 'hhi', 'estimated_sharpe'].map((key) => {
                    const comp = aiReport.rebalancing_comparison as any;
                    const before = comp?.before?.[key];
                    const after = comp?.after?.[key];
                    const labels: Record<string, string> = { tech_pct: 'Tech 비중', defensive_pct: '방어 섹터', hhi: 'HHI', estimated_sharpe: 'Sharpe' };
                    if (before == null && after == null) return null;
                    return (
                      <tr key={key}>
                        <td style={{ padding: `${SPACING.xs} ${SPACING.sm}`, color: theme.text_secondary }}>{labels[key] ?? key}</td>
                        <td style={{ padding: `${SPACING.xs} ${SPACING.sm}`, textAlign: 'right', fontFamily: FONTS.numeric, color: theme.text_primary }}>
                          {key.includes('pct') ? `${fmt(before, 1)}%` : fmt(before, 2)}
                        </td>
                        <td style={{ padding: `${SPACING.xs} ${SPACING.sm}`, textAlign: 'right', fontFamily: FONTS.numeric, color: theme.accent }}>
                          {key.includes('pct') ? `${fmt(after, 1)}%` : fmt(after, 2)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

          {aiReport.disclaimer && (
            <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginTop: SPACING.lg, fontStyle: 'italic' }}>
              {aiReport.disclaimer as string}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/* ── 서브 컴포넌트 ── */

function KeyMetricCard({ label, value, valueColor, sub, theme }: { label: string; value: string; valueColor: string; sub: string; theme: any }) {
  return (
    <div style={{ background: theme.bg_card, border: `1px solid ${theme.border}`, borderRadius: RADIUS.card, padding: SPACING.md, textAlign: 'center' }}>
      <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: SPACING.sm }}>{label}</div>
      <div style={{ fontFamily: FONTS.numeric, fontSize: FONT_SIZES['2xl'], fontWeight: 700, color: valueColor }}>{value}</div>
      <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginTop: SPACING.xs }}>{sub}</div>
    </div>
  );
}

function ScoreGauge({ label, score, theme, invert }: { label: string; score: number; theme: any; invert: boolean }) {
  const s = score ?? 0;
  const getColor = () => {
    if (invert) return s > 66 ? theme.down : s > 33 ? theme.warning : theme.up;
    return s > 66 ? theme.up : s > 33 ? theme.warning : theme.down;
  };
  const getLabel = () => {
    if (invert) return s > 66 ? '높음 ⚠' : s > 33 ? '보통' : '낮음 ✓';
    return s > 66 ? '우수 ✓' : s > 33 ? '보통' : '낮음 ⚠';
  };

  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ fontFamily: FONTS.numeric, fontSize: FONT_SIZES['2xl'], fontWeight: 700, color: theme.text_primary }}>{s}</div>
      <div style={{ fontSize: FONT_SIZES.xs, color: theme.text_muted, marginBottom: SPACING.xs }}>/100</div>
      <div style={{ height: 6, background: theme.bg_primary, borderRadius: 3, overflow: 'hidden', marginBottom: SPACING.xs }}>
        <div style={{ width: `${s}%`, height: '100%', background: getColor(), borderRadius: 3 }} />
      </div>
      <div style={{ fontSize: FONT_SIZES.xs, color: getColor() }}>{getLabel()}</div>
      <div style={{ fontSize: FONT_SIZES.xs, color: theme.text_muted, marginTop: '2px' }}>{label}</div>
    </div>
  );
}

function MetricRow({ label, value, theme, valueColor, bold }: { label: string; value: string; theme: any; valueColor?: string; bold?: boolean }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: `3px 0`, fontSize: FONT_SIZES.sm }}>
      <span style={{ color: theme.text_secondary }}>{label}</span>
      <span style={{ fontFamily: FONTS.numeric, fontWeight: bold ? 700 : 400, color: valueColor ?? theme.text_primary }}>{value}</span>
    </div>
  );
}

function MiniMetric({ label, value, theme, warn, sub }: { label: string; value: string; theme: any; warn?: boolean; sub?: string }) {
  return (
    <div style={{ textAlign: 'center', padding: SPACING.sm, background: theme.bg_primary, borderRadius: RADIUS.badge }}>
      <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginBottom: SPACING.xs }}>{label}</div>
      <div style={{ fontFamily: FONTS.numeric, fontSize: FONT_SIZES.xl, fontWeight: 700, color: warn ? theme.warning : theme.text_primary }}>{value}</div>
      {sub && <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginTop: '2px' }}>{sub}</div>}
    </div>
  );
}

function CorrelationMatrix({ correlation, theme }: { correlation: Record<string, Record<string, number>>; theme: any }) {
  const tickers = Object.keys(correlation);
  if (tickers.length === 0) return null;

  return (
    <div style={{ marginTop: SPACING.md }}>
      <div style={{ color: theme.text_secondary, fontSize: FONT_SIZES.xs, marginBottom: SPACING.sm }}>상관관계 행렬</div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'collapse', fontSize: FONT_SIZES.xs }}>
          <thead>
            <tr>
              <th style={{ padding: `${SPACING.xs} ${SPACING.sm}` }} />
              {tickers.map((t) => (
                <th key={t} style={{ padding: `${SPACING.xs} ${SPACING.sm}`, color: theme.text_muted, textAlign: 'center' }}>{t}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {tickers.map((t1) => (
              <tr key={t1}>
                <td style={{ padding: `${SPACING.xs} ${SPACING.sm}`, color: theme.text_muted, fontWeight: 600 }}>{t1}</td>
                {tickers.map((t2) => {
                  const val = correlation[t1]?.[t2] ?? 0;
                  const color = t1 === t2 ? theme.text_muted : val > 0.75 ? theme.down : val > 0.5 ? theme.warning : theme.up;
                  return (
                    <td key={t2} style={{ padding: `${SPACING.xs} ${SPACING.sm}`, textAlign: 'center', fontFamily: FONTS.numeric, color }}>
                      {val.toFixed(2)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StyleBar({ label, left, right, leftPct, rightPct, midPct, theme }: { label: string; left: string; right: string; leftPct: number; rightPct: number; midPct?: number; theme: any }) {
  return (
    <div>
      <div style={{ color: theme.text_secondary, fontSize: FONT_SIZES.xs, marginBottom: SPACING.xs }}>{label}</div>
      <div style={{ display: 'flex', height: 16, borderRadius: RADIUS.badge, overflow: 'hidden', background: theme.bg_primary }}>
        {leftPct > 0 && <div style={{ width: `${leftPct}%`, background: theme.accent, opacity: 0.8 }} />}
        {midPct != null && midPct > 0 && <div style={{ width: `${midPct}%`, background: theme.warning, opacity: 0.6 }} />}
        {rightPct > 0 && <div style={{ width: `${rightPct}%`, background: theme.text_muted, opacity: 0.4 }} />}
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: FONT_SIZES.xs, marginTop: '2px' }}>
        <span style={{ color: theme.accent }}>{left} {fmt(leftPct, 0)}%</span>
        {midPct != null && midPct > 0 && <span style={{ color: theme.warning }}>중형 {fmt(midPct, 0)}%</span>}
        <span style={{ color: theme.text_muted }}>{right} {fmt(rightPct, 0)}%</span>
      </div>
    </div>
  );
}

function FundRow({ label, value, theme }: { label: string; value: string; theme: any }) {
  return (
    <tr>
      <td style={{ padding: `${SPACING.xs} ${SPACING.sm}`, color: theme.text_secondary, borderBottom: `1px solid ${theme.border}` }}>{label}</td>
      <td style={{ padding: `${SPACING.xs} ${SPACING.sm}`, fontFamily: FONTS.numeric, color: theme.text_primary, textAlign: 'right', borderBottom: `1px solid ${theme.border}` }}>{value}</td>
    </tr>
  );
}

function AiSection({ title, items, color, theme }: { title: string; items: string[]; color: string; theme: any }) {
  return (
    <div style={{ marginTop: SPACING.md }}>
      <div style={{ color, fontSize: FONT_SIZES.sm, fontWeight: 600, marginBottom: SPACING.sm }}>{title}</div>
      <ul style={{ margin: 0, paddingLeft: SPACING.md, color: theme.text_secondary, fontSize: FONT_SIZES.sm, lineHeight: '1.6' }}>
        {items.map((s, i) => <li key={i}>{s}</li>)}
      </ul>
    </div>
  );
}
