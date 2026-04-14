# AI Stock Analyzer - Design Specification

> React + FastAPI 구현을 위한 디자인 스펙 문서  
> Dark Mode / Light Mode 동시 지원 (Settings에서 전환)

---

## 1. 프로젝트 컨셉

**"Calm Intelligence"** — 차분하지만 똑똑해 보이는 금융 대시보드

- Bloomberg Terminal 스타일에서 영감
- 데이터 밀도는 높지만 시각적으로 차분함
- 장난스럽거나 화려하지 않음 — 신뢰감과 전문성 우선
- AI Agent가 분석하는 제품이므로 "데이터가 말하게" 하는 디자인

---

## 2. 테마 구조

### Dark / Light 동시 지원
- 기본값: Dark Mode
- Settings에서 Dark ↔ Light 전환 가능
- 색 토큰 교체 방식 — 레이아웃/컴포넌트 동일, 색상만 스왑
- session_state 기반 테마 상태 관리

---

## 3. Color Tokens

### Dark Mode (기본)

```python
DARK_COLORS = {
    # 배경
    "bg_primary":    "#0B1020",  # 메인 배경 (가장 어두운 네이비)
    "bg_card":       "#151B2E",  # 카드 배경
    "bg_card_hover": "#1C2540",  # 카드 호버 상태
    
    # 보더
    "border":        "#1F2937",  # 기본 보더
    
    # 텍스트
    "text_primary":   "#E4E7EB",  # 주요 텍스트 (순백 아님, 눈 피로 줄임)
    "text_secondary": "#94A3B8",  # 보조 텍스트, 라벨
    "text_muted":     "#64748B",  # 흐린 텍스트, 캡션
    
    # 강조
    "accent":       "#00D4FF",  # 시안 — AI 느낌, 브랜드 컬러
    "accent_hover": "#22E0FF",
    
    # 주가 관련 (오직 주가 숫자에만 사용)
    "up":      "#10B981",  # 상승 — 부드러운 초록
    "down":    "#EF4444",  # 하락 — 부드러운 빨강
    "warning": "#F59E0B",  # 경고, 중립 — 주황
}
```

### Light Mode

```python
LIGHT_COLORS = {
    "bg_primary":    "#F8FAFC",  # 순백 아님! 살짝 회색 섞인 흰색
    "bg_card":       "#FFFFFF",
    "bg_card_hover": "#F1F5F9",
    "border":        "#E2E8F0",
    "text_primary":   "#0F172A",
    "text_secondary": "#64748B",
    "text_muted":     "#94A3B8",
    "accent":       "#0284C7",  # 다크의 시안 대신 진한 파랑
    "accent_hover": "#0369A1",
    "up":      "#059669",
    "down":    "#DC2626",
    "warning": "#D97706",
}
```

**중요 원칙**: 상승/하락 색상은 **오직 주가 관련 숫자에만** 사용. 일반 성공/에러 메시지에는 쓰지 않음.

---

## 4. Typography

```python
FONTS = {
    "body":    "'Inter', 'Pretendard', sans-serif",      # 본문, UI 텍스트
    "numeric": "'JetBrains Mono', 'IBM Plex Mono', monospace",  # 모든 숫자
    "heading": "'Inter', 'Pretendard', sans-serif",      # 제목 (Bold)
}

FONT_SIZES = {
    "xs":  "11px",   # 캡션, 라벨
    "sm":  "13px",   # 보조 텍스트
    "md":  "14px",   # 본문
    "lg":  "16px",   # 강조 본문
    "xl":  "20px",   # 소제목
    "2xl": "24px",   # 섹션 제목
    "3xl": "32px",   # 주요 가격
    "4xl": "40px",   # 히어로 숫자
}
```

**필수 규칙**: 
- 모든 **숫자**(가격, 퍼센트, 시가총액, PE 등)는 **monospace 폰트** 사용 → 자릿수 정렬
- 텍스트는 Inter, 숫자는 JetBrains Mono로 엄격히 분리

---

## 5. Spacing & Layout

### 간격 (8px 기준)

```python
SPACING = {
    "xs":  "4px",
    "sm":  "8px",
    "md":  "16px",
    "lg":  "24px",
    "xl":  "32px",
    "2xl": "48px",
}
```

### Border Radius

```python
RADIUS = {
    "card":   "8px",   # 카드, 패널
    "button": "6px",   # 버튼
    "badge":  "4px",   # 배지, 태그
    "pill":   "9999px" # 원형 배지
}
```

### 전체 캔버스

- **기준 해상도**: 1440 × 900 (데스크톱 기준)
- **사이드바 폭**: 240px 고정
- **메인 영역**: 남은 공간 flex
- **내부 여백**: 24px
- **카드 간격**: 16px

