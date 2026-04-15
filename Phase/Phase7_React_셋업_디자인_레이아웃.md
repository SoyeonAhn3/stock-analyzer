# Phase 7 — React 셋업 + 디자인 시스템 + 레이아웃 `✅ 완료`

> React 프로젝트 생성, Dark/Light 테마 시스템, 사이드바, 라우팅, 하단 마켓 지수 바

**상태**: ✅ 완료
**선행 조건**: Phase 6 완료 (FastAPI 서버 동작 확인)
**기술 스택**: React, TypeScript, Vite, CSS Modules (또는 styled-components)
**디자인 권위 문서**: `pre-requirement/design-spec.md`

---

## 개요

React 프로젝트를 생성하고, design-spec.md의 디자인 토큰(색상, 폰트, 간격)을 TypeScript로 옮긴다. Dark/Light 테마 전환 시스템, 사이드바(검색+메뉴+Watchlist), 페이지 라우팅, 하단 마켓 지수 바를 구현한다. 이 Phase가 끝나면 **앱의 뼈대**가 완성된다.

### Streamlit 대비 변화
| Streamlit (이전) | React (현재) |
|-----------------|-------------|
| `screens/styles.py` → CSS 주입 | `theme/` → CSS 변수 + Context API |
| `screens/sidebar.py` → st.sidebar | `components/Sidebar.tsx` → 자유로운 HTML/CSS |
| `screens/state.py` → session_state | React Router + useState/Context |
| `st.rerun()` → 페이지 전체 새로고침 | 상태 변경 → 해당 부분만 업데이트 (깜빡임 없음) |

---

## 완료 예정 / 완료 항목

| # | 모듈 | 상태 | 설명 |
|---|---|---|---|
| 1 | `frontend/` 프로젝트 셋업 | ✅ | Vite + React + TypeScript 초기화 |
| 2 | `src/theme/` | ✅ | tokens.ts + dark.ts + light.ts + ThemeProvider.tsx |
| 3 | `src/components/Sidebar.tsx` | ✅ | 사이드바 (로고+검색+메뉴+Watchlist+AI Usage+Settings) |
| 4 | `src/App.tsx` + 라우팅 | ✅ | React Router 페이지 라우팅 |
| 5 | `src/components/TickerBar.tsx` | ✅ | 하단 마켓 지수 바 (6개 항목) |
| 6 | `src/hooks/useApi.ts` | ✅ | FastAPI 호출 공통 hook |
| 7 | `src/types/api.ts` | ✅ | API 응답 TypeScript 타입 정의 |
| 8 | `src/pages/Settings.tsx` | ✅ | Settings 화면 (테마 전환) |
| 9 | `src/config.ts` | ✅ | API Base URL 환경변수 설정 |
| 10 | `src/hooks/useBreakpoint.ts` | ✅ | 반응형 breakpoint hook (Phase 10 연계) |

---

## 프로젝트 구조

```
frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── src/
    ├── App.tsx                  앱 시작점 + 라우팅
    ├── main.tsx                 ReactDOM 렌더
    │
    ├── theme/                   디자인 시스템
    │   ├── tokens.ts            색상/폰트/간격 상수
    │   ├── dark.ts              다크 테마 객체
    │   ├── light.ts             라이트 테마 객체
    │   └── ThemeProvider.tsx    테마 Context + 전환 함수
    │
    ├── components/              재사용 가능한 UI 조각
    │   ├── Sidebar.tsx          사이드바
    │   ├── TickerBar.tsx        하단 마켓 지수 바
    │   ├── SearchInput.tsx      티커 검색창
    │   ├── MenuItem.tsx         메뉴 항목
    │   └── WatchlistItem.tsx    관심종목 항목
    │
    ├── hooks/                   데이터 호출 로직
    │   ├── useApi.ts            fetch 래퍼 (로딩/에러 처리)
    │   ├── useMarket.ts         시장 데이터 hook
    │   └── useWatchlist.ts      관심종목 hook
    │
    ├── pages/                   화면별 페이지
    │   ├── Settings.tsx         설정 화면
    │   └── (나머지는 Phase 8~9) 
    │
    ├── types/                   타입 정의
    │   └── api.ts               API 응답 인터페이스
    │
    └── styles/                  글로벌 CSS
        └── global.css           리셋 + 폰트 임포트
```

---

## 디자인 시스템 (theme/)

### tokens.ts — 디자인 토큰

design-spec.md 3~5장을 TypeScript 상수로 변환:

```typescript
// 폰트
export const FONTS = {
  body:    "'Inter', 'Pretendard', sans-serif",
  numeric: "'JetBrains Mono', 'IBM Plex Mono', monospace",
} as const

// 폰트 크기
export const FONT_SIZES = {
  xs: "11px", sm: "13px", md: "14px", lg: "16px",
  xl: "20px", "2xl": "24px", "3xl": "32px", "4xl": "40px",
} as const

// 간격
export const SPACING = {
  xs: "4px", sm: "8px", md: "16px", lg: "24px", xl: "32px", "2xl": "48px",
} as const

// 보더 라디우스
export const RADIUS = {
  card: "8px", button: "6px", badge: "4px", pill: "9999px",
} as const
```

### dark.ts / light.ts — 테마 객체

```typescript
// dark.ts
export const darkTheme = {
  bg_primary:    "#0B1020",
  bg_card:       "#151B2E",
  bg_card_hover: "#1C2540",
  border:        "#1F2937",
  text_primary:  "#E4E7EB",
  text_secondary:"#94A3B8",
  text_muted:    "#64748B",
  accent:        "#00D4FF",
  accent_hover:  "#22E0FF",
  up:            "#10B981",
  down:          "#EF4444",
  warning:       "#F59E0B",
}

// light.ts
export const lightTheme = {
  bg_primary:    "#F8FAFC",
  bg_card:       "#FFFFFF",
  // ... design-spec.md 3장 참조
}
```

