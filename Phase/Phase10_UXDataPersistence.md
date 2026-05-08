# Phase 10 — UX Improvements + Data Persistence `✅ Completed`

> Search autocomplete, Watchlist UI, SQLite persistence, price alerts, responsive layout

**Completed**: 2026-04-14
**Status**: ✅ Completed
**Prerequisites**: Phase 9 completed (all pages implemented + disclaimer placement)

---

## Overview

After MVP completion, this phase implements the 5 highest-impact improvements from a real-usage perspective: search UX (autocomplete), direct Watchlist manipulation, data persistence (JSON → SQLite), price alerts, and mobile/tablet responsive layout.

---

## Deliverables

| # | Module | Status | Description |
|---|---|---|---|
| 1 | Search Autocomplete | ✅ | `SearchAutocomplete.tsx` + `backend/routers/search.py` + `data/ticker_list.py` |
| 2 | Watchlist Button | ✅ | `WatchlistButton.tsx` — Add/Remove toggle on Quick Look |
| 3 | SQLite Persistence | ✅ | `data/database.py` + `data/analysis_cache.py` — Watchlist/Themes/AI cache → SQLite |
| 4 | Price Alerts | ✅ | `AlertModal.tsx` + `AlertToast.tsx` + `useAlerts.ts` + `data/alerts.py` + `backend/routers/alerts.py` |
| 5 | Responsive Layout | ✅ | `useBreakpoint.ts` — mobile/tablet adaptation |

---

## 1. Search Autocomplete

### Purpose
Provide dropdown autocomplete based on S&P 500 stock list during ticker input.

### Implementation Files

| Location | File | Description |
|----------|------|-------------|
| Backend | `backend/routers/search.py` | `GET /api/search?q=NV` → matching stocks |
| Backend | `data/ticker_list.py` | S&P 500 stock list (ticker + name) |
| Frontend | `components/SearchAutocomplete.tsx` | Dropdown UI component |
| Frontend | `components/Sidebar.tsx` | Replace `<input>` with `<SearchAutocomplete>` |

### Core Structure

```
Backend:
  GET /api/search?q=NV&limit=8
  → [{ ticker: "NVDA", name: "NVIDIA Corp" }, { ticker: "NVS", name: "Novartis AG" }]

  Matching: ticker.startsWith(q) || name.toLowerCase().includes(q)
  Sort: exact ticker match first, then by name

Frontend:
  SearchAutocomplete
  ├── input (debounce 200ms)
  ├── dropdown list (max 8 items)
  │   └── each item: [NVDA] NVIDIA Corp  ← click → /quick-look/NVDA
  └── Esc / outside click to close
```

### Design Decisions

| Decision | Reason |
|----------|--------|
| S&P 500 + major ETF static list | Instant response without external API calls |
| Server-side filtering | 500+ stocks — more efficient than sending all to frontend |
| 200ms debounce | Prevent excessive API calls while typing |
| Keyboard navigation | ↑↓ arrow keys + Enter selection support |

---

## 2. Watchlist Add/Remove Button

### Purpose
Add a one-click "Add to Watchlist" / "Remove from Watchlist" toggle button on the Quick Look page.

### Implementation Files

| Location | File | Description |
|----------|------|-------------|
| Frontend | `components/WatchlistButton.tsx` | Toggle button component |
| Frontend | `pages/QuickLook.tsx` | Button placement next to PriceHeader |
| Frontend | `hooks/useApi.ts` | Uses existing `usePost` |

### Core Structure

```
WatchlistButton({ ticker })
├── Check current state: GET /api/watchlist → check if ticker in array
├── Add: POST /api/watchlist/{ticker}
├── Remove: DELETE /api/watchlist/{ticker}
└── UI: ☆ (not added) / ★ (added) toggle icon + text
```

### Design Decisions

| Decision | Reason |
|----------|--------|
| Star (★/☆) icon toggle | Intuitive, minimal space |
| Optimistic update | Instant UI change on click → API call → rollback on failure |
| Sidebar watchlist auto-refresh | Reflected within 60s polling cycle after button click |

---

## 3. SQLite Persistence

### Purpose
Migrate Watchlist and Themes from JSON files to SQLite for concurrency safety, and add AI analysis result caching.

### Implementation Files

