# Phase 13 — Portfolio `✅ Completed`

> Holdings tracking + quantitative analysis pipeline + AI report + cross-device sync

**Completed**: 2026-04-27
**Status**: ✅ Completed
**Prerequisites**: Phase 12 completed (UI/UX + Mobile Optimization)
**Design Reference**: `pre-requirement/image.png`, `pre-requirement/20260427_115228.png`
**Feature Spec**: `pre-requirement/portfolio-design-spec.md`
**AI Output Example**: `pre-requirement/portfolio-analysis-example.md`

---

## Overview

Users enter their holdings (ticker, shares, average cost) and the system auto-fetches current prices to calculate returns. A 9-step quantitative analysis pipeline analyzes the entire portfolio, then AI converts the calculated numbers into a natural-language report with risk warnings and rebalancing suggestions. Data is stored in LocalStorage, with optional cross-device sync via code+PIN.

**Core design principle**: Python performs all quantitative calculations; AI only interprets the calculated numbers. AI never computes.

---

## Deliverables

| # | Module | Status | Type | Est. Hours |
|---|---|---|---|---|
| 1 | Backend — Portfolio Data Model + CRUD API | ✅ | project-specific | 2h |
| 2 | Backend — Quantitative Analysis Pipeline (Steps 2-7) | ✅ | project-specific | 3h |
| 3 | Backend — AI Report Agent (Step 8) | ✅ | project-specific | 2h |
| 4 | Frontend — Portfolio Main Page | ✅ | project-specific | 4h |
| 5 | Frontend — Add/Edit Stock Modal | ✅ | project-specific | 2h |
| 6 | Frontend — AI Analysis Display (10 sections) | ✅ | project-specific | 3h |
| 7 | Frontend — Navigation Integration | ✅ | project-specific | 0.5h |
| 8 | Cross-Device Sync | ✅ | project-specific | 3h |

**Total: ~17 hours**

---

## Step 1: Backend — Data Model + CRUD API

### Data Model

```python
PortfolioHolding = {
    "id": str,              # UUID
    "ticker": str,          # "AAPL"
    "shares": int,          # 45
    "avg_cost": float,      # 142.30
    "currency": str,        # "USD"
    "purchase_date": str,   # "2025-03-15" (optional)
    "memo": str,            # max 100 chars (optional)
    "created_at": str,      # ISO 8601
    "updated_at": str       # ISO 8601
}
```

### API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/portfolio/holdings` | Add holding |
| PUT | `/api/portfolio/holdings/{id}` | Edit holding |
| DELETE | `/api/portfolio/holdings/{id}` | Delete holding |
| GET | `/api/portfolio/holdings` | List all holdings + current prices |
| POST | `/api/portfolio/analyze` | Run 9-step analysis |
| GET | `/api/portfolio/analyze/cache` | Get cached analysis result |

### Storage Architecture

- **Default**: Frontend LocalStorage stores holdings array (not sent to server for storage)
- **On analysis**: Frontend sends holdings in POST body → server analyzes without storing → returns result
- **No user data persists on server** (privacy by design)

---

## Step 2: Backend — Quantitative Analysis Pipeline

Nine steps, all pure Python math — no AI calls.

### 2-1. Current Price + Metadata Collection
```
Input: holdings array
Output: per-ticker {current_price, sector, country, market_cap, beta, fundamentals, 1yr daily returns}
Data sources: quote.py (Finnhub → yfinance), fundamentals.py (yfinance → FMP → Finviz), yfinance 1yr OHLCV
Benchmark: yfinance ^GSPC (S&P 500) 1yr daily returns
All tickers fetched in parallel via asyncio.gather.
```

### 2-2. Valuation & Weight Calculation
```
Per holding:
  market_value = current_price * shares
  cost_basis = avg_cost * shares
  pnl = market_value - cost_basis
  pnl_pct = pnl / cost_basis * 100
  weight = market_value / total_market_value * 100

Portfolio total:
  total_market_value = sum(market_value)
  total_cost_basis = sum(cost_basis)
  total_pnl = total_market_value - total_cost_basis
  total_pnl_pct = total_pnl / total_cost_basis * 100
```

### 2-3. Concentration Analysis
```
top_1_weight, top_3_weight, top_5_weight
sector_weights = {sector: sum of weights}
country_weights = {country: sum of weights}
HHI = sum((weight_i / 100)^2)    # 0~1, higher = more concentrated
effective_n = 1 / HHI
```

