# Phase 8 — Quick Look + AI 분석 결과 화면 `✅ 완료`

> 가장 자주 사용되는 두 핵심 화면을 React 컴포넌트로 구현

**상태**: ✅ 완료
**선행 조건**: Phase 7 완료 (React 뼈대 + 디자인 시스템 + 사이드바 동작)
**디자인 권위 문서**: `pre-requirement/design-spec.md` 6장

---

## 개요

Quick Look 화면(시세 헤더, KPI 카드, 캔들스틱 차트, 기술 지표 카드, AI Recommendation)과 AI 분석 결과 화면(Agent 진행 상태, BUY/HOLD/SELL 판정, Bull/Bear Case)을 React로 구현한다. 이 Phase가 끝나면 **앱의 핵심 기능이 동작**한다.

---

## 완료 예정 / 완료 항목

| # | 모듈 | 상태 | 설명 |
|---|---|---|---|
| 1 | `pages/QuickLook.tsx` | ✅ | Quick Look 전체 화면 |
| 2 | `components/PriceHeader.tsx` | ✅ | 시세 헤더 (가격+등락+52W Range) |
| 3 | `components/KpiCard.tsx` | ✅ | KPI 카드 (Market Cap, PE, EPS, Forward PE) |
| 4 | `components/Chart.tsx` | ✅ | 캔들스틱 + MA + 볼륨 차트 |
| 5 | `components/TechCard.tsx` | ✅ | RSI / MACD / Bollinger 카드 |
| 6 | `components/AiRecommendation.tsx` | ✅ | AI Recommendation 카드 |
| 7 | `components/Tooltip.tsx` | ✅ | 인라인 툴팁 |
| 8 | `components/SignalBadge.tsx` | ✅ | bullish/bearish/neutral 뱃지 |
| 9 | `pages/AIAnalysis.tsx` | ✅ | AI 분석 결과 화면 |
| 10 | `components/LoadingSkeleton.tsx` | ✅ | 로딩 스켈레톤 UI |
| 11 | `components/ErrorBanner.tsx` | ✅ | 에러 배너 컴포넌트 |
| 12 | `hooks/useQuote.ts` | ✅ | 시세 데이터 hook |
| 13 | `hooks/useAnalysis.ts` | ✅ | AI 분석 hook |

---

## Quick Look 화면 — 레이아웃

```
┌──────────────────────────────────────────────────────────────┐
│  EQUITIES › TECHNOLOGY › SEMICONDUCTORS           Breadcrumb │
│                                                              │
│  [NVDA] [NASDAQ]  NVIDIA Corp                                │
│  $142.50  +2.3% (+$3.21)     52W: $40━●━$145  VOL: 342.1M   │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │MARKET CAP│ │P/E RATIO │ │   EPS    │ │FORWARD PE│        │
│  │ $3.52T   │ │  35.24   │ │  $4.05   │ │  28.12   │  KPI   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
├──────────────────────────────────────┬───────────────────────┤
│  [1D] [1W] [1M] [3M] [6M] [1Y] [5Y]│  ┌─RSI (14)────────┐  │
│                                      │  │ 62.4 NEUTRAL-BULL│  │
│  ┌──────────────────────────────┐    │  └─────────────────┘  │
│  │                              │    │  ┌─MACD────────────┐  │
│  │      캔들스틱 차트 + MA       │    │  │ Positive ▂▄▆█   │  │
│  │                              │    │  └─────────────────┘  │
│  ├──────────────────────────────┤    │  ┌─BOLLINGER───────┐  │
│  │  VOLUME  ▂▄█▂▄▆             │    │  │ U: 148.12       │  │
│  └──────────────────────────────┘    │  │ M: 141.05       │  │
│                                      │  │ L: 133.98       │  │
│                                      │  └─────────────────┘  │
├──────────────────────────────────────┴───────────────────────┤
│  🧠 AI Recommendation  [BUY]        CONFIDENCE: high        │
│  NVDA is showing strong structural support at $140...        │
│                          [▶ AI 분석 실행]                     │
└──────────────────────────────────────────────────────────────┘
```

---

## 컴포넌트별 상세

### PriceHeader.tsx — 시세 헤더

| UI 요소 | API | 필드 |
|---------|-----|------|
| Breadcrumb | `/api/fundamentals/{ticker}` | sector, industry |
| 티커 배지 | URL 파라미터 | ticker |
| 회사명 | `/api/fundamentals/{ticker}` | (yfinance info.shortName) |
| 가격 + 등락 | `/api/quote/{ticker}` | price, change, change_percent |
| 52W Range | `/api/fundamentals/{ticker}` | week52_high, week52_low |
| Volume | `/api/quote/{ticker}` | volume |

52W Range 슬라이더 위치 계산:
```typescript
const position = (price - week52_low) / (week52_high - week52_low) * 100
// → CSS width: `${position}%`
```

### KpiCard.tsx — KPI 카드 4개

