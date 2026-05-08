# Phase 5 — Compare + Watchlist + Guide + Overview `✅ Completed`

> Complete all remaining data logic. UI rendering is separated into later phases.

**Completed**: 2026-04-14
**Status**: ✅ Completed
**Prerequisites**: Phase 4 completed

---

## Overview

Develop data logic for Compare Mode (comparison type detection, investment style classification, AI comparison analysis), Watchlist (ticker management, change rate polling), Beginner's Guide (content data), and Market Overview (indices, movers, news). All modules are pure Python with no UI framework dependency. Screen rendering and state management are handled in later phases.

---

## Deliverables

| # | Module | Status | Type |
|---|---|---|---|
| 1 | `data/compare.py` | ✅ | project-specific |
| 2 | `data/style_classifier.py` | ✅ | project-specific |
| 3 | `agents/compare_agent.py` | ✅ | project-specific |
| 4 | `data/watchlist.py` | ✅ | project-specific |
| 5 | `data/guide_content.py` | ✅ | project-specific |
| 6 | `data/market_overview.py` | ✅ | project-specific |

---

## Compare Mode — Type Detection (compare.py)

### Purpose
Auto-detect whether 2–3 tickers are in the same sector or different sectors.

### Implementation Files
- `data/compare.py`

### Core Structure

```python
def detect_comparison_type(tickers: list[str]) -> str:
    """
    4-step detection:
    1. Get sector + industry for each ticker (Quick Look reuse)
    2. Different sectors → "cross_sector"
    3. Same sector + same industry → "same_sector"
    4. Same sector + different industry → check related_industries.json
       Related → "same_sector", Not related → "cross_sector"
    
    Returns: "same_sector" | "cross_sector"
    """

def get_comparison_data(tickers: list[str]) -> dict:
    """Return Fundamentals + Technicals side by side for 2–3 tickers"""
```

### Design Decisions

| Decision | Reason |
|---|---|
| Unknown combinations default to "cross_sector" | Safer fallback — cross-sector analysis is more general |
| Empty sector/industry → "Unknown" → "cross_sector" | Prevent false same-sector classification |
| Reuse Quick Look sector/industry data | No additional API calls needed |

---

## Compare Mode — Style Classifier (style_classifier.py)

### Purpose
Classify each ticker as Growth / Value / Balanced.

### Implementation Files
- `data/style_classifier.py`

### Core Structure

```python
def classify_style(ticker_data: dict) -> str:
    """
    Classification order (important):
    1. Growth check: revenue growth >= 20% AND Forward PE >= 25
    2. Value check: Forward PE < 18 AND (dividend >= 2% OR PBR < 1.5)
    3. Default: Balanced
    
    Returns: "Growth" | "Value" | "Balanced"
    """
```

### Classification Criteria

| Metric | Growth | Value | Balanced |
|---|---|---|---|
| Revenue Growth (YoY) | 20%+ | < 10% | 10–20% |
| Forward P/E | 25+ | < 18 | 18–25 |
| Dividend Yield | < 0.5% | 2%+ | 0.5–2% |

### Design Decisions

| Decision | Reason |
|---|---|
| Growth check runs first | When growth is dominant, high PE is acceptable |
| Code does 1st-pass classification, AI adds context | Separation of concerns — deterministic rules + AI judgment |

---

## Compare Mode — AI Analysis (compare_agent.py)

### Purpose
Run AI comparison analysis with different prompts based on comparison type.

### Implementation Files
- `agents/compare_agent.py`

### Core Structure

```python
def run_compare_analysis(tickers: list, comparison_type: str,
                         ticker_data: dict) -> dict:
    """Single Claude call. Only the prompt differs by type."""
```

### Prompt Branching

**same_sector**: Direct comparison
- Category rankings (growth, valuation, financial health, technical position)
- Key Risks per ticker
- Recommendation by investor style (Growth/Value/Balanced)
- Blind spots

