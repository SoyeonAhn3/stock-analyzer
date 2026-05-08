# Phase 8 — QuickLook + AI Analysis UI `✅ Completed`

> Build the two most-used screens — QuickLook (quote + chart + indicators) and AI Analysis results — as React components

**Completed**: 2026-04-14
**Status**: ✅ Completed
**Prerequisites**: Phase 7 completed (React skeleton + design system + sidebar)
**Design Reference**: `pre-requirement/design-spec.md` Chapter 6

---

## Overview

Implement the QuickLook page (price header, KPI cards, candlestick chart, technical indicator cards, AI recommendation) and the AI Analysis results page (agent progress, BUY/HOLD/SELL verdict, bull/bear case). After this Phase, the **app's core features are functional**.

---

## Deliverables

| # | Module | Status | Type |
|---|---|---|---|
| 1 | `pages/QuickLook.tsx` | ✅ | project-specific |
| 2 | `components/PriceHeader.tsx` | ✅ | project-specific |
| 3 | `components/KpiCard.tsx` | ✅ | project-specific |
| 4 | `components/Chart.tsx` | ✅ | project-specific |
| 5 | `components/TechCard.tsx` | ✅ | project-specific |
| 6 | `components/AiRecommendation.tsx` | ✅ | project-specific |
| 7 | `components/Tooltip.tsx` | ✅ | general |
| 8 | `components/SignalBadge.tsx` | ✅ | general |
| 9 | `pages/AIAnalysis.tsx` | ✅ | project-specific |
| 10 | `components/LoadingSkeleton.tsx` | ✅ | general |
| 11 | `components/ErrorBanner.tsx` | ✅ | general |
| 12 | `hooks/useQuote.ts` | ✅ | project-specific |
| 13 | `hooks/useAnalysis.ts` | ✅ | project-specific |

---

## QuickLook Page Layout

```
┌──────────────────────────────────────────────────────────────┐
│  EQUITIES > TECHNOLOGY > SEMICONDUCTORS           Breadcrumb │
│  [NVDA] [NASDAQ]  NVIDIA Corp                                │
│  $142.50  +2.3% (+$3.21)     52W: $40━●━$145  VOL: 342.1M   │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │MARKET CAP│ │P/E RATIO │ │   EPS    │ │FORWARD PE│  KPI   │
│  │ $3.52T   │ │  35.24   │ │  $4.05   │ │  28.12   │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
├──────────────────────────────┬───────────────────────────────┤
│  [1D][1W][1M][3M][6M][1Y][5Y]│  RSI (14): 62.4 NEUTRAL-BULL │
│  ┌────────────────────────┐  │  MACD: Positive               │
│  │  Candlestick + MA      │  │  BOLLINGER: U/M/L             │
│  │  + Volume              │  │                               │
│  └────────────────────────┘  │                               │
├──────────────────────────────┴───────────────────────────────┤
│  AI Recommendation  [BUY]  CONFIDENCE: high                  │
│  "NVDA is showing strong structural support..."              │
│                          [AI 분석 실행]                        │
└──────────────────────────────────────────────────────────────┘
```

---

## Component Details

### PriceHeader.tsx

Displays breadcrumb (sector > industry), ticker badge, company name, price + change, 52W range slider, and volume. Data from `/api/quote/{ticker}` and `/api/fundamentals/{ticker}`.

### KpiCard.tsx

4 cards: Market Cap, P/E Ratio (TTM), EPS (Diluted), Forward P/E. Labels are uppercase xs text_secondary; values are 2xl monospace bold.

### Chart.tsx

**Library**: Lightweight Charts (TradingView open-source, ~40KB).

| Feature | Description |
|---------|-------------|
| Period selector | 1D / 1W / 1M / 3M / 6M / 1Y / 5Y tabs |
| Candlestick | Up/down color coding |
| MA50 line | Accent color |
| MA200 line | Warning color |
| Volume bars | Color-matched to candle, below chart |
| Current price label | Right edge, accent background |
| Theme sync | Dark/Light auto-switch |

### TechCard.tsx

3 cards from `/api/technicals/{ticker}`:
- **RSI (14)**: Gauge bar (0-100), status dot, signal text
- **MACD**: Histogram positive/negative, mini bar
- **Bollinger Bands**: Upper/Middle/Lower values, closest value highlighted