### 2-4. Weighted Fundamentals
```
weighted_per, weighted_pbr, weighted_roe, weighted_debt_ratio,
weighted_op_margin, weighted_dividend_yield
annual_dividend = sum(current_price_i * dividend_yield_i * shares_i)
```

### 2-5. Performance Analysis
```
contribution_i = pnl_i / total_cost_basis * 100
benchmark_return = S&P 500 return over same period
alpha = portfolio_return - benchmark_return
```

### 2-6. Risk Analysis
```python
volatility = np.std(port_daily_returns) * sqrt(252)
portfolio_beta = cov(portfolio, benchmark) / var(benchmark)
mdd = min(drawdown series)
sharpe = mean(excess_returns) / std(excess_returns) * sqrt(252)
var_95_30d = percentile(daily_returns, 5) * sqrt(30) * total_value
correlation_matrix = np.corrcoef(returns_matrix)
liquidity_flag = "safe" | "caution" | "danger"  # based on volume ratio
```

### 2-7. Style Analysis
```
Per holding:
  style = "growth" if PER > 25 or revenue_growth > 15% else "value"
  cap = "large" (>$10B) | "mid" (>$2B) | "small"
  dividend = "dividend" if yield > 1% else "non-dividend"
  cycle = "cyclical" if sector in [Tech, Consumer Disc, Financials, Materials, Energy] else "defensive"

Portfolio level: growth_pct, value_pct, large_pct, mid_pct, small_pct, cyclical_pct, defensive_pct
```

### 2-8. Macro Exposure
```
high_per_weight = sum of weights where PER > 30 (interest rate sensitivity)
Same-macro-bet detection: if correlation > 0.75 AND same sector → flag
```

### 2-9. Scoring (0-100)
```
Diversification = hhi_score(40) + sector_score(30) + corr_score(30)
Risk = vol(30) + beta(30) + mdd(20) + concentration(20)  → risk_rating = score/10
Performance = return_score(40) + alpha_score(30) + sharpe_score(30)
Quality = roe(30) + debt(30) + margin(20) + liquidity(20)
```

---

## Step 3: Backend — AI Report Agent

### Design Principles
- AI never recalculates — only interprets Step 2 results
- Prompt includes explicit judgment criteria
- All suggestions must cite source numbers

### Judgment Criteria in Prompt
```
HHI > 0.25: concentration risk
Single sector > 40%: sector bias
Correlation > 0.75 + same sector: same bet
Beta > 1.5: high risk
MDD > -20%: psychological stress risk
Sharpe < 0.5: poor risk-adjusted return
Liquidity flag "danger": immediate warning
```

### AI Output Schema

```json
{
  "summary": "One-line portfolio summary",
  "concentration": { "level": "HIGH|MEDIUM|LOW", "hhi": 0.24, "detail": "..." },
  "risk_score": { "score": 7.4, "breakdown": "..." },
  "strengths": ["..."],
  "risks": ["..."],
  "rebalancing": [
    { "action": "NVDA 32.8% → 20%", "reason": "Beta 1.65, highest volatility" }
  ],
  "rebalancing_comparison": {
    "before": { "tech_pct": 84.0, "defensive_pct": 0, "hhi": 0.24, "sharpe": 1.52 },
    "after": { "tech_pct": 55, "defensive_pct": 20, "hhi": 0.15, "sharpe": 1.35 }
  },
  "macro_warning": "...",
  "style_summary": "...",
  "disclaimer": "This analysis is AI-generated reference material, not financial advice."
}
```

### Implementation Files

| Location | File | Role |
|---|---|---|
| Backend | `agents/portfolio_agent.py` | AI report agent |
| Backend | `services/portfolio_calculator.py` | 9-step quantitative pipeline |

---

## Step 4: Frontend — Portfolio Main Page

### Layout (Portfolio.tsx)

```
+--------------------------------------------------+
| Portfolio                    Refresh  Export  +Add |
+-------------------------+------------------------+
| TOTAL MARKET VALUE       | COST BASIS             |
| $41,732.65  Live         | $28,694.00             |
| Today +$175.28  +45.44%  | UNREALIZED P&L         |
| [mini line chart]        | +$13,037.85 +45.4%     |
|                          | BEST: AAPL +91.88%     |
|                          | WORST: TSLA -8.28%     |
+-------------------------+------------------------+
| ALLOCATION & PERFORMANCE      All 1M 3M YTD 1Y    |
+-----------------------+--------------------------+
| Position Weight       | Return by Position        |
| [Donut chart]         | [Horizontal bar chart]    |
| Center: 5 positions   | Green=profit, Red=loss    |
+-----------------------+--------------------------+
| HOLDINGS (5)               Sort: Return Value Name |
| [Holding card list]                                |
+--------------------------------------------------+
| AI PORTFOLIO: Risk & Allocation Review             |
| [Step 6 area]                                      |
+--------------------------------------------------+
```

