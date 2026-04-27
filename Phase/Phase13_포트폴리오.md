# Phase 13 — 포트폴리오 기능 `✅ 완료`

> 보유 종목 관리 + 정량 분석 파이프라인 + AI 리포트 + 크로스 디바이스 동기화

**상태**: ✅ 완료
**선행 조건**: Phase 12 완료 (UI/UX 개선 + 모바일 최적화)
**디자인 레퍼런스**: `pre-requirement/image.png`, `pre-requirement/20260427_115228.png`
**기능 명세**: `pre-requirement/portfolio-design-spec.md`
**AI 분석 출력 예시**: `pre-requirement/portfolio-analysis-example.md`

---

## 개요

사용자가 보유 종목(티커, 수량, 평균단가)을 입력하면 현재가를 자동 조회하여 수익률을 계산하고, 정량 분석 파이프라인으로 포트폴리오 전체를 분석한다. 분석 결과는 AI가 자연어 리포트로 변환하여 리스크 경고 + 리밸런싱 제안을 제공한다. 데이터는 LocalStorage에 저장하며, 동기화 코드+PIN을 통해 크로스 디바이스 동기화를 지원한다.

**핵심 설계 원칙**: 정량 계산은 Python이 수행하고, AI는 계산된 숫자의 해석만 담당한다. AI에게 계산을 시키지 않는다.

---

## 완료 예정 항목

| # | 항목 | 상태 | 난이도 | 예상 소요 |
|---|---|---|---|---|
| 1 | 백엔드 — 포트폴리오 데이터 모델 + CRUD API | ✅ | 중 | 2시간 |
| 2 | 백엔드 — 정량 분석 파이프라인 (Step 2~7) | ✅ | 상 | 3시간 |
| 3 | 백엔드 — AI 리포트 에이전트 (Step 8) | ✅ | 중 | 2시간 |
| 4 | 프론트엔드 — 포트폴리오 메인 페이지 | ✅ | 상 | 4시간 |
| 5 | 프론트엔드 — 종목 추가/수정 모달 | ✅ | 중 | 2시간 |
| 6 | 프론트엔드 — AI 분석 결과 표시 영역 | ✅ | 중 | 3시간 |
| 7 | 프론트엔드 — 네비게이션 통합 | ✅ | 하 | 30분 |
| 8 | 크로스 디바이스 동기화 | ✅ | 상 | 3시간 |

**총 예상 소요: ~17시간**

---

## Step 1: 백엔드 — 포트폴리오 데이터 모델 + CRUD API

### 데이터 모델

```python
# 사용자 입력 데이터
PortfolioHolding = {
    "id": str,              # UUID
    "ticker": str,          # "AAPL"
    "shares": int,          # 45
    "avg_cost": float,      # 142.30
    "currency": str,        # "USD"
    "purchase_date": str,   # "2025-03-15" (선택)
    "memo": str,            # "실적 발표 전 매수" (선택, 100자)
    "created_at": str,      # ISO 8601
    "updated_at": str       # ISO 8601
}
```

### API 엔드포인트

| Method | Path | 설명 |
|---|---|---|
| POST | `/api/portfolio/holdings` | 종목 추가 |
| PUT | `/api/portfolio/holdings/{id}` | 종목 수정 |
| DELETE | `/api/portfolio/holdings/{id}` | 종목 삭제 |
| GET | `/api/portfolio/holdings` | 전체 보유 목록 + 현재가 조회 |
| POST | `/api/portfolio/analyze` | 9단계 분석 실행 |
| GET | `/api/portfolio/analyze/cache` | 캐시된 분석 결과 조회 |

### 저장 구조

- **기본**: 프론트엔드 LocalStorage에 holdings 배열 저장 (서버 전송 안 함)
- **분석 요청 시**: 프론트엔드가 holdings 배열을 POST body로 전송 → 서버는 저장하지 않고 분석만 수행 후 반환
- **서버에 사용자 데이터가 남지 않는 구조** (프라이버시 보장)

---

## Step 2: 백엔드 — 정량 분석 파이프라인

분석 요청이 들어오면 아래 순서로 Python이 계산한다. **AI 호출 없이 순수 수학 계산만 수행**.

### 2-1. 현재가 + 메타데이터 수집

```
입력: holdings 배열
출력: 종목별 {현재가, 섹터, 국가, 시총, Beta, 재무지표, 1년 일간 수익률}

데이터 소스:
- 현재가: quote.py (Finnhub → yfinance fallback)
- 메타: fundamentals.py (yfinance → FMP → Finviz fallback)
- 히스토리: yfinance 1년 일간 OHLCV
- 벤치마크: yfinance ^GSPC (S&P500) 1년 일간 수익률
```

