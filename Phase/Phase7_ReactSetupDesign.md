# Phase 7 — React Setup + Design System + Layout `✅ Completed`

> React project creation, Dark/Light theme system, sidebar, routing, and bottom market index bar

**Completed**: 2026-04-14
**Status**: ✅ Completed
**Prerequisites**: Phase 6 completed (FastAPI server operational)
**Design Reference**: `pre-requirement/design-spec.md`

---

## Overview

Create the React project and translate design-spec.md tokens (colors, fonts, spacing) into TypeScript. Implement Dark/Light theme switching, sidebar (search + menus + watchlist), page routing, and the bottom market index bar. This Phase produces the **app skeleton** that all subsequent UI Phases build on.

---

## Deliverables

| # | Module | Status | Type |
|---|---|---|---|
| 1 | `frontend/` project setup | ✅ | project-specific |
| 2 | `src/theme/tokens.ts` | ✅ | project-specific |
| 3 | `src/theme/dark.ts` + `light.ts` | ✅ | project-specific |
| 4 | `src/theme/ThemeProvider.tsx` | ✅ | project-specific |
| 5 | `src/components/Sidebar.tsx` | ✅ | project-specific |
| 6 | `src/App.tsx` + routing | ✅ | project-specific |
| 7 | `src/components/TickerBar.tsx` | ✅ | project-specific |
| 8 | `src/hooks/useApi.ts` | ✅ | general |
| 9 | `src/types/api.ts` | ✅ | project-specific |
| 10 | `src/pages/Settings.tsx` | ✅ | project-specific |
| 11 | `src/config.ts` | ✅ | project-specific |
| 12 | `src/hooks/useBreakpoint.ts` | ✅ | general |

---

## Design System (theme/)

### tokens.ts

Translates design-spec.md chapters 3-5 into TypeScript constants:

```typescript
export const FONTS = {
  body:    "'Inter', 'Pretendard', sans-serif",
  numeric: "'JetBrains Mono', 'IBM Plex Mono', monospace",
}
export const FONT_SIZES = { xs: "11px", sm: "13px", md: "14px", lg: "16px", xl: "20px", "2xl": "24px" }
export const SPACING    = { xs: "4px", sm: "8px", md: "16px", lg: "24px", xl: "32px" }
export const RADIUS     = { card: "8px", button: "6px", badge: "4px", pill: "9999px" }
```

### dark.ts / light.ts

Each exports a theme object with semantic color tokens (`bg_primary`, `bg_card`, `text_primary`, `accent`, `up`, `down`, `warning`, etc.).

### ThemeProvider.tsx

React Context providing `{ theme, mode, toggleTheme }` to the entire app. Default mode: dark.

---

## Sidebar (Sidebar.tsx)

240px fixed-width sidebar with 6 sections:

1. **Logo** — QuantAI branding
2. **Search** — Ticker input (autocomplete added in Phase 10)
3. **Menu** — 5 items: Market Overview, Quick Look, Compare Mode, Sector Screening, Beginner's Guide
4. **Watchlist** — Real-time quotes via `GET /api/watchlist`, 60s polling
5. **AI Usage** — Progress bar (local state)
6. **Settings** — Link to Settings page

---

## Routing (App.tsx)

React Router URL-to-page mapping:

| Path | Page |
|------|------|
| `/` | MarketOverview |
| `/quick-look/:ticker` | QuickLook |
| `/compare` | CompareMode |
| `/sector` | SectorScreening |
| `/guide` | Guide |
| `/settings` | Settings |

---

## TickerBar (TickerBar.tsx)

Bottom bar displayed on all pages, showing 6 indices: SPY, QQQ, DIA, BTC, ETH, VIX. Data from `GET /api/market/indices`, auto-refreshed every 60 seconds.

---

## API Hook (useApi.ts)

Generic fetch wrapper handling loading/error states:

```typescript
function useApi<T>(url: string): { data: T | null; loading: boolean; error: string | null }
```

Also provides `usePolling` for periodic data refresh and `usePost` for POST requests.

---

## Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Build tool | Vite | Fast HMR, native ESM, simple proxy config |
| Styling | Inline styles + tokens.ts | Consistency with project patterns, no CSS-in-JS library needed |
| Theme switching | React Context | Simple, no external state library required |
| Sidebar width | 240px fixed | design-spec.md specification |
| Numeric font | JetBrains Mono | Monospace for financial data readability |

---

## Prerequisites & Dependencies

- Phase 6: FastAPI server running on `localhost:8000`
- Node.js 18+, npm
- npm packages: `react`, `react-router-dom`, `typescript`, `vite`
- Google Fonts: Inter, JetBrains Mono

---

## Development Notes

- design-spec.md is the authoritative design document
- All numbers use `FONTS.numeric` (JetBrains Mono)
- Do not use up/down colors for non-price elements
- Pages built in Phase 8-9 are left as empty placeholders

---

## Change Log

| Date | Description |
|---|---|
| 2026-04-06 | Initial creation (Streamlit UI) |
| 2026-04-14 | React migration — full rewrite as project setup + design system + layout |
| 2026-04-14 | Implementation complete — theme/ 4 files + Sidebar + TickerBar + App routing + Settings + config.ts |

---
---

# Phase 7 — React 셋업 + 디자인 시스템 + 레이아웃 `✅ 완료`