### Mobile Adaptation
- Summary cards: vertical stack
- Donut + bar chart: vertical stack
- Holding cards: compressed layout (1 line: ticker+return, 2: qty+price, 3: P&L)

### Data Flow
```
LocalStorage (holdings)
  → usePortfolio() custom hook
    → GET /api/portfolio/holdings (current price fetch)
    → Auto-refresh every 60 seconds
    → Render
```

### Empty State
0 holdings: "No stocks added yet. Add your first stock." + [+ Add Stock] button

---

## Step 5: Frontend — Add/Edit Stock Modal

### Fields

| Field | Required | Type | Validation |
|---|---|---|---|
| Ticker | Yes | Text + autocomplete | API validation |
| Shares | Yes | Integer | > 0 |
| Average Cost | Yes | Decimal (2 places) | > 0 |
| Currency | Yes | Dropdown (USD default) | — |
| Purchase Date | No | Date picker | Before today |
| Memo | No | Text | Max 100 chars |

### Behavior
- Add mode: all fields editable, "Save" button
- Edit mode: ticker locked (read-only), "Update" button
- Save button disabled until 3 required fields filled
- Saves to LocalStorage immediately

---

## Step 6: Frontend — AI Analysis Display (10 Sections)

Rendered in order after analysis completes:
1. Header (last analysis time + Re-analyze)
2. Key metrics (Concentration, Risk Score, Sharpe)
3. Four scores (Diversification/Risk/Performance/Quality with breakdown)
4. Concentration detail (holding/sector concentration, same-bet warnings)
5. Performance (benchmark comparison, contribution)
6. Risk (volatility/beta/MDD/VaR, correlation matrix, liquidity)
7. Style (growth/value, large/small, dividend, cyclical/defensive)
8. Macro exposure (interest rate sensitivity, same-macro-bet detection)
9. Fundamentals (weighted PER/PBR/ROE etc.)
10. AI report (summary/strengths/risks/rebalancing + before/after comparison)

### Trigger
- [Analyze My Portfolio] button (active when ≥2 holdings)
- Loading: skeleton + "AI is analyzing your portfolio..."
- Disclaimer always shown at bottom

---

## Step 7: Frontend — Navigation Integration

### PC Sidebar
```
Market Overview
Quick Look
Compare Mode
Portfolio        <-- New
Sector Screening
Beginner's Guide
```

### Mobile Bottom Tab
```
Home — Analysis — Portfolio — Sector — Settings
                   <-- New (briefcase icon)
```
4 tabs → 5 tabs. Added to `BottomTabBar.tsx` TABS array.

---

## Step 8: Cross-Device Sync

### Mechanism
- **Sync code**: 12-character random code (e.g., ABCD-1234-EFGH)
- **PIN**: 4-digit number
- No signup/login required
- Data inaccessible without code+PIN

### API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/sync/create` | Generate new sync code (set PIN) |
| POST | `/api/sync/connect` | Connect with existing code (verify code+PIN) |
| POST | `/api/sync/push` | Upload local data to server |
| GET | `/api/sync/pull` | Download server data to local |
| DELETE | `/api/sync/disconnect` | Disconnect + delete server data |

### Security
- PIN stored as bcrypt hash
- 3 consecutive failures → 30-second lockout
- 90 days of inactivity → auto-delete server data
- Conflict resolution: last-write-wins (timestamp)

### Settings Page Addition
- No sync configured: [Create Sync Code] / [Enter Existing Code] buttons
- Sync active: code display + last sync time + [Sync Now] + [Disconnect]

---

## Implementation Order & Dependencies

```
Step 1 (CRUD API)
  |
Step 2 (Quantitative Analysis) <-- Core, most time-consuming
  |
Step 3 (AI Report) <-- Needs Step 2 results
  |
Step 4 (Main Page) + Step 5 (Modal) <-- Can parallelize
  |
Step 6 (AI Display) <-- Needs Step 3 + Step 4
  |
Step 7 (Navigation) <-- Needs Step 4
  |
Step 8 (Sync) <-- Independent, added last
```