**cross_sector**: Relative comparison
- Sector context (each ticker's key drivers)
- Valuation vs own sector average
- Sector-neutral metrics (FCF yield, ROE, D/E)
- Macro scenario reactions (rate hold, recession)
- Portfolio diversification perspective
- Recommendation by investor style + blind spots

---

## Watchlist (watchlist.py)

### Purpose
Manage watched tickers + retrieve change rates.

### Implementation Files
- `data/watchlist.py`

### Core Structure

```python
def load_watchlist() -> list[str]
def add_to_watchlist(ticker: str) -> None
def remove_from_watchlist(ticker: str) -> None
def get_watchlist_quotes(watchlist: list) -> list[dict]:
    """Return current price + change rate for each ticker"""
def save_watchlist_to_file(watchlist: list) -> None:
    """Persistent JSON save (optional)"""
```

### Design Decisions

| Decision | Reason |
|---|---|
| Data logic only — no session_state | UI integration is in later phases |
| ±5% threshold: `abs(change_percent) >= 5.0` → `highlight: True` | Alert the user to significant movers |

---

## Beginner's Guide (guide_content.py)

### Purpose
Manage guide content as a dictionary.

### Implementation Files
- `data/guide_content.py`

### Core Structure

```python
GUIDE_CONTENT = {
    "chart_basics": {
        "category": "Chart Basics",
        "topics": [
            {
                "title": "Candlestick Chart",
                "level": "beginner",
                "what": "...", "how": "...", "when": "...", "example": "..."
            },
        ]
    },
    "key_metrics": { ... },
    "technicals": { ... },
    "market_concepts": { ... },
    "investment_styles": { ... }
}
```

### Design Decisions

| Decision | Reason |
|---|---|
| Static content, no API calls | Instant response, zero cost |
| 5 categories | Chart, Key Metrics, Technicals, Market Concepts, Investment Styles |
| 3 difficulty levels | beginner / intermediate / advanced |
| What → How → When → Example structure | Progressive learning flow |

---

## Market Overview (market_overview.py)

### Purpose
Collect market indices, top movers, and news headlines.

### Implementation Files
- `data/market_overview.py`

### Core Structure

```python
def get_market_indices() -> list[dict]:
    """S&P 500, NASDAQ, DOW, BTC, ETH, VIX → price + change rate"""

def get_top_movers() -> dict:
    """Top 5 gainers + Top 5 losers"""

def get_market_news(limit=5) -> list[dict]:
    """News headlines (Finnhub News)"""
```

### Design Decisions

| Decision | Reason |
|---|---|
| yfinance: ^GSPC, ^IXIC, ^DJI, ^VIX, BTC-USD, ETH-USD | Broad market coverage including crypto |
| Finnhub for movers and news | Real-time data with free tier |

---

## Phase 5 Skill Classification

| Skill | Classification | Reason |
|---|---|---|
| compare | project-specific | Stock comparison type detection |
| style_classifier | project-specific | Investment style classification |
| compare_agent | project-specific | AI comparison analysis |
| watchlist | project-specific | Watchlist CRUD |
| guide_content | project-specific | Static educational content |
| market_overview | project-specific | Market data aggregation |

---

## Prerequisites & Dependencies

- Phase 2: Quick Look data functions (quote, fundamentals, technicals)
- Phase 3: Claude call structure (for compare_agent)
- `config/related_industries.json` must exist

---

## Development Notes

- No UI framework code in this Phase — pure functions/classes only
- Screen transition logic (session_state.mode management) moved to Phase 6+
- compare.py sector/industry field names must match Phase 2 fundamentals output
- AI comparison uses 1 call; same_sector uses fewer tokens, cross_sector uses more

---

## Change Log

| Date | Description |
|---|---|
| 2026-04-06 | Initial creation |
| 2026-04-13 | Phase 5 implementation complete — 6 modules, tests passed |
| 2026-04-14 | Status updated to ✅ Completed. BTC/ETH added to market_overview |

---
---

# Phase 5 — Compare + Watchlist + Guide + Overview `✅ 완료`

> 나머지 기능의 데이터 로직 전부 완성. UI 렌더링은 이후 Phase로 분리.

**완료일**: 2026-04-14
**상태**: ✅ 완료
**선행 조건**: Phase 4 완료

---

## 개요

Compare Mode(비교 유형 판정, 투자 스타일 분류, AI 비교 분석), Watchlist(종목 관리, 등락률 조회), Beginner's Guide(콘텐츠 데이터), Market Overview(지수, 급등락, 뉴스)의 **데이터 로직만** 개발한다. 화면 렌더링과 상태 관리는 이후 Phase에서 처리한다.

---

## 완료 항목

| # | 모듈 | 상태 | 스킬 타입 |
|---|---|---|---|
| 1 | `data/compare.py` | ✅ | project-specific |
| 2 | `data/style_classifier.py` | ✅ | project-specific |
| 3 | `agents/compare_agent.py` | ✅ | project-specific |
| 4 | `data/watchlist.py` | ✅ | project-specific |
| 5 | `data/guide_content.py` | ✅ | project-specific |
| 6 | `data/market_overview.py` | ✅ | project-specific |

---

## Compare Mode — 비교 유형 판정 (compare.py)

### 목적
2~3 종목이 같은 섹터인지 다른 섹터인지 자동 감지한다.

### 구현 파일
- `data/compare.py`

### 핵심 구조

```python
def detect_comparison_type(tickers: list[str]) -> str:
    """
    4단계 판정:
    1. 각 티커의 sector + industry 가져옴 (Quick Look 재사용)
    2. sector 다르면 → "cross_sector"
    3. sector + industry 전부 같으면 → "same_sector"
    4. sector 같고 industry 다르면 → related_industries.json 참조
       관련 업종이면 "same_sector", 아니면 "cross_sector"
    
    반환: "same_sector" | "cross_sector"
    """

def get_comparison_data(tickers: list[str]) -> dict:
    """2~3 종목의 Fundamentals + Technicals 나란히 반환"""
```

### 설계 결정 사항

| 결정 | 이유 |
|---|---|
| 미등록 조합은 기본값 "cross_sector" | 안전한 폴백 — cross_sector 분석이 더 범용적 |
| 빈 sector/industry → "Unknown" → "cross_sector" | 잘못된 same_sector 분류 방지 |
| Quick Look의 sector/industry 데이터 재사용 | 추가 API 호출 불필요 |

---

## Compare Mode — 투자 스타일 분류 (style_classifier.py)

### 목적
각 종목을 Growth / Value / Balanced로 분류한다.

### 구현 파일
- `data/style_classifier.py`

### 핵심 구조

```python
def classify_style(ticker_data: dict) -> str:
    """
    분류 순서 (중요):
    1. Growth 체크: 매출 성장률 >= 20% AND Forward PE >= 25
    2. Value 체크: Forward PE < 18 AND (배당 >= 2% OR PBR < 1.5)
    3. 기본값: Balanced
    
    반환: "Growth" | "Value" | "Balanced"
    """
```

### 분류 기준표

| 지표 | Growth | Value | Balanced |
|---|---|---|---|
| 매출 성장률 (YoY) | 20%+ | < 10% | 10~20% |
| Forward P/E | 25+ | < 18 | 18~25 |
| 배당 수익률 | < 0.5% | 2%+ | 0.5~2% |

### 설계 결정 사항

| 결정 | 이유 |
|---|---|
| Growth 체크를 먼저 수행 | 성장이 압도적이면 PE가 높아도 Growth |
| 코드가 1차 분류, AI가 맥락 보정 | 결정적 규칙 + AI 판단의 분리 |

---

## Compare Mode — AI 비교 분석 (compare_agent.py)

### 목적
비교 유형에 따라 다른 프롬프트로 AI 비교 분석을 수행한다.

### 구현 파일
- `agents/compare_agent.py`

### 핵심 구조

```python
def run_compare_analysis(tickers: list, comparison_type: str,
                         ticker_data: dict) -> dict:
    """AI 1회 호출. 프롬프트만 다름."""
```

### 프롬프트 분기

**same_sector**: 직접 비교
- 카테고리별 순위 (성장성, 밸류에이션, 재무 건전성, 기술적 포지션)
- Key Risks (종목별)
- 투자 성향별 추천 (Growth/Value/Balanced)
- Blind spots

**cross_sector**: 상대 비교
- 섹터 맥락 (각 종목의 핵심 드라이버)
- 밸류에이션: 자기 섹터 평균 대비
- 섹터 무관 지표 (FCF yield, ROE, D/E)
- 매크로 시나리오별 반응 (금리 유지, 경기 침체)
- 포트폴리오 분산 관점
- 투자 성향별 추천 + Blind spots

---

## Watchlist (watchlist.py)

### 목적
관심 종목 관리 + 등락률 조회.

### 구현 파일
- `data/watchlist.py`

### 핵심 구조

```python
def load_watchlist() -> list[str]
def add_to_watchlist(ticker: str) -> None
def remove_from_watchlist(ticker: str) -> None
def get_watchlist_quotes(watchlist: list) -> list[dict]:
    """각 종목의 현재가 + 등락률 반환"""
def save_watchlist_to_file(watchlist: list) -> None:
    """JSON 영구 저장 (선택)"""
```

### 설계 결정 사항

| 결정 | 이유 |
|---|---|
| 데이터 로직만 — session_state 없음 | UI 연동은 이후 Phase에서 처리 |
| ±5% 판정: `abs(change_percent) >= 5.0` → `highlight: True` | 급변동 종목을 사용자에게 알림 |

---

## Beginner's Guide (guide_content.py)

### 목적
가이드 콘텐츠를 딕셔너리로 관리한다.

### 구현 파일
- `data/guide_content.py`

### 핵심 구조

```python
GUIDE_CONTENT = {
    "chart_basics": {
        "category": "차트 보는 법",
        "topics": [
            {
                "title": "캔들스틱 차트",
                "level": "beginner",
                "what": "...", "how": "...", "when": "...", "example": "..."
            },
        ]
    },
    "key_metrics": { ... },
    "technicals": { ... },
    "market_concepts": { ... },
    "investment_styles": { ... }
}
```

### 설계 결정 사항

| 결정 | 이유 |
|---|---|
| 정적 콘텐츠, API 호출 없음 | 즉시 응답, 비용 없음 |
| 5개 카테고리 | 차트, 핵심 지표, 기술적 지표, 시장 개념, 투자 스타일 |
| 3단계 난이도 | beginner / intermediate / advanced |
| What → How → When → Example 구조 | 단계적 학습 흐름 |

---

## Market Overview (market_overview.py)

### 목적
시장 지수 + 급등/급락 + 뉴스 데이터 수집.

### 구현 파일
- `data/market_overview.py`

### 핵심 구조

```python
def get_market_indices() -> list[dict]:
    """S&P 500, NASDAQ, DOW, BTC, ETH, VIX → 현재가 + 등락률"""

def get_top_movers() -> dict:
    """급등 Top 5 + 급락 Top 5"""

def get_market_news(limit=5) -> list[dict]:
    """주요 뉴스 헤드라인 (Finnhub News)"""
```

### 설계 결정 사항

| 결정 | 이유 |
|---|---|
| yfinance: ^GSPC, ^IXIC, ^DJI, ^VIX, BTC-USD, ETH-USD | 암호화폐 포함 광범위한 시장 커버리지 |
| Finnhub으로 급등락 + 뉴스 | 무료 티어에서 실시간 데이터 제공 |

---

## Phase 5 스킬 범용/전용 분류

| 스킬 | 분류 | 이유 |
|---|---|---|
| compare | project-specific | 종목 비교 유형 판정 |
| style_classifier | project-specific | 투자 스타일 분류 |
| compare_agent | project-specific | AI 비교 분석 |
| watchlist | project-specific | Watchlist CRUD |
| guide_content | project-specific | 정적 교육 콘텐츠 |
| market_overview | project-specific | 시장 데이터 집계 |

---

## 선행 조건 및 의존성

- Phase 2: Quick Look 데이터 함수 (시세, 재무, 기술지표)
- Phase 3: Claude 호출 구조 (compare_agent용)
- `config/related_industries.json` 존재

---

## 개발 시 주의사항

- 이 Phase에서 UI 프레임워크 코드 작성 금지 — 순수 함수/클래스만
- 화면 전환 로직(session_state.mode 관리)은 Phase 6 이후로 이동
- compare.py의 sector/industry 필드명은 Phase 2의 fundamentals와 동일하게 유지
- AI 비교 분석은 1회 호출. same_sector가 토큰 적고, cross_sector가 토큰 많음

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-06 | 최초 작성 |
| 2026-04-13 | Phase 5 구현 완료 — 6개 모듈, 테스트 PASSED |
| 2026-04-14 | 상태 ✅ 완료로 업데이트. market_overview에 BTC/ETH 추가 |