> React 프로젝트 생성, Dark/Light 테마 시스템, 사이드바, 라우팅, 하단 마켓 지수 바

**완료일**: 2026-04-14
**상태**: ✅ 완료
**선행 조건**: Phase 6 완료 (FastAPI 서버 동작 확인)
**디자인 레퍼런스**: `pre-requirement/design-spec.md`

---

## 개요

React 프로젝트를 생성하고, design-spec.md의 디자인 토큰(색상, 폰트, 간격)을 TypeScript로 옮긴다. Dark/Light 테마 전환, 사이드바(검색+메뉴+Watchlist), 페이지 라우팅, 하단 마켓 지수 바를 구현한다. 이 Phase가 끝나면 **앱의 뼈대**가 완성된다.

---

## 완료 항목

| # | 모듈 | 상태 | 타입 |
|---|---|---|---|
| 1 | `frontend/` 프로젝트 셋업 | ✅ | project-specific |
| 2 | `src/theme/tokens.ts` | ✅ | project-specific |
| 3 | `src/theme/dark.ts` + `light.ts` | ✅ | project-specific |
| 4 | `src/theme/ThemeProvider.tsx` | ✅ | project-specific |
| 5 | `src/components/Sidebar.tsx` | ✅ | project-specific |
| 6 | `src/App.tsx` + 라우팅 | ✅ | project-specific |
| 7 | `src/components/TickerBar.tsx` | ✅ | project-specific |
| 8 | `src/hooks/useApi.ts` | ✅ | general |
| 9 | `src/types/api.ts` | ✅ | project-specific |
| 10 | `src/pages/Settings.tsx` | ✅ | project-specific |
| 11 | `src/config.ts` | ✅ | project-specific |
| 12 | `src/hooks/useBreakpoint.ts` | ✅ | general |

---

## 디자인 시스템 (theme/)

### tokens.ts

design-spec.md 3~5장을 TypeScript 상수로 변환: 폰트(Inter/JetBrains Mono), 폰트 크기, 간격, 보더 라디우스.

### dark.ts / light.ts

시맨틱 색상 토큰(`bg_primary`, `bg_card`, `text_primary`, `accent`, `up`, `down`, `warning` 등)을 포함하는 테마 객체.

### ThemeProvider.tsx

React Context로 `{ theme, mode, toggleTheme }`을 앱 전체에 공급. 기본 모드: dark.

---

## 사이드바 (Sidebar.tsx)

240px 고정 폭, 6개 섹션:

1. **로고** — QuantAI 브랜딩
2. **검색** — 티커 입력 (자동완성은 Phase 10에서 추가)
3. **메뉴** — 5개: Market Overview, Quick Look, Compare Mode, Sector Screening, Beginner's Guide
4. **Watchlist** — `GET /api/watchlist` 60초 폴링
5. **AI Usage** — 진행 바 (로컬 상태)
6. **Settings** — 설정 페이지 링크

---

## 라우팅 (App.tsx)

React Router로 URL ↔ 화면 매핑:

| 경로 | 페이지 |
|------|------|
| `/` | MarketOverview |
| `/quick-look/:ticker` | QuickLook |
| `/compare` | CompareMode |
| `/sector` | SectorScreening |
| `/guide` | Guide |
| `/settings` | Settings |

---

## 하단 마켓 지수 바 (TickerBar.tsx)

모든 페이지 하단에 상시 표시. 6개 지수: SPY, QQQ, DIA, BTC, ETH, VIX. `GET /api/market/indices`에서 데이터, 60초마다 자동 갱신.

---

## API Hook (useApi.ts)

로딩/에러 처리를 포함하는 범용 fetch 래퍼. `usePolling`(주기적 갱신), `usePost`(POST 요청)도 제공.

---

## 설계 결정 사항

| 결정 | 선택 | 이유 |
|---|---|---|
| 빌드 도구 | Vite | 빠른 HMR, 네이티브 ESM, 간편한 프록시 설정 |
| 스타일링 | 인라인 스타일 + tokens.ts | 프로젝트 패턴 일관성, CSS-in-JS 라이브러리 불필요 |
| 테마 전환 | React Context | 단순, 외부 상태 라이브러리 불필요 |
| 사이드바 폭 | 240px 고정 | design-spec.md 명세 |
| 숫자 폰트 | JetBrains Mono | 금융 데이터 가독성을 위한 monospace |

---

## 선행 조건 및 의존성

- Phase 6: FastAPI 서버 `localhost:8000` 동작
- Node.js 18+, npm
- npm 패키지: `react`, `react-router-dom`, `typescript`, `vite`
- Google Fonts: Inter, JetBrains Mono

---

## 개발 시 주의사항

- design-spec.md를 디자인 권위 문서로 참조
- 모든 숫자는 `FONTS.numeric` (JetBrains Mono) 사용
- 주가 외 요소에 up/down 색상 사용 금지
- Phase 8~9에서 만들 페이지는 빈 placeholder로 남겨둠

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-06 | 최초 작성 (Streamlit UI) |
| 2026-04-14 | React 전환 — 프로젝트 셋업 + 디자인 시스템 + 레이아웃으로 전면 재작성 |
| 2026-04-14 | 구현 완료 — theme/ 4파일 + Sidebar + TickerBar + App 라우팅 + Settings + config.ts |