---

## Implementation Files

### New Files

| Location | File | Role |
|---|---|---|
| Backend | `backend/routers/portfolio.py` | Portfolio CRUD + analysis API |
| Backend | `services/portfolio_calculator.py` | Quantitative calculation module |
| Backend | `agents/portfolio_agent.py` | AI report agent |
| Backend | `backend/routers/sync.py` | Sync API |
| Backend | `services/sync_service.py` | Sync logic + PIN hash |
| Frontend | `pages/Portfolio.tsx` | Portfolio main page |
| Frontend | `components/AddStockModal.tsx` | Add/edit stock modal |
| Frontend | `components/PortfolioAIReport.tsx` | AI analysis result display |
| Frontend | `components/PortfolioCharts.tsx` | Donut + bar charts |
| Frontend | `components/HoldingCard.tsx` | Individual holding card |
| Frontend | `hooks/usePortfolio.ts` | Portfolio state management hook |
| Frontend | `services/portfolioApi.ts` | API call functions |

### Modified Files

| File | Change |
|---|---|
| `frontend/src/App.tsx` | Portfolio route added |
| `frontend/src/components/Sidebar.tsx` | Portfolio menu item added |
| `frontend/src/components/BottomTabBar.tsx` | Portfolio tab added (4→5 tabs) |
| `frontend/src/pages/Settings.tsx` | PORTFOLIO SYNC section added |
| `backend/main.py` | portfolio, sync routers registered |

---

## Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Data storage | LocalStorage (default) + server sync (optional) | Privacy — no user data on server by default |
| Quant/AI separation | Python calculates + AI interprets | Prevents AI hallucination, ensures number precision |
| Benchmark | S&P 500 (^GSPC) | Standard for US stock portfolios |
| Chart library | lightweight-charts (existing) + custom SVG | No additional dependencies |
| Sync auth | Code+PIN (no login) | OAuth overkill for personal project, simple security |
| Conflict resolution | Last-write-wins | Single-user scenario, CRDT unnecessary |

---

## Change Log

| Date | Description |
|---|---|
| 2026-04-27 | Initial creation |
| 2026-04-27 | AI output example separated to portfolio-analysis-example.md |
| 2026-04-27 | Stress test removed, total 20h → 17h |
| 2026-04-27 | Step 2 complete — portfolio_calculator.py, 9-step pipeline |
| 2026-04-27 | Step 3 complete — portfolio_agent.py, AI report agent |
| 2026-04-27 | Step 4 complete — Portfolio page + usePortfolio hook + 3 components + API service + route |
| 2026-04-27 | Step 5 complete — AddStockModal with ticker validation + add/edit modes |
| 2026-04-27 | Step 6 complete — PortfolioAnalysis 10 sections, AiReportPreview replaced |
| 2026-04-27 | Step 7 complete — Sidebar + BottomTabBar Portfolio menu added |
| 2026-04-27 | Step 8 complete — sync_service.py + sync router + syncApi.ts + Settings UI |
| 2026-04-27 | Phase 13 fully complete |

---
---

# Phase 13 — 포트폴리오 `✅ 완료`

> 보유 종목 관리 + 정량 분석 파이프라인 + AI 리포트 + 크로스 디바이스 동기화

**완료일**: 2026-04-27
**상태**: ✅ 완료
**선행 조건**: Phase 12 완료 (UI/UX 개선 + 모바일 최적화)
**디자인 레퍼런스**: `pre-requirement/image.png`, `pre-requirement/20260427_115228.png`
**기능 명세**: `pre-requirement/portfolio-design-spec.md`
**AI 분석 출력 예시**: `pre-requirement/portfolio-analysis-example.md`

---

## 개요

사용자가 보유 종목(티커, 수량, 평균단가)을 입력하면 현재가를 자동 조회하여 수익률을 계산하고, 9단계 정량 분석 파이프라인으로 포트폴리오 전체를 분석한다. 분석 결과는 AI가 자연어 리포트로 변환하여 리스크 경고 + 리밸런싱 제안을 제공한다. 데이터는 LocalStorage에 저장하며, 동기화 코드+PIN을 통해 크로스 디바이스 동기화를 지원한다.

**핵심 설계 원칙**: 정량 계산은 Python이 수행하고, AI는 계산된 숫자의 해석만 담당한다. AI에게 계산을 시키지 않는다.

---

## 완료 항목

