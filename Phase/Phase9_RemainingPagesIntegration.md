# Phase 9 — Remaining Pages + Final Integration `✅ Completed`

> Market Overview, Sector Screening, Compare Mode, Beginner's Guide UI + disclaimer placement

**Completed**: 2026-04-14
**Status**: ✅ Completed
**Prerequisites**: Phase 8 completed (QuickLook + AI Analysis pages operational)
**Design Reference**: `pre-requirement/design-spec.md`

---

## Overview

Build the remaining 4 pages (Market Overview, Sector Screening, Compare Mode, Beginner's Guide), place disclaimers across all AI outputs, and handle loading/error states. After this Phase, the **MVP is complete**.

---

## Deliverables

| # | Module | Status | Type |
|---|---|---|---|
| 1 | `pages/MarketOverview.tsx` | ✅ | project-specific |
| 2 | `pages/SectorScreening.tsx` | ✅ | project-specific |
| 3 | `pages/CompareMode.tsx` | ✅ | project-specific |
| 4 | `pages/Guide.tsx` | ✅ | project-specific |
| 5 | `components/CompareChart.tsx` | ✅ | project-specific |
| 6 | MoverCard (inline) | ✅ | project-specific |
| 7 | NewsItem (inline) | ✅ | project-specific |
| 8 | CompareBar (inline) | ✅ | project-specific |
| 9 | CompareTable (inline) | ✅ | project-specific |
| 10 | GuideAccordion (inline) | ✅ | project-specific |
| 11 | `components/LoadingSkeleton.tsx` | ✅ | general |
| 12 | `components/ErrorBanner.tsx` | ✅ | general |

---

## Market Overview (Default Page)

```
┌────────────────────────┬──────────────────────────┐
│  TODAY'S MOVERS        │  MARKET NEWS              │
│                        │                          │
│  GAINERS               │  Fed holds rates steady   │
│  NVDA  +7.2%  $142.50  │  Reuters · 2h ago        │
│  AMD   +5.1%  $168.30  │                          │
│                        │  Apple reports record Q2  │
│  LOSERS                │  Bloomberg · 4h ago       │
│  META  -4.1%  $485.20  │                          │
└────────────────────────┴──────────────────────────┘
```

- **Gainers/Losers**: `GET /api/market/movers` — click navigates to `/quick-look/{ticker}`
- **News**: `GET /api/market/news` — headline click opens external URL
- Major indices shown in bottom TickerBar (no duplication)

---

## Sector Screening

```
┌───────────────────────────────────────────────────┐
│  GICS SECTORS                                      │
│  [Technology] [Healthcare] [Financials] [Energy]   │
│  [Consumer] [Industrial] [Materials] [Utilities]   │
│  ...                                               │
│  CUSTOM THEMES                                     │
│  [AI/반도체] [방산] [클린에너지] [+ New Theme]         │
├───────────────────────────────────────────────────┤
│  ⟳ Analyzing... Stage 2/2: AI Analysis             │
├───────────────────────────────────────────────────┤
│  TOP 5 RESULTS                                     │
│  1. ☐ NVDA  Score: 85  "AI demand explosive"       │
│  2. ☐ AMD   Score: 78  "Data center GPU share up"  │
│  [Compare Selected]    (active when 2+ checked)    │
└───────────────────────────────────────────────────┘
```

| Element | API |
|---------|-----|
| GICS sector buttons | Static (11 hardcoded) |
| Custom themes | `GET /api/themes` |
| Theme creation | `POST /api/themes` |
| Screening execution | `POST /api/sector/{name}` |
| Ticker click | → `/quick-look/{ticker}` |
| Compare Selected | → `/compare?tickers=NVDA,AMD` |

---

## Compare Mode

```
┌───────────────────────────────────────────────────┐
│  COMPARE                                           │
│  [NVDA ×] [AMD ×] [+ Add ticker]                   │
│  Comparison type: Same Sector (Technology)          │
├───────────────────────────────────────────────────┤
│  Comparison Table (price, PE, EPS, market_cap...)  │
├───────────────────────────────────────────────────┤
│  Normalized Return Chart (Base 100, 1Y)            │
├───────────────────────────────────────────────────┤
│  [Run AI Compare Analysis]                         │
├───────────────────────────────────────────────────┤
│  AI Compare Results                                │
│  (same_sector: category rankings + Key Risks)      │
│  (cross_sector: Sector Context + Macro Scenarios)  │
│  Disclaimer                                        │
└───────────────────────────────────────────────────┘
```

- **Data**: `POST /api/compare`
- **AI analysis**: `POST /api/compare/analyze`
- **CompareChart.tsx**: Normalized return comparison (Base 100), 1Y period

---

## Beginner's Guide

```
┌───────────────────────────────────────────────────┐
│  Beginner's Guide                                  │
│                                                    │
│  ▼ Chart Basics                                    │
│  │  [beginner] Candlestick Charts                  │
│  │  [beginner] Moving Averages                     │
│  │  [intermediate] Volume Analysis                 │
│                                                    │
│  ▶ Key Metrics              (collapsed)            │
│  ▶ Technical Indicators     (collapsed)            │
│  ▶ Market Concepts          (collapsed)            │
│  ▶ Investment Styles        (collapsed)            │
└───────────────────────────────────────────────────┘
```

- Categories: `GET /api/guide/categories`
- Topics: `GET /api/guide/{category}`
- Details: `GET /api/guide/{category}/{index}`
- Difficulty badge colors: beginner=up, intermediate=warning, advanced=accent

---

## Disclaimer Placement

| Location | Version |
|----------|---------|
| Settings page | Full text |
| AI analysis results | Full text |
| AI compare results | Full text |
| Sector screening results | Short: "AI-generated reference. Not financial advice." |
| AI Recommendation card | Short |

---

## Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Inline components | MoverCard, NewsItem, etc. as inline in pages | Simple components, not reused elsewhere |
| Compare chart | CompareChart.tsx with Lightweight Charts | Consistent with Chart.tsx, normalized return for fair comparison |
| Guide structure | Accordion (expand/collapse) | Space-efficient, users browse categories |
| Disclaimer | Both full and abbreviated versions | Full for dedicated AI pages, short for cards |

---

## Prerequisites & Dependencies

- Phase 7-8 completed
- Phase 6: all API endpoints operational
- Chart library (installed in Phase 8)

---

## Development Notes

- This Phase completes the **MVP**
- Bugs found in scenario testing are traced back to the responsible Phase for fixing
- Performance issues addressed via API cache TTL tuning or React memoization
- All AI results must include a disclaimer

---

## Change Log

| Date | Description |
|---|---|
| 2026-04-14 | Initial creation — Phase 9 for remaining pages after React migration |
| 2026-04-14 | Implementation complete — SectorScreening theme CRUD + progress display, CompareMode useState fix + CompareChart + AI result rendering, disclaimer placement |

---
---

# Phase 9 — 나머지 화면 + 최종 통합 `✅ 완료`

> Market Overview, Sector Screening, Compare Mode, Beginner's Guide UI 완성 + 면책 조항 배치

**완료일**: 2026-04-14
**상태**: ✅ 완료
**선행 조건**: Phase 8 완료 (QuickLook + AI 분석 화면 동작)
**디자인 레퍼런스**: `pre-requirement/design-spec.md`

---

## 개요

남은 4개 화면(Market Overview, Sector Screening, Compare Mode, Beginner's Guide)을 React로 구현하고, 면책 조항 배치, 로딩/에러 상태 처리를 수행한다. 이 Phase가 끝나면 **MVP 완성**.

---

## 완료 항목

| # | 모듈 | 상태 | 타입 |
|---|---|---|---|
| 1 | `pages/MarketOverview.tsx` | ✅ | project-specific |
| 2 | `pages/SectorScreening.tsx` | ✅ | project-specific |
| 3 | `pages/CompareMode.tsx` | ✅ | project-specific |
| 4 | `pages/Guide.tsx` | ✅ | project-specific |
| 5 | `components/CompareChart.tsx` | ✅ | project-specific |
| 6 | MoverCard (인라인) | ✅ | project-specific |
| 7 | NewsItem (인라인) | ✅ | project-specific |
| 8 | CompareBar (인라인) | ✅ | project-specific |
| 9 | CompareTable (인라인) | ✅ | project-specific |
| 10 | GuideAccordion (인라인) | ✅ | project-specific |
| 11 | `components/LoadingSkeleton.tsx` | ✅ | general |
| 12 | `components/ErrorBanner.tsx` | ✅ | general |

---

## Market Overview (기본 화면)

Gainers/Losers(`GET /api/market/movers`) + Market News(`GET /api/market/news`) 2열 그리드. 종목 클릭 시 `/quick-look/{ticker}` 이동. 뉴스 클릭 시 외부 URL 열림. 주요 지수는 하단 TickerBar에서 상시 표시 (중복 배치 없음).

---

## Sector Screening

GICS 11개 섹터 버튼 + 커스텀 테마(CRUD) + 분석 진행 단계 표시 + Top 5 결과. 체크박스 2개 이상 선택 시 "Compare Selected" 버튼 활성화 → `/compare?tickers=...` 이동.

---

## Compare Mode

티커 입력 → 비교 유형 자동 감지(same_sector/cross_sector) → 비교 테이블 → 정규화 수익률 차트(CompareChart.tsx, Base 100) → AI 비교 분석 실행 → 결과 표시 + 면책 조항. useState 버그 수정, AI 결과 구조화 렌더링 포함.

---

## Beginner's Guide

아코디언 카테고리(차트/핵심지표/기술지표/시장개념/투자스타일). 난이도 뱃지: beginner=up(초록), intermediate=warning(주황), advanced=accent(파랑). 펼치면 What/How/When/Example 구조.

---

## 면책 조항 배치

| 위치 | 버전 |
|------|------|
| Settings 화면 | 전체 문구 |
| AI 분석 결과 하단 | 전체 문구 |
| AI 비교 분석 하단 | 전체 문구 |
| Sector 결과 하단 | 축약: "AI-generated reference. Not financial advice." |
| AI Recommendation 카드 하단 | 축약 |

---

## 설계 결정 사항

| 결정 | 선택 | 이유 |
|---|---|---|
| 인라인 컴포넌트 | MoverCard, NewsItem 등 페이지 내 인라인 | 단순한 컴포넌트, 타 페이지에서 재사용 없음 |
| 비교 차트 | CompareChart.tsx + Lightweight Charts | Chart.tsx와 일관성, 정규화 수익률로 공정 비교 |
| 가이드 구조 | 아코디언(펼치기/접기) | 공간 효율적, 카테고리 탐색 용이 |
| 면책 조항 | 전체 + 축약 두 버전 | AI 전용 페이지는 전체, 카드에는 축약 |

---

## 선행 조건 및 의존성

- Phase 7~8 완료
- Phase 6의 모든 API 엔드포인트 동작
- 차트 라이브러리 (Phase 8에서 설치)

---

## 개발 시 주의사항

- 이 Phase가 끝나면 **MVP 완성**
- 시나리오 테스트에서 발견된 버그는 해당 Phase로 역추적하여 수정
- 성능 이슈는 API 캐시 TTL 조정 또는 React 메모이제이션으로 해결
- 모든 AI 결과에는 면책 조항 필수

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-14 | 신규 작성 — React 전환에 따른 Phase 9 신설 |
| 2026-04-14 | 구현 완료 — SectorScreening 테마 CRUD/진행 단계, CompareMode useState 버그 수정 + CompareChart 정규화 차트 + AI 결과 구조화 렌더링, 면책 조항 배치 |