---

## 6. Layout Structure — Quick Look 화면

### 6-1. 사이드바 (좌측, 240px 고정)

위에서 아래 순서:
1. **로고 영역**
   - `QuantAI` 로고 (accent color)
   - "Institutional Grade" 태그라인 (text_secondary, 작게)
2. **티커 검색창** (최상단 배치)
   - Enter로 검색 → Quick Look 화면 자동 진입
   - 유효하지 않은 티커면 힌트 표시
3. **메인 메뉴** (선택 시 왼쪽에 accent 바)
   - Market Overview (기본 선택)
   - Quick Look
   - Compare Mode
   - Sector Screening
   - Beginner's Guide
4. **REAL-TIME WATCHLIST** 섹션
   - 섹션 제목 (text_muted, xs)
   - 종목 리스트 (AAPL, TSLA, AMD 등)
   - 각 항목: 티커 + 등락률 (up/down 색상)
   - 클릭 → Quick Look 화면 진입
5. **하단 고정 영역**
   - AI Usage 카운터: `47/100` + 프로그레스 바
   - Settings 링크 (클릭 시 Settings 패널 열림)

### 6-2. 메인 헤더 영역

**상단 한 줄**: Breadcrumb
```
EQUITIES › TECHNOLOGY › SEMICONDUCTORS
```
- text_muted 색상
- 마지막 항목(현재 위치)만 accent color

**그 아래 두 영역 분할**:

**왼쪽 (종목 정보)**:
```
[NVDA 배지] [NASDAQ 배지]  NVIDIA Corp
$142.50   +2.3% (+$3.21)
```
- NVDA: 티커 배지 (회색 배경, 중간 크기)
- NASDAQ: 거래소 배지 (회색 배경)
- NVIDIA Corp: 회사명 (xl, 굵게)
- $142.50: 가격 (4xl, monospace, 굵게)
- +2.3% (+$3.21): 등락 (lg, up 색상, monospace)

**오른쪽 (보조 지표)**:
```
52W RANGE                  VOLUME (24H)   [Data Delayed ~15 min]
$40.22 ━●━ $145.76         342.1M         [🔔 알림] [👤 프로필]
```
- 52W Range: 라벨 + 슬라이더 + 값 (monospace)
- Volume: 라벨 + 값 (monospace)
- Data Delayed 배지: 주황/경고 색상으로 눈에 띄게
- 알림/프로필 아이콘

### 6-3. KPI 카드 4개 (가로 배치)

각 카드 구조:
```
MARKET CAP            ← 라벨 (text_secondary, xs, 대문자)
$3.52T                ← 값 (2xl, monospace, 굵게)
```

4개 카드 (현재 데이터에서 가져올 수 있는 값만 사용):
1. **MARKET CAP** — `$3.52T`
2. **P/E RATIO (TTM)** — `35.24`
3. **EPS (DILUTED)** — `$4.05`
4. **FORWARD P/E** — `28.12`

> 보조 정보(Sector Rank, Hist PE Avg, Beat Expected, Projected Growth)는
> 추가 API 소스 확보 후 별도 업데이트 예정. 현재는 메인 값만 표시.

### 6-4. 차트 영역 (메인, 왼쪽 넓게)

- **시간프레임 탭**: `1D / 1W / 1M / 3M / 6M / 1Y / 5Y`
  - 선택된 탭은 accent 배경
- **범례**: `— MA(50)` (accent) / `— MA(200)` (warning)
- **메인 차트**: 캔들스틱
  - 상승 캔들: up 색상
  - 하락 캔들: down 색상
  - MA50 라인: accent 색상
  - MA200 라인: warning 색상
  - 현재가 라벨: `142.50` 오른쪽 끝에 accent 배경 배지
- **볼륨 바**: 차트 하단 별도 영역
  - "VOLUME" 라벨 (text_secondary, xs)
  - 캔들 색과 매칭 (상승날은 up, 하락날은 down)

### 6-5. 기술 지표 3개 카드 (우측 세로 스택)

**카드 1 — RSI (14)**
```
RSI (14)                    ●   ← 상태 점 (bullish=green, bearish=red, neutral=gray)
62.4       NEUTRAL-BULL
━━━●━━━                         ← 게이지 바 (0~100 범위)
```

**카드 2 — MACD**
```
MACD                        ●
HISTOGRAM
Positive  ▂▄▆█               ← 히스토그램 값 기반 미니 차트
```
- histogram > 0: "Positive" (up 색상) / histogram < 0: "Negative" (down 색상)