| # | 모듈 | 상태 | 스킬 타입 | 예상 소요 |
|---|---|---|---|---|
| 1 | 백엔드 — 포트폴리오 데이터 모델 + CRUD API | ✅ | project-specific | 2시간 |
| 2 | 백엔드 — 정량 분석 파이프라인 (Step 2~7) | ✅ | project-specific | 3시간 |
| 3 | 백엔드 — AI 리포트 에이전트 (Step 8) | ✅ | project-specific | 2시간 |
| 4 | 프론트엔드 — 포트폴리오 메인 페이지 | ✅ | project-specific | 4시간 |
| 5 | 프론트엔드 — 종목 추가/수정 모달 | ✅ | project-specific | 2시간 |
| 6 | 프론트엔드 — AI 분석 결과 표시 (10개 섹션) | ✅ | project-specific | 3시간 |
| 7 | 프론트엔드 — 네비게이션 통합 | ✅ | project-specific | 30분 |
| 8 | 크로스 디바이스 동기화 | ✅ | project-specific | 3시간 |

**총 소요: ~17시간**

---

## Step 1: 백엔드 — 데이터 모델 + CRUD API

### 데이터 모델

```python
PortfolioHolding = {
    "id": str,              # UUID
    "ticker": str,          # "AAPL"
    "shares": int,          # 45
    "avg_cost": float,      # 142.30
    "currency": str,        # "USD"
    "purchase_date": str,   # "2025-03-15" (선택)
    "memo": str,            # 최대 100자 (선택)
    "created_at": str,      # ISO 8601
    "updated_at": str       # ISO 8601
}
```

### API 엔드포인트

| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | `/api/portfolio/holdings` | 종목 추가 |
| PUT | `/api/portfolio/holdings/{id}` | 종목 수정 |
| DELETE | `/api/portfolio/holdings/{id}` | 종목 삭제 |
| GET | `/api/portfolio/holdings` | 전체 보유 목록 + 현재가 조회 |
| POST | `/api/portfolio/analyze` | 9단계 분석 실행 |
| GET | `/api/portfolio/analyze/cache` | 캐시된 분석 결과 조회 |

### 저장 구조

- **기본**: 프론트엔드 LocalStorage에 holdings 배열 저장 (서버에 전송 안 함)
- **분석 요청 시**: 프론트엔드가 holdings를 POST body로 전송 → 서버는 저장하지 않고 분석만 수행 후 반환
- **서버에 사용자 데이터가 남지 않는 구조** (프라이버시 보장)

---

## Step 2: 백엔드 — 정량 분석 파이프라인

9단계, 순수 Python 수학 계산 — AI 호출 없음.

### 2-1. 현재가 + 메타데이터 수집
```
입력: holdings 배열
출력: 종목별 {현재가, 섹터, 국가, 시총, Beta, 재무지표, 1년 일간 수익률}
데이터 소스: quote.py (Finnhub → yfinance), fundamentals.py, yfinance 1년 OHLCV
벤치마크: yfinance ^GSPC (S&P500) 1년 일간 수익률
모든 종목 asyncio.gather로 병렬 수집
```

### 2-2. 평가금액 및 비중 계산
```
종목별:
  market_value = 현재가 * 수량
  cost_basis = 평균단가 * 수량
  pnl = market_value - cost_basis
  pnl_pct = pnl / cost_basis * 100
  weight = market_value / 전체 market_value * 100

포트폴리오 전체:
  total_market_value, total_cost_basis, total_pnl, total_pnl_pct
```

### 2-3. 집중도 분석
```
top_1_weight, top_3_weight, top_5_weight
sector_weights, country_weights
HHI = sum((weight_i / 100)^2)
effective_n = 1 / HHI
```

### 2-4. 가중평균 펀더멘털
```
weighted_per, weighted_pbr, weighted_roe, weighted_debt_ratio,
weighted_op_margin, weighted_dividend_yield
annual_dividend = sum(현재가_i * 배당수익률_i * 수량_i)
```

### 2-5. 성과 분석
```
contribution_i = pnl_i / total_cost_basis * 100
benchmark_return = S&P500 동일 기간 수익률
alpha = portfolio_return - benchmark_return
```