| 카드 | 라벨 | 데이터 필드 |
|------|------|-----------|
| 1 | MARKET CAP | `fundamentals.market_cap` |
| 2 | P/E RATIO (TTM) | `fundamentals.pe` |
| 3 | EPS (DILUTED) | `fundamentals.eps` |
| 4 | FORWARD P/E | `fundamentals.forward_pe` |

- 라벨: text_secondary, xs, UPPERCASE
- 값: 2xl, monospace(JetBrains Mono), 굵게
- 카드: bg_card, 1px border, radius 8px

### Chart.tsx — 캔들스틱 차트 (가장 복잡한 컴포넌트)

**사용 라이브러리 선택지:**
| 라이브러리 | 장점 | 단점 |
|-----------|------|------|
| **Plotly React** | 기존 Plotly 설정 재사용 | 번들 크기 큼 |
| **Lightweight Charts** | TradingView 품질, 가벼움 | 캔들+볼륨 별도 처리 |
| **Recharts** | React 친화적 | 캔들스틱 지원 약함 |

**추천: Lightweight Charts** (TradingView 오픈소스)

| 기능 | 설명 |
|------|------|
| 기간 선택 | 1D/1W/1M/3M/6M/1Y/5Y 탭 — API: `/api/history/{ticker}?period=1M` |
| 캔들스틱 | 상승=up, 하락=down 색상 |
| MA50 라인 | accent 색상 |
| MA200 라인 | warning 색상 |
| 볼륨 바 | 캔들 색 매칭, 차트 하단 |
| 현재가 라벨 | 오른쪽 끝 accent 배경 |
| 테마 연동 | Dark/Light 자동 전환 (design-spec.md 10장) |

### TechCard.tsx — 기술 지표 카드 3개

API: `/api/technicals/{ticker}`

**RSI (14)**
```
상태 점 (●) + 값 (62.4) + 신호 텍스트 (NEUTRAL-BULL) + 게이지 바
게이지 바: width = rsi.value + "%" (0~100)
상태 점 색상: bullish=up, bearish=down, neutral=text_muted
```

**MACD**
```
상태 점 (●) + "HISTOGRAM" 라벨 + Positive/Negative + 미니 바
histogram > 0: "Positive" (up 색상)
histogram < 0: "Negative" (down 색상)
```

**BOLLINGER BANDS**
```
상태 점 (●) + Upper/Middle/Lower 3행
현재가에 가장 가까운 값 → accent로 강조
```

### AiRecommendation.tsx — AI Recommendation 카드

| 요소 | 값 | 스타일 |
|------|-----|-------|
| 아이콘 | 🧠 | accent 원형 배경 |
| 판정 배지 | BUY / HOLD / SELL | up / warning / down |
| 요약 텍스트 | `summary` | text_primary, md |
| Confidence | high / medium / low | accent / warning / text_muted |
| 분석 실행 버튼 | "AI 분석 실행" | accent 그라데이션, 전체 폭 |

---

## AI 분석 결과 화면 (AIAnalysis.tsx)

### 레이아웃

```
┌──────────────────────────────────────┐
│  Agent 진행 상태                      │
│  ● News Agent         ✓ 완료         │
│  ● Data Agent         ✓ 완료         │
│  ● Macro Agent        ⟳ 진행 중      │
│  ○ Cross-validation   — 대기         │
│  ○ Analyst Agent      — 대기         │
├──────────────────────────────────────┤
│  [BUY]  Confidence: high             │
│  Score: 82/100                       │
├──────────────────────────────────────┤
│  Bull Case          │  Bear Case     │
│  (up 카드)          │  (down 카드)   │
├──────────────────────────────────────┤
│  Catalyst (warning 카드)             │
├──────────────────────────────────────┤
│  Action Summary (accent 카드)        │
├──────────────────────────────────────┤
│  면책 조항                            │
└──────────────────────────────────────┘
```

### API 연동

```typescript
// POST /api/analysis/{ticker}
const { data, loading } = useAnalysis(ticker)

// loading 중: AgentProgress 컴포넌트 표시
// 완료 후: VerdictCard + Bull/Bear + Catalyst + Action Summary 표시
```

---

## 데이터 Hook

### useQuote.ts
```typescript
function useQuote(ticker: string) {
  // 병렬 호출: quote + fundamentals + technicals
  // 반환: { quote, fundamentals, technicals, loading, error }
}
```

### useAnalysis.ts
```typescript
function useAnalysis(ticker: string) {
  // POST /api/analysis/{ticker}
  // 반환: { result, loading, error, trigger }
  // trigger(): 수동 실행 (버튼 클릭 시)
}
```

---

## 선행 조건 및 의존성

- Phase 7: React 뼈대 + 사이드바 + 라우팅 동작
- Phase 6: FastAPI 엔드포인트 (`/api/quote/*`, `/api/history/*`, `/api/technicals/*`, `/api/analysis/*`)
- npm: 차트 라이브러리 (lightweight-charts 또는 plotly.js)

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
| 2026-04-14 | ✅ 구현 완료 — QuickLook + AIAnalysis 페이지 + 10개 컴포넌트 + 2개 hook |
| 2026-04-15 | AgentProgress/VerdictCard → LoadingSkeleton/ErrorBanner로 설계 변경 반영 |