**카드 3 — BOLLINGER BANDS**
```
BOLLINGER BANDS             ●
Upper              148.12
Middle             141.05    ← 현재가에 가장 가까운 값은 accent로 강조
Lower              133.98
```

### 6-6. AI Recommendation 카드 (하단 전체 폭)

```
[🧠 아이콘]  AI Recommendation   [BUY 배지]              CONFIDENCE
             NVDA is showing strong structural          high
             support at the $140 level...               (accent, 2xl)
```

- 왼쪽 아이콘 (accent 원형 배경)
- 중앙 제목 + 판정 배지 + 본문
  - 판정: **BUY** (up) / **HOLD** (warning) / **SELL** (down) — 3단계
- 우측 Confidence (텍스트: high / medium / low)
  - 배지 색상: high=accent, medium=warning, low=text_muted

### 6-7. 마켓 지수 바 (최하단 전체 폭)

```
SPY ↗ 4,892.12 (+0.45%)  QQQ ↗ 425.80 (+1.12%)  DIA → 38,150.30 (-0.02%)  
BTC ₿ 64,250.00 (+2.15%)  ETH ⬨ 3,450.12 (+0.85%)  VIX ▲ 12.45 (+1.42%)
```

- 한 줄, 스크롤 가능
- 각 항목: 심볼 + 값 + 등락률 (up/down 색상)
- 구분선: 얇은 세로 라인 (border 색상)
- 데이터 소스: `get_market_indices()` — SPY(S&P 500), QQQ(NASDAQ), DIA(DOW), BTC, ETH, VIX

---

## 7. Style Principles

### 시각적 원칙
- **카드 구분**: Dark=1px 보더, Light=subtle box-shadow
- **여백**: 8의 배수로 엄격히 유지 (4, 8, 16, 24, 32, 48)
- **숫자 정렬**: 모든 테이블/리스트의 숫자는 우측 정렬 + monospace
- **대문자 라벨**: 섹션 라벨은 UPPERCASE + letter-spacing 0.05em

### 금지 사항
- 이모지 사용 금지 (대신 Lucide 아이콘)
- 그라데이션 배경 (Bloomberg 스타일은 솔리드)
- 화려한 애니메이션 (hover만 subtle하게)
- 순백색 텍스트 `#FFFFFF` (대신 `#E4E7EB`)
- 주가 외 요소에 초록/빨강 사용

### 권장 사항
- 카드 hover 시 border 색상만 살짝 밝게
- 숫자 업데이트 시 짧은 flash 애니메이션 (200ms)
- 로딩 상태는 skeleton UI (spinner보다)
- 에러는 주황색 warning, 빨강 아님

---

## 8. Settings 패널

### 진입 방식
- 사이드바 최하단 Settings 링크 클릭 → `/settings` 페이지로 이동
- React Router로 라우팅

### 설정 항목

**1. 테마 전환**
- Dark Mode / Light Mode 토글 (또는 라디오 버튼)
- 선택 즉시 반영 (React 상태 업데이트, 새로고침 없음)
- React Context에 저장

**2. AI 사용량 리셋 정보**
- 현재 사용량 / 일일 한도 표시
- 다음 리셋 시간

**3. 면책 조항**
- "AI-generated reference. Not financial advice." 전문

### 테마 전환 구현 구조