### 2-6. 위험 분석
```python
volatility = np.std(port_daily_returns) * sqrt(252)  # 연율화
portfolio_beta = cov(portfolio, benchmark) / var(benchmark)
mdd = min(drawdown series)
sharpe = mean(excess_returns) / std(excess_returns) * sqrt(252)
var_95_30d = percentile(daily_returns, 5) * sqrt(30) * total_value
correlation_matrix = np.corrcoef(returns_matrix)
liquidity_flag = "safe" | "caution" | "danger"
```

### 2-7. 스타일 분석
```
종목별:
  style = "growth" if PER > 25 or 매출성장률 > 15% else "value"
  cap = "large" (>$10B) | "mid" (>$2B) | "small"
  dividend = "dividend" if 수익률 > 1% else "non-dividend"
  cycle = "cyclical" | "defensive" (섹터 기반)

포트폴리오: growth_pct, value_pct, large_pct, mid_pct, small_pct, cyclical_pct, defensive_pct
```

### 2-8. 거시 노출도
```
high_per_weight = PER > 30인 종목 비중 합 (금리 민감도)
동일 매크로 베팅 감지: 상관계수 > 0.75 AND 같은 섹터 → 경고
```

### 2-9. 점수화 (0~100)
```
분산 점수 = hhi_score(40) + sector_score(30) + corr_score(30)
위험 점수 = vol(30) + beta(30) + mdd(20) + concentration(20) → rating = score/10
성과 점수 = return_score(40) + alpha_score(30) + sharpe_score(30)
퀄리티 점수 = roe(30) + debt(30) + margin(20) + liquidity(20)
```

---

## Step 3: 백엔드 — AI 리포트 에이전트

### 설계 원칙
- AI에게 계산을 시키지 않는다
- Step 2의 모든 결과를 JSON으로 전달
- 프롬프트에 판단 기준표 명시
- 제안은 반드시 근거 숫자 인용

### 판단 기준
```
HHI > 0.25: 집중 위험
단일 섹터 > 40%: 섹터 쏠림
상관계수 > 0.75 + 같은 섹터: 동일 베팅
Beta > 1.5: 고위험
MDD > -20%: 심리적 부담
Sharpe < 0.5: 위험 대비 수익 부족
유동성 flag "danger": 즉시 경고
```

### AI 출력 스키마

```json
{
  "summary": "포트폴리오 한 줄 요약",
  "concentration": { "level": "HIGH|MEDIUM|LOW", "hhi": 0.24, "detail": "..." },
  "risk_score": { "score": 7.4, "breakdown": "..." },
  "strengths": ["..."],
  "risks": ["..."],
  "rebalancing": [
    { "action": "NVDA 32.8% → 20%", "reason": "Beta 1.65, 가장 높은 변동성" }
  ],
  "rebalancing_comparison": {
    "before": { "tech_pct": 84.0, "defensive_pct": 0, "hhi": 0.24, "sharpe": 1.52 },
    "after": { "tech_pct": 55, "defensive_pct": 20, "hhi": 0.15, "sharpe": 1.35 }
  },
  "macro_warning": "...",
  "style_summary": "...",
  "disclaimer": "본 분석은 AI가 생성한 참고 자료이며, 투자 자문이 아닙니다."
}
```

### 구현 파일

| 위치 | 파일 | 역할 |
|---|---|---|
| Backend | `agents/portfolio_agent.py` | AI 리포트 에이전트 |
| Backend | `services/portfolio_calculator.py` | 9단계 정량 계산 모듈 |

---

## Step 4: 프론트엔드 — 포트폴리오 메인 페이지

### 레이아웃 (Portfolio.tsx)

```
+--------------------------------------------------+
| Portfolio                    새로고침  Export  +추가 |
+-------------------------+------------------------+
| 총 평가금액               | 매수 원금               |
| $41,732.65  Live         | $28,694.00             |
| 오늘 +$175.28  +45.44%   | 미실현 손익              |
| [미니 라인 차트]           | +$13,037.85 +45.4%     |
|                          | 최고: AAPL +91.88%     |
|                          | 최저: TSLA -8.28%      |
+-------------------------+------------------------+
| 배분 & 성과                    All 1M 3M YTD 1Y    |
+-----------------------+--------------------------+
| 포지션 비중             | 포지션별 수익률            |
| [도넛 차트]             | [가로 바 차트]             |
+-----------------------+--------------------------+
| 보유 종목 (5)               정렬: 수익률 금액 종목명  |
| [종목 카드 리스트]                                   |
+--------------------------------------------------+
| AI 포트폴리오: 리스크 & 배분 리뷰                      |
| [Step 6 영역]                                      |
+--------------------------------------------------+
```