### ThemeProvider.tsx — 테마 전환

```typescript
// React Context로 앱 전체에 테마 공급
const ThemeContext = createContext(...)

export function ThemeProvider({ children }) {
  const [mode, setMode] = useState<"dark" | "light">("dark")
  const theme = mode === "dark" ? darkTheme : lightTheme

  const toggleTheme = () => setMode(m => m === "dark" ? "light" : "dark")

  return (
    <ThemeContext.Provider value={{ theme, mode, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

// 어디서든 사용:
// const { theme, toggleTheme } = useTheme()
```

---

## 사이드바 (Sidebar.tsx)

### 구현 내용 (design-spec.md 6-1장)

```
┌──────────────────────┐
│  🔷 QuantAI           │  1. 로고
│  Institutional Grade  │
│                       │
│  🔍 [ 티커 검색 ]     │  2. 검색창
│                       │
│  ● Market Overview    │  3. 메뉴 5개
│    Quick Look         │
│    Compare Mode       │
│    Sector Screening   │
│    Beginner's Guide   │
│                       │
│  REAL-TIME WATCHLIST  │  4. Watchlist
│  AAPL      +1.24%    │     API: GET /api/watchlist
│  TSLA      -0.82%    │
│                       │
│  AI USAGE    47/100   │  5. AI 사용량
│  ━━━━━━●━━━━━━━━      │
│  ⚙ Settings           │  6. Settings 링크
└──────────────────────┘
```

### Streamlit 대비 장점
- 메뉴 hover 시 부드러운 애니메이션
- Watchlist 클릭 시 사이드바 유지, 메인만 전환 (깜빡임 없음)
- 검색 시 자동완성 가능 (나중에 추가)
- 240px 고정 폭, CSS로 완전 커스텀

### 데이터 연동
| 영역 | API 호출 | 주기 |
|------|---------|------|
| Watchlist | `GET /api/watchlist` | 60초 폴링 |
| AI Usage | 로컬 state (서버 불필요) | - |

---

## 라우팅 (App.tsx)

React Router로 URL ↔ 화면 매핑:

```typescript
<Routes>
  <Route path="/"              element={<MarketOverview />} />
  <Route path="/quick-look/:ticker" element={<QuickLook />} />
  <Route path="/compare"       element={<CompareMode />} />
  <Route path="/sector"        element={<SectorScreening />} />
  <Route path="/guide"         element={<Guide />} />
  <Route path="/settings"      element={<Settings />} />
</Routes>
```

### Streamlit 대비 장점
- URL로 직접 이동 가능 (예: `/quick-look/NVDA` 북마크)
- 브라우저 뒤로가기 지원
- 페이지 새로고침 없이 전환

---

## 하단 마켓 지수 바 (TickerBar.tsx)

모든 페이지 하단에 상시 표시:

```
SPY ↗ 4,892.12 (+0.45%)  QQQ ↗ 425.80 (+1.12%)  DIA → 38,150.30 (-0.02%)
BTC ₿ 64,250.00 (+2.15%)  ETH ⬨ 3,450.12 (+0.85%)  VIX ▲ 12.45 (+1.42%)
```

- API: `GET /api/market/indices`
- 60초마다 자동 갱신
- 가로 스크롤 (CSS overflow-x)

---

## API 호출 공통 Hook (useApi.ts)

모든 API 호출에서 반복되는 로딩/에러 처리를 한 곳에서 관리:

```typescript
function useApi<T>(url: string) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch(url)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [url])

  return { data, loading, error }
}

// 사용 예:
const { data, loading } = useApi<QuoteResponse>("/api/quote/NVDA")
```

---

## Settings 화면 (Settings.tsx)

```
┌─────────────────────────────────────────┐
│  ⚙ Settings                              │
│                                          │
│  THEME                                   │
│  [● Dark]  [○ Light]                     │  ← 클릭 즉시 전환
│                                          │
│  AI USAGE                                │
│  Today: 47 / 100                         │
│  ━━━━━━━━━━●━━━━━━━━━                    │
│                                          │
│  DISCLAIMER                              │
│  AI-generated reference only.            │
│  Not financial advice.                   │
└─────────────────────────────────────────┘
```

---

## 선행 조건 및 의존성

- Phase 6: FastAPI 서버가 `localhost:8000`에서 동작
- Node.js 18+, npm
- npm 패키지: `react`, `react-router-dom`, `typescript`, `vite`
- Google Fonts: Inter, JetBrains Mono

---

## 실행 방법

```bash
# 프로젝트 생성
npm create vite@latest frontend -- --template react-ts

# 의존성 설치
cd frontend && npm install react-router-dom

# 개발 서버 실행
npm run dev    # → localhost:3000

# 동시에 백엔드도 실행 중이어야 함
# uvicorn backend.main:app --reload --port 8000
```

---

## 개발 시 주의사항

- design-spec.md를 디자인 권위 문서로 참조
- 모든 숫자는 `FONTS.numeric` (JetBrains Mono) 사용
- 주가 외 요소에 up/down 색상 사용 금지
- 사이드바 폭 240px 고정
- Phase 8~9에서 만들 페이지 자리는 빈 placeholder로 남겨둠

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-06 | 최초 작성 (Streamlit Quick Look + AI 결과 UI) |
| 2026-04-14 | React 전환 — 프로젝트 셋업 + 디자인 시스템 + 레이아웃으로 전면 재작성 |
| 2026-04-14 | ✅ 구현 완료 — theme/ 4파일 + Sidebar + TickerBar + App 라우팅 + Settings + config.ts |
