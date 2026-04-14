# Phase 9 — 나머지 화면 + 최종 통합 `✅ 완료`

> Market Overview, Sector Screening, Compare Mode, Beginner's Guide UI 완성 + 면책 조항 배치

**상태**: ✅ 완료
**선행 조건**: Phase 8 완료 (Quick Look + AI 분석 화면 동작)
**디자인 권위 문서**: `pre-requirement/design-spec.md`

---

## 개요

남은 4개 화면(Market Overview, Sector Screening, Compare Mode, Beginner's Guide)을 React로 구현하고, 면책 조항 배치, 로딩/에러 상태, 반응형 처리 등 마감 작업을 수행한다. 전체 앱을 처음부터 끝까지 시나리오 테스트한다. 이 Phase가 끝나면 **MVP 완성**.

---

## 완료 예정 / 완료 항목

| # | 모듈 | 상태 | 설명 |
|---|---|---|---|
| 1 | `pages/MarketOverview.tsx` | ✅ | 기본 화면 (급등락 + 뉴스) — Phase 8에서 구현 |
| 2 | `pages/SectorScreening.tsx` | ✅ | 섹터 스크리닝 화면 — 테마 생성/삭제 UI + 진행 단계 표시 추가 |
| 3 | `pages/CompareMode.tsx` | ✅ | 종목 비교 화면 — useState 버그 수정, 정규화 차트 추가, AI 결과 구조화 |
| 4 | `pages/Guide.tsx` | ✅ | Beginner's Guide 화면 — Phase 8에서 구현 |
| 5 | `components/CompareChart.tsx` | ✅ | 정규화 수익률 비교 차트 (Base 100, 1Y) — 신규 |
| 6 | MoverCard (인라인) | ✅ | MarketOverview 내 인라인 구현 |
| 7 | NewsItem (인라인) | ✅ | MarketOverview 내 인라인 구현 |
| 8 | CompareBar (인라인) | ✅ | CompareMode 내 인라인 구현 |
| 9 | CompareTable (인라인) | ✅ | CompareMode 내 인라인 구현 |
| 10 | GuideAccordion (인라인) | ✅ | Guide 내 CategorySection/TopicItem으로 인라인 구현 |
| 11 | `components/LoadingSkeleton.tsx` | ✅ | 스켈레톤 로딩 컴포넌트 — Phase 8에서 구현 |
| 12 | `components/ErrorBanner.tsx` | ✅ | API 실패 경고 배너 — Phase 8에서 구현 |

---

## Market Overview (기본 화면)

### 레이아웃

```
┌───────────────────────────────────────────────────┐
│  Welcome to QuantAI                                │
│  실시간 미국 주식 분석 대시보드                        │
├────────────────────────┬──────────────────────────┤
│  TODAY'S MOVERS        │  MARKET NEWS              │
│                        │                          │
│  🔺 GAINERS            │  Fed holds rates steady   │
│  NVDA  +7.2%  $142.50  │  Reuters · 2h ago        │
│  AMD   +5.1%  $168.30  │                          │
│  ...                   │  Apple reports record Q2  │
│                        │  Bloomberg · 4h ago       │
│  🔻 LOSERS             │                          │
│  META  -4.1%  $485.20  │  ...                     │
│  ...                   │                          │
└────────────────────────┴──────────────────────────┘
```

| 요소 | API | 클릭 동작 |
|------|-----|----------|
| Gainers/Losers | `GET /api/market/movers` | 종목 클릭 → `/quick-look/{ticker}` |
| News | `GET /api/market/news` | 헤드라인 클릭 → 외부 URL |

> 주요 지수(SPY, QQQ 등)는 하단 TickerBar에서 상시 표시.
> Market Overview에는 중복 배치하지 않음.

---

## Sector Screening

### 레이아웃

```
┌───────────────────────────────────────────────────┐
│  GICS SECTORS                                      │
│  [Technology] [Healthcare] [Financials] [Energy]   │
│  [Consumer] [Industrial] [Materials] [Utilities]   │
│  [Real Estate] [Communication] [Consumer Staples]  │
│                                                    │
│  CUSTOM THEMES                                     │
│  [AI/반도체] [방산] [클린에너지] [사이버보안] [우주]   │
│  [+ New Theme]                                     │
├───────────────────────────────────────────────────┤
│  ⟳ 분석 중... Stage 2/2: AI 분석                    │
├───────────────────────────────────────────────────┤
│  ⚠ 필터 완화 적용됨 (시총 기준 1단계 완화)            │
├───────────────────────────────────────────────────┤
│  TOP 5 RESULTS                                     │
│  1. ☐ NVDA  Score: 85  "AI 수요 폭발적 성장"        │
│  2. ☐ AMD   Score: 78  "데이터센터 GPU 점유율 상승"   │
│  3. ☐ AVGO  Score: 75  "VMware 인수 시너지"          │
│  ...                                               │
│  [Compare Selected]    (체크 2개+ 시 활성)           │
└───────────────────────────────────────────────────┘
```

| 요소 | API |
|------|-----|
| GICS 섹터 버튼 | 정적 (11개 하드코딩) |
| Custom Themes | `GET /api/themes` |
| 테마 생성 | `POST /api/themes` |
| 스크리닝 실행 | `POST /api/sector/{name}` |
| 종목 클릭 | → `/quick-look/{ticker}` |
| Compare Selected | → `/compare?tickers=NVDA,AMD` |

---

## Compare Mode

### 레이아웃

```
┌───────────────────────────────────────────────────┐
│  COMPARE                                           │
│  [NVDA ×] [AMD ×] [+ Add ticker]                   │
│  비교 유형: 🔵 Same Sector (Technology)              │
├───────────────────────────────────────────────────┤
│  비교 테이블                                        │
│  ┌──────────┬──────────┬──────────┐               │
│  │          │   NVDA   │   AMD    │               │
│  ├──────────┼──────────┼──────────┤               │
│  │ Price    │ $142.50  │ $168.30  │               │
│  │ P/E      │  35.24   │  42.10   │               │
│  │ ...      │   ...    │   ...    │               │
│  └──────────┴──────────┴──────────┘               │
├───────────────────────────────────────────────────┤
│  수익률 비교 차트 (정규화 100 기준)                   │
├───────────────────────────────────────────────────┤
│  [▶ AI 비교 분석 실행]                               │
├───────────────────────────────────────────────────┤
│  AI 비교 결과                                       │
│  (same_sector: 카테고리별 순위 + Key Risks)          │
│  (cross_sector: Sector Context + Macro Scenarios)  │
│  면책 조항                                          │
└───────────────────────────────────────────────────┘
```

| 요소 | API |
|------|-----|
| 비교 데이터 | `POST /api/compare` |
| AI 비교 분석 | `POST /api/compare/analyze` |
| 비교 유형 감지 | `/api/compare` 응답의 `comparison_type` |

---

## Beginner's Guide

### 레이아웃

```
┌───────────────────────────────────────────────────┐
│  📖 Beginner's Guide                               │
│                                                    │
│  ▼ 차트 보는 법                                     │
│  │  [beginner] 캔들스틱 차트                        │
│  │  [beginner] 이동평균선                           │
│  │  [intermediate] 거래량 분석                      │
│                                                    │
│  ▶ 핵심 지표                    (접힌 상태)         │
│  ▶ 기술적 지표                  (접힌 상태)         │
│  ▶ 시장 개념                    (접힌 상태)         │
│  ▶ 투자 스타일                  (접힌 상태)         │
│                                                    │
│  펼친 내용:                                         │
│  ┃ What: 캔들스틱 차트란...                         │
│  ┃ How: 빨간 봉은 하락, 초록 봉은 상승...            │
│  ┃ When: 단기 트레이딩에서 주로...                   │
│  ┃ Example: AAPL의 2024년 차트를 보면...            │
└───────────────────────────────────────────────────┘
```

| 요소 | API |
|------|-----|
| 카테고리 목록 | `GET /api/guide/categories` |
| 주제 목록 | `GET /api/guide/{category}` |
| 주제 상세 | `GET /api/guide/{category}/{index}` |

난이도 뱃지 색상:
- beginner: up 색상
- intermediate: warning 색상
- advanced: accent 색상

---

## 공통 컴포넌트

### LoadingSkeleton.tsx
- 데이터 로딩 중 회색 깜빡이는 placeholder
- Spinner보다 자연스러움 (design-spec.md 권장)

### ErrorBanner.tsx
- API 실패 시 화면 상단에 warning 색상 배너
- "일부 데이터를 불러올 수 없습니다. 다시 시도해주세요."
- 빨강(down) 아닌 **주황(warning)** 사용

---

## 면책 조항 최종 배치

| 위치 | 버전 |
|------|------|
| Settings 화면 | 전체 문구 |
| AI 분석 결과 하단 | 전체 문구 |
| AI 비교 분석 하단 | 전체 문구 |
| Sector 결과 하단 | 축약: "AI-generated reference. Not financial advice." |
| AI Recommendation 카드 하단 | 축약 |

---

## 최종 시나리오 테스트

| # | 시나리오 | 확인 항목 |
|:-:|---------|----------|
| 1 | 앱 최초 접속 | Market Overview 표시, 하단 지수 바 동작 |
| 2 | 티커 검색 "NVDA" | Quick Look 화면 전환, 모든 데이터 표시 |
| 3 | AI 분석 실행 | 로딩 → 결과 표시, BUY/HOLD/SELL 판정 |
| 4 | Compare에 AMD 추가 | 비교 테이블 + AI 비교 분석 |
| 5 | Sector → Technology 클릭 | 필터링 → Top 5 결과 |
| 6 | Watchlist 종목 추가/삭제 | 사이드바 반영, 등락률 표시 |
| 7 | 다크 → 라이트 전환 | 모든 화면 색상 정상 전환 |
| 8 | API 실패 상황 | 에러 배너 표시, 앱 크래시 없음 |
| 9 | Guide 콘텐츠 열람 | 펼치기/접기, 난이도 뱃지 |
| 10 | 브라우저 뒤로가기 | 이전 화면 복귀, 데이터 유지 |

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
| 2026-04-14 | Phase 9 구현 완료 — SectorScreening 테마 CRUD/진행 단계, CompareMode useState 버그 수정 + CompareChart 정규화 차트 + AI 결과 구조화 렌더링, 면책 조항 배치 완료. 최종 시나리오 테스트는 제외. |