### 모바일 대응
- 요약 카드: 세로 스택
- 도넛 + 바 차트: 세로 스택
- 종목 카드: 압축 레이아웃 (1줄: 티커+수익률, 2줄: 수량+현재가, 3줄: 수익금액)

### 데이터 흐름
```
LocalStorage (holdings)
  → usePortfolio() 커스텀 훅
    → GET /api/portfolio/holdings (현재가 조회)
    → 60초마다 자동 갱신
    → 화면 렌더링
```

### 빈 상태
종목 0개: "아직 추가된 종목이 없습니다. 첫 종목을 추가해보세요." + [+ Add Stock] 버튼

---

## Step 5: 프론트엔드 — 종목 추가/수정 모달

### 필드

| 필드 | 필수 | 타입 | 검증 |
|---|---|---|---|
| 종목 코드 | O | 텍스트 + 자동완성 | 유효한 티커인지 API 확인 |
| 보유 수량 | O | 정수 | > 0 |
| 평균 매수가 | O | 소수점 2자리 | > 0 |
| 통화 | O | 드롭다운 (USD 기본) | — |
| 매수일 | X | 날짜 선택 | 오늘 이전 |
| 메모 | X | 텍스트 | 최대 100자 |

### 동작
- 추가 모드: 모든 필드 편집 가능, "Save" 버튼
- 수정 모드: 종목 코드 잠금(읽기 전용), "Update" 버튼
- 필수 3개 미입력 시 저장 버튼 비활성화
- 저장 시 LocalStorage에 즉시 반영

---

## Step 6: 프론트엔드 — AI 분석 결과 표시 (10개 섹션)

분석 완료 후 순서대로 렌더링:
1. 헤더 (마지막 분석 시각 + Re-analyze)
2. 핵심 지표 3개 (Concentration, Risk Score, Sharpe)
3. 4대 점수 (분산/위험/성과/퀄리티, 산출 근거 포함)
4. 집중도 상세 (종목/섹터 집중도, 동일 베팅 경고)
5. 성과 (벤치마크 비교, 수익 기여도)
6. 위험 (변동성/Beta/MDD/VaR, 상관관계 행렬, 유동성)
7. 스타일 (성장/가치, 대형/소형, 배당, 경기민감도)
8. 거시 노출도 (금리 민감도, 동일 매크로 베팅 감지)
9. 펀더멘털 (가중평균 PER/PBR/ROE 등)
10. AI 종합 리포트 (요약/강점/리스크/리밸런싱 제안 + 전후 비교표)

### 트리거
- [Analyze My Portfolio] 버튼 (종목 2개 이상일 때 활성화)
- 로딩: 스켈레톤 + "AI가 포트폴리오를 분석하고 있습니다..."
- 면책 조항 하단 항상 표시

---

## Step 7: 프론트엔드 — 네비게이션 통합

### PC 사이드바
```
Market Overview
Quick Look
Compare Mode
Portfolio        <-- 신규 추가
Sector Screening
Beginner's Guide
```

### 모바일 바텀 탭
```
Home — Analysis — Portfolio — Sector — Settings
                   <-- 신규 추가 (briefcase 아이콘)
```
4탭 → 5탭 변경. `BottomTabBar.tsx`의 TABS 배열에 추가.

---

## Step 8: 크로스 디바이스 동기화

### 동작 방식
- **동기화 코드**: 12자리 랜덤 코드 (예: ABCD-1234-EFGH)
- **PIN**: 4자리 숫자
- 회원가입/로그인 없음
- 코드+PIN 없이는 서버 데이터 접근 불가

### API 엔드포인트

| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | `/api/sync/create` | 새 동기화 코드 생성 (PIN 설정) |
| POST | `/api/sync/connect` | 기존 코드로 연결 (코드+PIN 검증) |
| POST | `/api/sync/push` | 내 데이터 → 서버 업로드 |
| GET | `/api/sync/pull` | 서버 → 내 데이터 다운로드 |
| DELETE | `/api/sync/disconnect` | 동기화 해제 + 서버 데이터 삭제 |

### 보안
- PIN은 bcrypt 해시로 저장
- 3회 연속 실패 시 30초 대기
- 90일간 미접속 시 서버 데이터 자동 삭제
- 충돌 해결: last-write-wins (타임스탬프 기준)

### Settings 페이지 추가 영역
- 동기화 미설정 시: [Create Sync Code] / [Enter Existing Code] 버튼
- 동기화 설정 후: 코드 표시 + 마지막 동기화 시각 + [Sync Now] + [Disconnect]