모든 종목 데이터를 **asyncio.gather**로 병렬 수집한다.

### 2-2. 평가금액 및 비중 계산

```
종목별:
  market_value = 현재가 × 수량
  cost_basis = 평균단가 × 수량
  pnl = market_value - cost_basis
  pnl_pct = pnl / cost_basis × 100
  weight = market_value / 전체 market_value × 100

포트폴리오 전체:
  total_market_value = Σ market_value
  total_cost_basis = Σ cost_basis
  total_pnl = total_market_value - total_cost_basis
  total_pnl_pct = total_pnl / total_cost_basis × 100
```

### 2-3. 집중도 분석

```
top_1_weight = 최대 비중 종목의 %
top_3_weight = 상위 3개 합산 %
top_5_weight = 상위 5개 합산 %

sector_weights = {섹터: 해당 섹터 종목 비중 합}
country_weights = {국가: 해당 국가 종목 비중 합}

HHI = Σ (weight_i / 100)^2    # 0~1, 높을수록 집중
effective_n = 1 / HHI          # 유효 종목 수
```

### 2-4. 포트폴리오 가중평균 펀더멘털

```
weighted_per = Σ (PER_i × weight_i) / 100
weighted_pbr = Σ (PBR_i × weight_i) / 100
weighted_roe = Σ (ROE_i × weight_i) / 100
weighted_debt_ratio = Σ (부채비율_i × weight_i) / 100
weighted_op_margin = Σ (영업이익률_i × weight_i) / 100
weighted_dividend_yield = Σ (배당수익률_i × weight_i) / 100
annual_dividend = Σ (현재가_i × 배당수익률_i × 수량_i)
```

### 2-5. 성과 분석

```
종목별 수익률: pnl_pct (2-2에서 계산 완료)

수익 기여도:
  contribution_i = pnl_i / total_cost_basis × 100
  # "AAPL이 전체 수익의 45% 기여"

벤치마크 대비 (S&P500):
  portfolio_return = total_pnl_pct
  benchmark_return = S&P500 동일 기간 수익률
  alpha = portfolio_return - benchmark_return

  # 벤치마크 기간: 가장 오래된 매수일 ~ 오늘
  # 매수일 미입력 시: holdings 생성일 기준
```

### 2-6. 위험 분석

```python
import numpy as np

# 1년 일간 수익률 행렬 (종목 × 일수)
returns_matrix = [종목별 일간 수익률]

# 포트폴리오 일간 수익률 (비중 가중합)
port_daily_returns = Σ (weight_i × daily_return_i)

# 변동성 (연율화)
volatility = np.std(port_daily_returns) × √252

# 포트폴리오 Beta
benchmark_returns = S&P500 일간 수익률
cov = np.cov(port_daily_returns, benchmark_returns)[0][1]
var_benchmark = np.var(benchmark_returns)
portfolio_beta = cov / var_benchmark

# 최대낙폭 (MDD)
cumulative = np.cumprod(1 + port_daily_returns)
running_max = np.maximum.accumulate(cumulative)
drawdown = (cumulative - running_max) / running_max
mdd = np.min(drawdown)

# 샤프 비율
risk_free_rate = FRED 3개월 T-bill / 252  # 일간 무위험이자율
excess_returns = port_daily_returns - risk_free_rate
sharpe = np.mean(excess_returns) / np.std(excess_returns) × √252

# VaR (95%, 30일)
var_95_daily = np.percentile(port_daily_returns, 5)
var_95_30d = var_95_daily × √30 × total_market_value

# 상관관계 행렬
correlation_matrix = np.corrcoef(returns_matrix)

# 유동성 리스크
for holding in holdings:
    avg_volume = 20일 평균 거래량
    holding_value_ratio = market_value / (avg_volume × 현재가)
    # ratio > 0.1이면 유동성 주의, > 0.5면 위험
    liquidity_flag = "safe" | "caution" | "danger"
    cap_tier = "large" if 시총 > 10B else "mid" if 시총 > 2B else "small"
```

### 2-7. 스타일 분석

```
종목별 분류:
  style = "growth" if PER > 25 or 매출성장률 > 15% else "value"
  cap = "large" if 시총 > $10B else "mid" if 시총 > $2B else "small"
  dividend = "dividend" if 배당수익률 > 1% else "non-dividend"
  cycle = "cyclical" if 섹터 in [Technology, Consumer Discretionary, Financials, Materials, Energy]
           else "defensive"

포트폴리오 레벨:
  growth_pct = growth 종목 비중 합
  value_pct = value 종목 비중 합
  large_pct / mid_pct / small_pct
  dividend_pct / non_dividend_pct
  cyclical_pct / defensive_pct
```