```typescript
// React Context API
const ThemeContext = createContext(...)

function ThemeProvider({ children }) {
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

## 9. 구현 우선순위 (Phase별)

### Phase 6 — FastAPI 백엔드
1. FastAPI 앱 + CORS 설정
2. API 엔드포인트 ~15개 (기존 함수 감싸기)
3. Pydantic 모델 정의
4. `/docs` 자동 문서로 전체 테스트

### Phase 7 — React 셋업 + 레이아웃
1. Vite + React + TypeScript 프로젝트 생성
2. 디자인 토큰 (`theme/tokens.ts`, `dark.ts`, `light.ts`)
3. ThemeProvider (Context API)
4. 레이아웃 뼈대 (사이드바 240px + 메인 flex)
5. 사이드바 (검색 + 메뉴 5개 + Watchlist + Settings)
6. React Router 페이지 라우팅
7. 하단 마켓 지수 바
8. Settings 화면 (테마 전환)
9. API 호출 공통 hook

### Phase 8 — Quick Look + AI 분석
1. 시세 헤더 (PriceHeader)
2. KPI 카드 4개
3. 캔들스틱 차트 + MA + 볼륨
4. 기술 지표 카드 3개 (RSI, MACD, Bollinger)
5. AI Recommendation 카드
6. AI 분석 결과 화면 (Agent 진행 + 판정)

### Phase 9 — 나머지 + 통합
1. Market Overview (급등락 + 뉴스)
2. Sector Screening
3. Compare Mode
4. Beginner's Guide
5. 에러/로딩 공통 컴포넌트
6. 전체 시나리오 테스트

---

## 10. Plotly 차트 상세 스펙

### Dark Mode

```python
PLOTLY_DARK = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor":  "rgba(0,0,0,0)",
        "font": {
            "family": "JetBrains Mono",
            "color":  "#94A3B8",
            "size":   11,
        },
        "xaxis": {
            "gridcolor": "#1F2937",
            "linecolor": "#1F2937",
            "zeroline":  False,
        },
        "yaxis": {
            "gridcolor": "#1F2937",
            "linecolor": "#1F2937",
            "zeroline":  False,
        },
        "margin": {"t": 10, "r": 10, "b": 30, "l": 50},
    },
    "candlestick": {
        "increasing": {"line": {"color": "#10B981"}, "fillcolor": "#10B981"},
        "decreasing": {"line": {"color": "#EF4444"}, "fillcolor": "#EF4444"},
    },
    "ma_lines": {
        "ma50":  {"color": "#00D4FF", "width": 2},
        "ma200": {"color": "#F59E0B", "width": 2},
    },
}
```

### Light Mode

```python
PLOTLY_LIGHT = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor":  "rgba(0,0,0,0)",
        "font": {
            "family": "JetBrains Mono",
            "color":  "#64748B",
            "size":   11,
        },
        "xaxis": {
            "gridcolor": "#E2E8F0",
            "linecolor": "#E2E8F0",
            "zeroline":  False,
        },
        "yaxis": {
            "gridcolor": "#E2E8F0",
            "linecolor": "#E2E8F0",
            "zeroline":  False,
        },
        "margin": {"t": 10, "r": 10, "b": 30, "l": 50},
    },
    "candlestick": {
        "increasing": {"line": {"color": "#059669"}, "fillcolor": "#059669"},
        "decreasing": {"line": {"color": "#DC2626"}, "fillcolor": "#DC2626"},
    },
    "ma_lines": {
        "ma50":  {"color": "#0284C7", "width": 2},
        "ma200": {"color": "#D97706", "width": 2},
    },
}
```

---

## 11. Reference Images

- `Stock Analyzer UI.png` — 다크 모드 Quick Look 화면 레퍼런스

---

## 12. 화면별 스펙 범위

이 문서는 **Quick Look 화면**의 레이아웃 + 디자인 토큰을 정의한다.
아래 화면들은 동일한 디자인 토큰/레이아웃 뼈대를 공유하며, 메인 콘텐츠 영역만 다르다:

| 화면 | 메인 콘텐츠 | Phase |
|------|-----------|:-----:|
| Market Overview | 지수 카드 + 급등락 + 뉴스 | 8 |
| Quick Look | 헤더 + KPI + 차트 + 기술지표 + AI 추천 | 7 |
| AI Deep Analysis | Agent 진행 상태 + BUY/HOLD/SELL 판정 카드 | 7 |
| Sector Screening | 섹터 그리드 + 필터 + Top 5 결과 | 8 |
| Compare Mode | 비교 바 + 테이블 + 수익률 차트 + AI 비교 | 8 |
| Beginner's Guide | 카테고리 펼치기/접기 + 난이도 뱃지 | 8 |
| Settings | 테마 전환 + AI 사용량 + 면책 조항 | 6 |

공통 요소 (모든 화면에 표시):
- 사이드바 (검색 + 메뉴 + Watchlist + AI Usage + Settings)
- 하단 마켓 지수 바

---

## 부록: 데이터-UI 매핑 참조

### Quick Look 화면에서 사용하는 데이터 함수

| UI 요소 | 데이터 함수 | 반환 필드 |
|---------|-----------|----------|
| 가격/등락 | `get_quote()` | price, change, change_percent, volume |
| 52W Range | `get_fundamentals()` | week52_high, week52_low |
| Breadcrumb | `get_fundamentals()` | sector, industry |
| KPI 카드 | `get_fundamentals()` | market_cap, pe, eps, forward_pe |
| 차트 | `get_history()` | OHLCV + MA50/MA200 |
| RSI | `get_technicals()` | rsi.value, rsi.signal |
| MACD | `get_technicals()` | macd.histogram, macd.signal |
| Bollinger | `get_technicals()` | bollinger.upper/middle/lower, bollinger.signal |
| AI 추천 | `analyst_agent.run()` | verdict (BUY/HOLD/SELL), confidence, summary |
| 하단 지수 바 | `get_market_indices()` | SPY, QQQ, DIA, BTC, ETH, VIX |

---

*이 문서는 살아있는 문서입니다. 구현하면서 발견되는 사항을 계속 업데이트하세요.*