---

## 구현 순서 및 의존 관계

```
Step 1 (CRUD API)
  |
Step 2 (정량 분석) <-- 핵심, 가장 시간 소요
  |
Step 3 (AI 리포트) <-- Step 2 결과 필요
  |
Step 4 (메인 페이지) + Step 5 (모달) <-- 병렬 가능
  |
Step 6 (AI 표시) <-- Step 3 + Step 4 필요
  |
Step 7 (네비게이션) <-- Step 4 필요
  |
Step 8 (동기화) <-- 독립적, 마지막에 추가
```

---

## 구현 파일

### 신규 파일

| 위치 | 파일 | 역할 |
|---|---|---|
| Backend | `backend/routers/portfolio.py` | 포트폴리오 CRUD + 분석 API |
| Backend | `services/portfolio_calculator.py` | 정량 계산 모듈 |
| Backend | `agents/portfolio_agent.py` | AI 리포트 에이전트 |
| Backend | `backend/routers/sync.py` | 동기화 API |
| Backend | `services/sync_service.py` | 동기화 로직 + PIN 해시 |
| Frontend | `pages/Portfolio.tsx` | 포트폴리오 메인 페이지 |
| Frontend | `components/AddStockModal.tsx` | 종목 추가/수정 모달 |
| Frontend | `components/PortfolioAIReport.tsx` | AI 분석 결과 표시 |
| Frontend | `components/PortfolioCharts.tsx` | 도넛 + 바 차트 |
| Frontend | `components/HoldingCard.tsx` | 개별 종목 카드 |
| Frontend | `hooks/usePortfolio.ts` | 포트폴리오 상태 관리 훅 |
| Frontend | `services/portfolioApi.ts` | API 호출 함수 |

### 수정 파일

| 파일 | 변경 내용 |
|---|---|
| `frontend/src/App.tsx` | Portfolio 라우트 추가 |
| `frontend/src/components/Sidebar.tsx` | Portfolio 메뉴 항목 추가 |
| `frontend/src/components/BottomTabBar.tsx` | Portfolio 탭 추가 (4탭→5탭) |
| `frontend/src/pages/Settings.tsx` | PORTFOLIO SYNC 섹션 추가 |
| `backend/main.py` | portfolio, sync 라우터 등록 |

---

## 설계 결정 사항

| 결정 | 선택 | 이유 |
|---|---|---|
| 데이터 저장 | LocalStorage (기본) + 서버 동기화 (선택) | 프라이버시 보장, 서버에 사용자 데이터 미저장 |
| 정량/정성 분리 | Python 계산 + AI 해석 | AI 환각 방지, 숫자 정밀도 보장 |
| 벤치마크 | S&P 500 (^GSPC) | 미국 주식 포트폴리오 기준 |
| 차트 라이브러리 | lightweight-charts (기존) + 자체 SVG | 외부 의존성 추가 불필요 |
| 동기화 인증 | 코드+PIN (무로그인) | 개인 프로젝트에 OAuth 과잉, 심플한 보안 |
| 충돌 해결 | last-write-wins | 1인 사용 기준, CRDT 불필요 |

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-27 | Phase 13 문서 신규 생성 |
| 2026-04-27 | AI 분석 결과 상세 예시를 portfolio-analysis-example.md로 분리 |
| 2026-04-27 | 스트레스 테스트 제거, 총 소요 20h → 17h |
| 2026-04-27 | Step 2 완료 — portfolio_calculator.py, 9단계 정량 분석 파이프라인 |
| 2026-04-27 | Step 3 완료 — portfolio_agent.py, AI 리포트 에이전트 |
| 2026-04-27 | Step 4 완료 — Portfolio 메인 페이지 + usePortfolio 훅 + 컴포넌트 3종 + API 서비스 + 라우트 등록 |
| 2026-04-27 | Step 5 완료 — AddStockModal 생성, 티커 검증(디바운스) + 추가/수정 모드 |
| 2026-04-27 | Step 6 완료 — PortfolioAnalysis 10개 섹션 구현 |
| 2026-04-27 | Step 7 완료 — Sidebar + BottomTabBar에 Portfolio 메뉴 추가 |
| 2026-04-27 | Step 8 완료 — sync_service.py + sync 라우터 + syncApi.ts + Settings UI |
| 2026-04-27 | Phase 13 전체 완료 |