### 2-8. 거시 노출도

```
데이터 소스: FRED (이미 fred_client.py 존재)

금리 민감도:
  high_per_weight = PER > 30인 종목 비중 합
  # 높을수록 금리 인상에 취약

동일 매크로 베팅 감지:
  for pair in 종목 조합:
    if 상관계수 > 0.75 and 같은 섹터:
      flag("동일 베팅 경고: {종목A}와 {종목B}는 사실상 같은 포지션")
```

### 2-9. 점수화 (0~100)

```
분산 점수 (Diversification Score):
  hhi_score = (1 - HHI) × 40          # HHI 낮을수록 좋음 (0~40)
  sector_score = (섹터 수 / 11) × 30   # GICS 11개 섹터 기준 (0~30)
  corr_score = (1 - 평균상관계수) × 30  # 낮을수록 좋음 (0~30)
  → diversification = hhi_score + sector_score + corr_score

위험 점수 (Risk Score, 낮을수록 안전):
  vol_component = min(volatility / 0.4, 1) × 30       # 변동성 40% 이상이면 만점
  beta_component = min(portfolio_beta / 2.0, 1) × 30   # Beta 2.0 이상이면 만점
  mdd_component = min(abs(mdd) / 0.3, 1) × 20         # MDD 30% 이상이면 만점
  concentration = min(HHI / 0.5, 1) × 20               # HHI 0.5 이상이면 만점
  → risk_score = vol + beta + mdd + concentration
  → risk_rating = risk_score / 10  # 디자인의 "7.4/10" 형태

성과 점수 (Performance Score):
  return_score = 수익률 구간 매핑 (0~40)
  alpha_score = alpha 구간 매핑 (0~30)
  sharpe_score = sharpe 구간 매핑 (0~30)
  → performance = return_score + alpha_score + sharpe_score

퀄리티 점수 (Quality Score):
  roe_score = weighted_roe 구간 매핑 (0~30)
  debt_score = (1 - min(weighted_debt_ratio/2, 1)) × 30
  margin_score = weighted_op_margin 구간 매핑 (0~20)
  liquidity_score = 유동성 위험 없는 종목 비중 (0~20)
  → quality = roe + debt + margin + liquidity
```

---

## Step 3: 백엔드 — AI 리포트 에이전트

### 설계 원칙

- **AI에게 계산을 시키지 않는다**
- Step 2의 모든 계산 결과를 JSON으로 넘긴다
- 프롬프트에 판단 기준표를 명시한다
- 제안은 반드시 근거 숫자를 인용해야 한다

### 프롬프트 구조

```
[시스템 프롬프트]
너는 포트폴리오 분석 전문가다. 아래 규칙을 따라라:
1. 주어진 숫자를 재계산하지 마. 해석만 해.
2. 모든 제안에는 근거 숫자를 반드시 인용해.
3. 판단 기준:
   - HHI > 0.25: 집중 위험
   - 단일 섹터 > 40%: 섹터 쏠림
   - 상관계수 > 0.75 + 같은 섹터: 동일 베팅
   - Beta > 1.5: 고위험
   - MDD > -20%: 심리적 부담 가능성
   - Sharpe < 0.5: 위험 대비 수익 부족
   - 유동성 flag "danger": 즉시 경고
4. 리밸런싱 제안은 구체적으로 (어떤 종목을 몇% → 몇%).
5. 리밸런싱 적용 전/후 비교표 포함 (Tech비중, 방어섹터, HHI, Sharpe).
6. 한국어로 작성.

[사용자 메시지]
Step 2 계산 결과 전체를 섹션별로 전달 (요약/집중도/펀더멘털/성과/위험/스타일/거시/점수)
```

### AI 출력 스키마