### AiRecommendation.tsx

Verdict badge (BUY/HOLD/SELL), summary text, confidence indicator, and "Run AI Analysis" button.

---

## AI Analysis Page (AIAnalysis.tsx)

```
┌──────────────────────────────────────┐
│  Agent Progress                       │
│  ● News Agent         ✓ Complete     │
│  ● Data Agent         ✓ Complete     │
│  ● Macro Agent        ⟳ Running     │
│  ○ Cross-validation   — Waiting     │
│  ○ Analyst Agent      — Waiting     │
├──────────────────────────────────────┤
│  [BUY]  Confidence: high             │
│  Score: 82/100                       │
├──────────────────────────────────────┤
│  Bull Case          │  Bear Case     │
├──────────────────────────────────────┤
│  Catalyst                            │
├──────────────────────────────────────┤
│  Action Summary                      │
├──────────────────────────────────────┤
│  Disclaimer                          │
└──────────────────────────────────────┘
```

---

## Data Hooks

### useQuote.ts

Parallel fetch of quote + fundamentals + technicals. Returns `{ quote, fundamentals, technicals, loading, error }`.

### useAnalysis.ts

POST to `/api/analysis/{ticker}`. Returns `{ result, loading, error, trigger }`. `trigger()` for manual execution via button click.

---

## Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Chart library | Lightweight Charts | TradingView quality, ~40KB bundle, free |
| KPI font | JetBrains Mono (monospace) | Financial data readability |
| Loading state | Skeleton UI (not spinner) | More natural feel per design-spec.md |
| Error display | Warning-colored banner (not red) | Less alarming UX |
| AI analysis duration | 1-2 minutes | Loading UX is critical — skeleton with progress |

---

## Prerequisites & Dependencies

- Phase 7: React skeleton + sidebar + routing
- Phase 6: FastAPI endpoints (`/api/quote/*`, `/api/history/*`, `/api/technicals/*`, `/api/analysis/*`)
- npm: `lightweight-charts`

---

## Development Notes

- Chart must sync colors on Dark/Light theme switch (design-spec.md chapter 10)
- All numbers use monospace font (JetBrains Mono)
- AI analysis takes 1-2 minutes — loading UX is important
- API failure shows warning-colored error banner (not red)
- Disclaimer appears at the bottom of every AI result card

---

## Change Log

| Date | Description |
|---|---|
| 2026-04-06 | Initial creation (Streamlit Quick Look + AI result UI) |
| 2026-04-14 | React migration — full rewrite as React components |
| 2026-04-14 | Implementation complete — QuickLook + AIAnalysis pages + 10 components + 2 hooks |
| 2026-04-15 | AgentProgress/VerdictCard replaced with LoadingSkeleton/ErrorBanner |

---
---

# Phase 8 — QuickLook + AI 분석 화면 `✅ 완료`

> 가장 자주 사용되는 두 핵심 화면(QuickLook, AI 분석 결과)을 React 컴포넌트로 구현

**완료일**: 2026-04-14
**상태**: ✅ 완료
**선행 조건**: Phase 7 완료 (React 뼈대 + 디자인 시스템 + 사이드바 동작)
**디자인 레퍼런스**: `pre-requirement/design-spec.md` 6장

---

## 개요

Quick Look 화면(시세 헤더, KPI 카드, 캔들스틱 차트, 기술 지표 카드, AI Recommendation)과 AI 분석 결과 화면(Agent 진행 상태, BUY/HOLD/SELL 판정, Bull/Bear Case)을 React로 구현한다. 이 Phase가 끝나면 **앱의 핵심 기능이 동작**한다.

---

## 완료 항목

| # | 모듈 | 상태 | 타입 |
|---|---|---|---|
| 1 | `pages/QuickLook.tsx` | ✅ | project-specific |
| 2 | `components/PriceHeader.tsx` | ✅ | project-specific |
| 3 | `components/KpiCard.tsx` | ✅ | project-specific |
| 4 | `components/Chart.tsx` | ✅ | project-specific |
| 5 | `components/TechCard.tsx` | ✅ | project-specific |
| 6 | `components/AiRecommendation.tsx` | ✅ | project-specific |
| 7 | `components/Tooltip.tsx` | ✅ | general |
| 8 | `components/SignalBadge.tsx` | ✅ | general |
| 9 | `pages/AIAnalysis.tsx` | ✅ | project-specific |
| 10 | `components/LoadingSkeleton.tsx` | ✅ | general |
| 11 | `components/ErrorBanner.tsx` | ✅ | general |
| 12 | `hooks/useQuote.ts` | ✅ | project-specific |
| 13 | `hooks/useAnalysis.ts` | ✅ | project-specific |