| Location | File | Description |
|----------|------|-------------|
| Backend | `data/database.py` | SQLite connection management + table init |
| Backend | `data/watchlist.py` | JSON → SQLite migration |
| Backend | `data/theme_manager.py` | JSON → SQLite migration |
| Backend | `data/analysis_cache.py` | AI analysis result cache |
| DB File | `data/app.db` | SQLite database file (auto-created) |

### Database Schema

```sql
CREATE TABLE watchlist (
    ticker TEXT PRIMARY KEY,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE themes (
    name TEXT PRIMARY KEY,
    tickers TEXT NOT NULL,
    preset TEXT NOT NULL,
    is_default BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE analysis_cache (
    ticker TEXT NOT NULL,
    result TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    PRIMARY KEY (ticker)
);

CREATE TABLE price_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    target_price REAL NOT NULL,
    direction TEXT NOT NULL,
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    triggered_at TIMESTAMP
);
```

### Design Decisions

| Decision | Reason |
|----------|--------|
| SQLite (no separate server) | Suitable for single-user app, Python built-in module |
| WAL mode | Improved concurrent read/write performance |
| AI cache 24h TTL | Market data changes daily; same-day reuse |
| JSON → SQLite migration | Auto-import config/*.json on first run |
| No router code changes | Only data/ layer replaced, interface preserved |

---

## 4. Price Alerts

### Purpose
Set target prices for Watchlist stocks and display frontend notifications when current price reaches the target.

### API Endpoints

```
POST   /api/alerts              — Create alert { ticker, target_price, direction }
GET    /api/alerts              — Active alerts list
DELETE /api/alerts/{id}         — Delete alert
GET    /api/alerts/triggered    — Recently triggered alerts (frontend polling)
```

### Core Structure

```
Backend check logic:
  1. On GET /api/alerts/triggered
  2. Query current price for each active alert's ticker
  3. direction='above' && current_price >= target_price → triggered
  4. direction='below' && current_price <= target_price → triggered
  5. Triggered alert: active=0, triggered_at=now()

Frontend flow:
  Sidebar Watchlist
  ├── 🔔 icon next to stock → opens AlertModal
  │   ├── Target price input
  │   ├── Direction select (above / below)
  │   └── Save button → POST /api/alerts
  └── useAlerts hook (30s polling)
      └── Triggered alert → AlertToast (top-right)

AlertToast:
  ┌──────────────────────────┐
  │ 🔔 NVDA reached $150.00  │
  │ Target: above $148.00     │
  │              [Dismiss]    │
  └──────────────────────────┘
  → Auto-dismiss after 5s or click Dismiss
```

### Design Decisions

| Decision | Reason |
|----------|--------|
| Backend polling (not WebSocket) | Architectural consistency, simpler implementation |
| 30s polling interval | Appropriate balance for non-real-time alerts |
| Auto-deactivate after trigger | Prevent repeated alerts; user can re-set manually |
| SQLite price_alerts table | Implemented alongside #3 persistence |

---

## 5. Responsive Layout

### Purpose
Adapt the desktop-only fixed 240px sidebar layout for mobile (≤640px) and tablet (641–1024px).

### Implementation Files

| Location | File | Description |
|----------|------|-------------|
| Frontend | `hooks/useBreakpoint.ts` | Responsive breakpoint hook |
| Frontend | `components/Sidebar.tsx` | Mobile: overlay + hamburger toggle |
| Frontend | `components/TickerBar.tsx` | Mobile: condensed display |
| Frontend | `App.tsx` | Layout branching |
| Frontend | `pages/*.tsx` | Grid adjustments per page |
| Frontend | `styles/global.css` | Media queries |

### Breakpoints

```
Desktop:  1025px+    — Current layout maintained
Tablet:   641–1024px — Sidebar collapsible, 2-column grid
Mobile:   ≤640px     — Sidebar overlay, 1-column grid, TickerBar 3 items
```

### Per-Page Responsive Changes

| Page | Desktop | Mobile |
|------|---------|--------|
| MarketOverview | Movers + News 2-column | 1-column vertical |
| QuickLook | KPI 4 cards in 1 row, Chart + Tech side by side | KPI 2-column, Chart full width, Tech vertical |
| CompareMode | Full-width comparison table | Horizontal scroll table |
| SectorScreening | Sector buttons flex-wrap | Same (natural wrapping) |
| AIAnalysis | Bull/Bear 2-column | 1-column vertical |
| Guide | Full-width accordion | Same (already 1-column) |

### Design Decisions

| Decision | Reason |
|----------|--------|
| CSS media queries + JS hook | Layout via CSS, conditional rendering via JS hook |
| Sidebar overlay (drawer) | Fixed sidebar takes too much space on mobile |
| TickerBar mobile 3 items | All 6 indices would reduce readability |
| No Tailwind (existing inline styles) | Project consistency, no additional dependencies |

---

## Implementation Order

```
Step 1: SQLite persistence (#3) → Data layer stabilization
Step 2: Watchlist button (#2) → Built on SQLite-backed Watchlist
Step 3: Search autocomplete (#1) → Independent feature
Step 4: Price alerts (#4) → SQLite price_alerts table + Watchlist UI extension
Step 5: Responsive layout (#5) → Layout adjustments after all features complete
```

---

## Prerequisites & Dependencies

- Phase 9 completed (all pages implemented)
- Python built-in `sqlite3` module (no additional installation)
- Existing `data/watchlist.py`, `data/theme_manager.py` interface preserved

---

## Development Notes

- Preserve existing `config/*.json` data during SQLite migration (keep as backup)
- `data/app.db` added to `.gitignore` (per-user data)
- Responsive work done last to minimize layout change impact on other features
- Alert polling minimizes app performance impact (30s interval, background)
- Search autocomplete dropdown requires z-index management (inside sidebar)

---

## Change Log

| Date | Description |
|---|---|
| 2026-04-14 | Initial creation — 5 UX improvement items + SQLite persistence plan |
| 2026-04-14 | ✅ All 5 items implemented + Koyeb/Netlify deployment config |

---
---

# Phase 10 — UX 개선 + 데이터 영속화 `✅ 완료`

> 검색 자동완성, Watchlist UI, SQLite 영속화, 가격 알림, 반응형 레이아웃

**완료일**: 2026-04-14
**상태**: ✅ 완료
**선행 조건**: Phase 9 완료 (모든 화면 구현 + 면책 조항 배치)

---

## 개요

MVP 완성 후 실사용 관점에서 가장 효과 높은 5가지 개선을 수행한다. 검색 UX 개선(자동완성), Watchlist 직접 조작, 데이터 영속화(JSON → SQLite), 가격 알림, 그리고 모바일/태블릿 반응형 레이아웃을 구현한다.

---

## 완료 항목

| # | 모듈 | 상태 | 설명 |
|---|---|---|---|
| 1 | 검색 자동완성 | ✅ | `SearchAutocomplete.tsx` + `backend/routers/search.py` + `data/ticker_list.py` |
| 2 | Watchlist 버튼 | ✅ | `WatchlistButton.tsx` — Quick Look에 Add/Remove 토글 |
| 3 | SQLite 영속화 | ✅ | `data/database.py` + `data/analysis_cache.py` — Watchlist/Themes/AI 캐시 → SQLite |
| 4 | 가격 알림 | ✅ | `AlertModal.tsx` + `AlertToast.tsx` + `useAlerts.ts` + `data/alerts.py` + `backend/routers/alerts.py` |
| 5 | 반응형 레이아웃 | ✅ | `useBreakpoint.ts` — 모바일/태블릿 대응 |

---

## 1. 검색 자동완성

### 목적
S&P 500 종목 리스트를 기반으로 입력 중 드롭다운 자동완성을 제공하여 사용성을 개선한다.

### 구현 파일

| 위치 | 파일 | 설명 |
|------|------|------|
| Backend | `backend/routers/search.py` | `GET /api/search?q=NV` → 매칭 종목 반환 |
| Backend | `data/ticker_list.py` | S&P 500 종목 리스트 (ticker + name) |
| Frontend | `components/SearchAutocomplete.tsx` | 드롭다운 UI 컴포넌트 |
| Frontend | `components/Sidebar.tsx` | 기존 `<input>` → `<SearchAutocomplete>` 교체 |

### 핵심 구조

```
Backend:
  GET /api/search?q=NV&limit=8
  → [{ ticker: "NVDA", name: "NVIDIA Corp" }, { ticker: "NVS", name: "Novartis AG" }]

  매칭 로직: ticker.startsWith(q) || name.toLowerCase().includes(q)
  정렬: ticker 정확 매칭 우선, 나머지 이름순

Frontend:
  SearchAutocomplete
  ├── input (debounce 200ms)
  ├── 드롭다운 목록 (최대 8개)
  │   └── 각 항목: [NVDA] NVIDIA Corp  ← 클릭 시 /quick-look/NVDA 이동
  └── Esc / 외부 클릭 시 닫기
```

### 설계 결정 사항

| 결정 | 이유 |
|------|------|
| S&P 500 + 주요 ETF 정적 리스트 | 외부 API 호출 없이 즉시 응답 가능 |
| 백엔드에서 필터링 | 종목 리스트가 500+개이므로 프론트에 전체 전송보다 효율적 |
| debounce 200ms | 타이핑 중 과도한 API 호출 방지 |
| 키보드 네비게이션 | ↑↓ 방향키 + Enter 선택 지원 |

---

## 2. Watchlist 추가/삭제 버튼

### 목적
Quick Look 화면에 "Add to Watchlist" / "Remove from Watchlist" 토글 버튼을 추가하여 한 클릭으로 관리할 수 있게 한다.

### 구현 파일

| 위치 | 파일 | 설명 |
|------|------|------|
| Frontend | `components/WatchlistButton.tsx` | 토글 버튼 컴포넌트 |
| Frontend | `pages/QuickLook.tsx` | PriceHeader 옆에 버튼 배치 |
| Frontend | `hooks/useApi.ts` | 기존 `usePost` 활용 |

### 설계 결정 사항

| 결정 | 이유 |
|------|------|
| 별(★/☆) 아이콘 토글 | 직관적이고 공간 최소화 |
| 낙관적 업데이트 | 클릭 즉시 UI 변경 → API 호출 → 실패 시 롤백 |
| Sidebar watchlist 자동 갱신 | 버튼 클릭 후 사이드바 폴링 주기(60s) 내 반영 |

---

## 3. SQLite 영속화

### 목적
Watchlist(`config/watchlist.json`)와 Themes(`config/themes.json`)를 SQLite로 전환하여 동시성 안전성을 확보하고, AI 분석 결과 캐시를 추가한다.

### 구현 파일

| 위치 | 파일 | 설명 |
|------|------|------|
| Backend | `data/database.py` | SQLite 연결 관리 + 테이블 초기화 |
| Backend | `data/watchlist.py` | JSON → SQLite 전환 |
| Backend | `data/theme_manager.py` | JSON → SQLite 전환 |
| Backend | `data/analysis_cache.py` | AI 분석 결과 캐시 |
| DB 파일 | `data/app.db` | SQLite 데이터베이스 파일 (자동 생성) |

### 데이터베이스 스키마

```sql
CREATE TABLE watchlist (
    ticker TEXT PRIMARY KEY,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE themes (
    name TEXT PRIMARY KEY,
    tickers TEXT NOT NULL,
    preset TEXT NOT NULL,
    is_default BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE analysis_cache (
    ticker TEXT NOT NULL,
    result TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    PRIMARY KEY (ticker)
);

CREATE TABLE price_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    target_price REAL NOT NULL,
    direction TEXT NOT NULL,
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    triggered_at TIMESTAMP
);
```

### 설계 결정 사항

| 결정 | 이유 |
|------|------|
| SQLite (별도 서버 불필요) | 단일 사용자 앱에 적합, Python 내장 모듈 |
| WAL 모드 | 읽기/쓰기 동시 처리 성능 향상 |
| AI 캐시 24시간 TTL | 시장 데이터는 하루 단위로 변하므로 당일 재사용 |
| 기존 JSON → SQLite 마이그레이션 | 최초 실행 시 config/*.json 데이터를 DB로 이관 |
| 라우터 코드 변경 없음 | data/ 레이어만 교체, 인터페이스 유지 |

---

## 4. 가격 알림

### 목적
Watchlist 종목에 목표가를 설정하고, 현재가가 목표에 도달하면 프론트엔드에 알림을 표시한다.

### API 엔드포인트

```
POST   /api/alerts              — 알림 생성 { ticker, target_price, direction }
GET    /api/alerts              — 활성 알림 목록
DELETE /api/alerts/{id}         — 알림 삭제
GET    /api/alerts/triggered    — 최근 트리거된 알림 조회 (프론트 폴링용)
```

### 핵심 구조

```
백엔드 체크 로직:
  1. GET /api/alerts/triggered 호출 시
  2. 활성 알림의 각 ticker 현재가 조회
  3. direction='above' && current_price >= target_price → triggered
  4. direction='below' && current_price <= target_price → triggered
  5. 트리거된 알림: active=0, triggered_at=now() 저장

프론트엔드 플로우:
  Sidebar Watchlist
  ├── 종목 옆 🔔 아이콘 클릭 → AlertModal 열기
  │   ├── 목표가 입력
  │   ├── 방향 선택 (위로 돌파 / 아래로 하락)
  │   └── 설정 버튼 → POST /api/alerts
  └── useAlerts hook (30초 폴링)
      └── 트리거된 알림 있으면 → AlertToast 표시 (우측 상단)
```

### 설계 결정 사항

| 결정 | 이유 |
|------|------|
| 백엔드 폴링 방식 (WebSocket 아님) | 현재 아키텍처 일관성 유지, 구현 단순 |
| 30초 폴링 간격 | 실시간 필요 없는 알림에 적절한 균형 |
| 트리거 후 자동 비활성화 | 반복 알림 방지, 재설정은 사용자가 수동으로 |
| SQLite price_alerts 테이블 | #3 영속화와 함께 구현 |

---

## 5. 반응형 레이아웃

### 목적
모바일(≤640px) 및 태블릿(641~1024px)에서도 사용 가능하도록 반응형 레이아웃을 적용한다.

### Breakpoint 기준

```
Desktop:  1025px 이상  — 현재 레이아웃 유지
Tablet:   641~1024px   — 사이드바 접기 가능, 그리드 2열 유지
Mobile:   ≤640px       — 사이드바 오버레이, 그리드 1열, TickerBar 축소
```

### 각 페이지 반응형 변경

| 페이지 | Desktop | Mobile |
|--------|---------|--------|
| MarketOverview | Movers + News 2열 그리드 | 1열 세로 배치 |
| QuickLook | KPI 4카드 1행, 차트 + Tech Cards 나란히 | KPI 2열, 차트 풀 너비, Tech Cards 세로 |
| CompareMode | 비교 테이블 풀 너비 | 테이블 가로 스크롤 |
| SectorScreening | 섹터 버튼 flex-wrap | 동일 (자연스럽게 줄바꿈) |
| AIAnalysis | Bull/Bear 2열 | 1열 세로 배치 |
| Guide | 아코디언 풀 너비 | 동일 (이미 1열) |

### 설계 결정 사항

| 결정 | 이유 |
|------|------|
| CSS 미디어 쿼리 + JS hook 병행 | 레이아웃은 CSS, 조건부 렌더링은 JS hook |
| 사이드바 오버레이 (drawer) | 모바일에서 고정 사이드바는 화면 차지 과다 |
| TickerBar 모바일 3개 축소 | 6개 지수 모두 표시하면 가독성 저하 |
| Tailwind 미사용 (기존 인라인 스타일 유지) | 프로젝트 일관성, 추가 의존성 없음 |

---

## 구현 순서

```
Step 1: SQLite 영속화 (#3) → 데이터 레이어 안정화가 나머지 기능의 기반
Step 2: Watchlist 버튼 (#2) → SQLite 기반 Watchlist와 함께 구현
Step 3: 검색 자동완성 (#1) → 독립적 기능, 병렬 작업 가능
Step 4: 가격 알림 (#4) → SQLite price_alerts 테이블 + Watchlist UI 확장
Step 5: 반응형 레이아웃 (#5) → 모든 기능 완성 후 레이아웃 조정
```

---

## 선행 조건 및 의존성

- Phase 9 완료 (모든 화면 구현)
- Python 내장 `sqlite3` 모듈 (추가 설치 없음)
- 기존 `data/watchlist.py`, `data/theme_manager.py`의 인터페이스 유지

---

## 개발 시 주의사항

- SQLite 마이그레이션 시 기존 `config/*.json` 데이터 손실 방지 (백업 유지)
- `data/app.db`는 `.gitignore`에 추가 (사용자별 데이터)
- 반응형 작업은 모든 기능 완성 후 마지막에 수행 (레이아웃 변경이 다른 기능에 영향)
- 가격 알림 폴링은 앱 성능에 영향 최소화 (30초 간격, 백그라운드)
- 검색 자동완성 드롭다운은 z-index 관리 필요 (사이드바 내부)

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-14 | 최초 작성 — UX 개선 5개 항목 + SQLite 영속화 계획 |
| 2026-04-14 | ✅ 전체 구현 완료 — 5개 항목 모두 구현 + Koyeb/Netlify 배포 설정 |