```json
{
  "summary": "포트폴리오 전체 한 줄 요약",
  "concentration": {
    "level": "HIGH|MEDIUM|LOW",
    "hhi": 0.24,
    "detail": "상위 2종목이 62.2%, Tech 84%로 섹터 쏠림"
  },
  "risk_score": {
    "score": 7.4,
    "breakdown": "집중도 3.1/4 + Beta 2.1/3 + 변동성 2.2/3"
  },
  "strengths": [
    "S&P500 대비 +12.3%p 초과 수익 (Alpha)",
    "Sharpe 1.52로 위험 대비 효율적"
  ],
  "risks": [
    "Tech 섹터 84% — 금리 인상 시 동반 하락 가능",
    "AAPL-MSFT 상관계수 0.81 — 실질 분산 효과 약함"
  ],
  "rebalancing": [
    {"action": "NVDA 비중 32.8% → 20% 축소", "reason": "Beta 1.65로 가장 높은 변동성"},
    {"action": "Healthcare ETF(XLV) 10~15% 편입", "reason": "방어 섹터 비중 0%, 하락장 대응력 확보"},
    {"action": "TSLA 손절 또는 비중 동결", "reason": "-8.28% 손실 중, 유일한 마이너스 포지션"}
  ],
  "rebalancing_comparison": {
    "before": {"tech_pct": 84.0, "defensive_pct": 0, "hhi": 0.24, "sharpe": 1.52},
    "after": {"tech_pct": 55, "defensive_pct": 20, "hhi": 0.15, "sharpe": 1.35}
  },
  "macro_warning": "금리 민감 종목(PER>30) 비중 62% — 금리 인상기에 취약",
  "style_summary": "성장주 92%, 대형주 100%, 비배당 70% — 공격적 성장 포트폴리오",
  "disclaimer": "본 분석은 AI가 생성한 참고 자료이며, 투자 자문이 아닙니다."
}
```

### AI 출력 예시

구체적인 전체 화면 출력 예시는 아래 문서를 참조한다:

→ **`pre-requirement/portfolio-analysis-example.md`**

---

## Step 4: 프론트엔드 — 포트폴리오 메인 페이지

### 레이아웃 (`Portfolio.tsx`)

디자인 레퍼런스 `image.png` 구조를 따른다.

```
┌─────────────────────────────────────────────────┐
│ Portfolio                    ⟳ Export  + Add Stock│
├─────────────────────────────┬───────────────────┤
│ TOTAL MARKET VALUE          │ COST BASIS        │
│ $41,732.65  ● Live          │ $28,694.00        │
│ Today +$175.28  All +45.44% │ UNREALIZED P&L    │
│ [미니 라인 차트]              │ +$13,037.85 +45.4%│
│                             │ BEST: AAPL +91.88%│
│                             │ WORST: TSLA -8.28%│
├─────────────────────────────┴───────────────────┤
│ ALLOCATION & PERFORMANCE        All 1M 3M YTD 1Y│
├──────────────────────┬──────────────────────────┤
│ Position Weight      │ Return by Position        │
│ [도넛 차트]           │ [가로 바 차트]             │
│ 가운데: 5 positions   │ 수익=초록, 손실=빨강       │
├──────────────────────┴──────────────────────────┤
│ HOLDINGS (5)                Sort: Return Value Name│
│ [종목 카드 리스트]                                  │
├─────────────────────────────────────────────────┤
│ AI · PORTFOLIO: Risk & Allocation Review         │
│ [Step 6 영역]                                     │
└─────────────────────────────────────────────────┘
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

종목 0개일 때: "아직 추가된 종목이 없습니다. 첫 종목을 추가해보세요." + [+ Add Stock] 버튼

---

## Step 5: 프론트엔드 — 종목 추가/수정 모달

### 필드

| 필드 | 필수 | 타입 | 검증 |
|---|---|---|---|
| 종목 코드 | O | 텍스트 + 자동완성 | 유효한 티커인지 API 확인 |
| 보유 수량 | O | 정수 | > 0 |
| 평균 매수가 | O | 소수점 2자리 | > 0 |
| 통화 | O | 드롭다운 (USD 기본) | - |
| 매수일 | X | 날짜 선택 | 오늘 이전 |
| 메모 | X | 텍스트 | 최대 100자 |

### 동작

- 추가 모드: 모든 필드 편집 가능, 저장 버튼 "Save"
- 수정 모드: 종목 코드 잠금(읽기 전용), 저장 버튼 "Update"
- 필수 3개 미입력 시 저장 버튼 비활성화
- 저장 시 LocalStorage에 즉시 반영

---

## Step 6: 프론트엔드 — AI 분석 결과 표시 영역

디자인 레퍼런스 `20260427_115228.png` 하단 구조를 따른다.

### 분석 전

- [Analyze My Portfolio] 버튼 (종목 2개 이상일 때 활성화)
- 1개 이하: "2개 이상의 종목이 필요합니다" 안내

### 분석 중

- "AI가 포트폴리오를 분석하고 있습니다..." 로딩 + 스켈레톤

### 분석 완료

분석 결과의 구체적 표시 항목, 레이아웃, 숫자 예시는 아래 문서를 참조한다:

→ **`pre-requirement/portfolio-analysis-example.md`**

이 문서에 정의된 영역을 순서대로 렌더링한다:
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

### 면책 조항

하단에 항상 표시: "본 분석은 AI가 생성한 참고 자료이며, 투자 자문이 아닙니다."

---

## Step 7: 프론트엔드 — 네비게이션 통합

### PC 사이드바

```
Market Overview
Quick Look
Compare Mode
Portfolio        ← 신규 추가
Sector Screening
Beginner's Guide
```

### 모바일 바텀 탭

```
Home — Analysis — Portfolio — Sector — Settings
                  ← 신규 추가 (💼 아이콘)