---

## QuickLook 페이지 레이아웃

브레드크럼(섹터 > 산업) → 시세 헤더(가격+등락+52W Range) → KPI 카드 4개(Market Cap, PE, EPS, Forward PE) → 캔들스틱 차트 + 기술 지표 카드 → AI Recommendation 카드.

---

## 컴포넌트별 상세

### PriceHeader.tsx

브레드크럼, 티커 배지, 회사명, 가격 + 등락, 52W Range 슬라이더, 거래량. `/api/quote/{ticker}` 및 `/api/fundamentals/{ticker}`에서 데이터.

### KpiCard.tsx

4개 카드: Market Cap, P/E Ratio (TTM), EPS (Diluted), Forward P/E. 라벨: uppercase xs text_secondary, 값: 2xl monospace 굵게.

### Chart.tsx

**라이브러리**: Lightweight Charts (TradingView 오픈소스, ~40KB).
기능: 7개 기간 선택, 캔들스틱 + MA50/MA200, 볼륨 바, 현재가 라벨, Dark/Light 테마 연동.

### TechCard.tsx

`/api/technicals/{ticker}`에서 데이터. RSI(14): 게이지 바, MACD: 히스토그램 양/음, Bollinger Bands: Upper/Middle/Lower.

### AiRecommendation.tsx

판정 배지(BUY/HOLD/SELL), 요약 텍스트, 신뢰도, "AI 분석 실행" 버튼.

---

## AI 분석 결과 화면 (AIAnalysis.tsx)

Agent 진행 상태 → 판정 카드(BUY/HOLD/SELL + 점수) → Bull/Bear Case → Catalyst → Action Summary → 면책 조항.

---

## 데이터 Hook

### useQuote.ts

quote + fundamentals + technicals 병렬 호출. `{ quote, fundamentals, technicals, loading, error }` 반환.

### useAnalysis.ts

`POST /api/analysis/{ticker}` 호출. `{ result, loading, error, trigger }` 반환. `trigger()`로 수동 실행.

---

## 설계 결정 사항

| 결정 | 선택 | 이유 |
|---|---|---|
| 차트 라이브러리 | Lightweight Charts | TradingView 품질, ~40KB 번들, 무료 |
| KPI 폰트 | JetBrains Mono (monospace) | 금융 데이터 가독성 |
| 로딩 상태 | 스켈레톤 UI (스피너 아님) | design-spec.md 권장, 자연스러운 UX |
| 에러 표시 | 주황(warning) 배너 (빨강 아님) | 덜 위협적인 UX |
| AI 분석 소요 시간 | 1~2분 | 로딩 UX 중요 — 스켈레톤 + 진행 상태 |

---

## 선행 조건 및 의존성

- Phase 7: React 뼈대 + 사이드바 + 라우팅
- Phase 6: FastAPI 엔드포인트 (`/api/quote/*`, `/api/history/*`, `/api/technicals/*`, `/api/analysis/*`)
- npm: `lightweight-charts`

---

## 개발 시 주의사항

- 차트는 Dark/Light 테마 전환 시 색상 연동 필수 (design-spec.md 10장)
- 모든 숫자는 monospace 폰트 (JetBrains Mono)
- AI 분석은 1~2분 소요 — 로딩 UX 중요
- API 실패 시 에러 배너 표시 (warning 색상, 빨강 아님)
- 면책 조항은 AI 결과가 있는 모든 카드 하단에 표시

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-06 | 최초 작성 (Streamlit Quick Look + AI 결과 UI) |
| 2026-04-14 | React 전환 — React 컴포넌트 기반으로 전면 재작성 |
| 2026-04-14 | 구현 완료 — QuickLook + AIAnalysis 페이지 + 10개 컴포넌트 + 2개 hook |
| 2026-04-15 | AgentProgress/VerdictCard → LoadingSkeleton/ErrorBanner로 설계 변경 반영 |