```

기존 4탭 → 5탭 변경. BottomTabBar.tsx의 TABS 배열에 추가.

---

## Step 8: 크로스 디바이스 동기화

### 동작 방식

- **동기화 코드**: 12자리 랜덤 코드 (예: ABCD-1234-EFGH)
- **PIN**: 4자리 숫자
- 회원가입/로그인 없음
- 코드+PIN 없이는 서버 데이터 접근 불가

### API 엔드포인트

| Method | Path | 설명 |
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
  ↓
Step 2 (정량 분석) ← 핵심, 가장 시간 소요
  ↓
Step 3 (AI 리포트) ← Step 2 결과 필요
  ↓
Step 4 (메인 페이지) + Step 5 (모달) ← 병렬 가능
  ↓
Step 6 (AI 표시) ← Step 3 + Step 4 필요
  ↓
Step 7 (네비게이션) ← Step 4 필요
  ↓
Step 8 (동기화) ← 독립적, 마지막에 추가
```

---

## 관련 파일 (신규 생성 예정)

| 위치 | 파일 | 역할 |
|---|---|---|
| Backend | `routers/portfolio.py` | 포트폴리오 CRUD + 분석 API |
| Backend | `services/portfolio_calculator.py` | 정량 계산 모듈 |
| Backend | `agents/portfolio_agent.py` | AI 리포트 에이전트 |
| Backend | `routers/sync.py` | 동기화 API |
| Backend | `services/sync_service.py` | 동기화 로직 + PIN 해시 |
| Frontend | `pages/Portfolio.tsx` | 포트폴리오 메인 페이지 |
| Frontend | `components/AddStockModal.tsx` | 종목 추가/수정 모달 |
| Frontend | `components/PortfolioAIReport.tsx` | AI 분석 결과 표시 |
| Frontend | `components/PortfolioCharts.tsx` | 도넛 + 바 차트 |
| Frontend | `components/HoldingCard.tsx` | 개별 종목 카드 |
| Frontend | `hooks/usePortfolio.ts` | 포트폴리오 상태 관리 훅 |
| Frontend | `services/portfolioApi.ts` | API 호출 함수 |

---

## 기존 파일 수정 예정

| 파일 | 수정 내용 |
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
| 벤치마크 | S&P500 (^GSPC) | 미국 주식 포트폴리오 기준 |
| 차트 라이브러리 | lightweight-charts (기존) + 자체 SVG | 외부 의존성 추가 불필요 |
| 동기화 인증 | 코드+PIN (무로그인) | 개인 프로젝트에 OAuth 과잉, 심플한 보안 |
| 충돌 해결 | last-write-wins | 1인 사용 기준, CRDT 불필요 |

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-27 | Phase 13 문서 신규 생성 |
| 2026-04-27 | AI 분석 결과 상세 예시를 portfolio-analysis-example.md로 분리, Phase 문서에서 참조만 명시 |
| 2026-04-27 | 스트레스 테스트 제거, 총 소요 20h→17h |
| 2026-04-27 | Step 2 완료 — `services/portfolio_calculator.py` 생성, 9단계 정량 분석 파이프라인 구현, 라우터 연결 |
| 2026-04-27 | Step 3 완료 — `agents/portfolio_agent.py` 생성, AI 리포트 에이전트 구현, 라우터 연결 |
| 2026-04-27 | Step 4 완료 — Portfolio 메인 페이지 + usePortfolio 훅 + 컴포넌트 3종 + API 서비스 + 라우트 등록 |
| 2026-04-27 | Step 5 완료 — AddStockModal 생성, 티커 검증(디바운스) + 추가/수정 모드 + Portfolio.tsx 이벤트 연결 |
| 2026-04-27 | Step 6 완료 — PortfolioAnalysis 10개 섹션 구현, AiReportPreview 교체 |
| 2026-04-27 | Step 7 완료 — Sidebar + BottomTabBar에 Portfolio 메뉴 추가 |
| 2026-04-27 | Step 8 완료 — sync_service.py + sync 라우터 + syncApi.ts + Settings UI (코드+PIN 동기화) |
| 2026-04-27 | Phase 13 전체 완료 |
