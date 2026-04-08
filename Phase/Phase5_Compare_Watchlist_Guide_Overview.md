# Phase 5 — Compare + Watchlist + Guide + Overview 데이터 ���직 `🔲 미시작`

> 나��지 기능의 데이터 로직 전부 완성. 화면 전환은 Phase 6으로 분리.

**상태**: 🔲 미시작
**선행 조건**: Phase 4 완료

---

## 개요

Compare Mode(비교 유형 판정, 투자 스타일 분류, AI 비교 분석), Watchlist(종목 관리, 등락률 조회), Beginner's Guide(콘텐츠 데이터), Market Overview(지수, 급등락, 뉴스)의 **데이터 로직만** 개발한다. Streamlit session_state 연동, 화면 전환 로직, 모드 분기는 Phase 6(UI)에서 처리한다.

---

## 완료 예정 / 완료 항목

| # | 모듈 | 상태 | 설명 |
|---|---|---|---|
| 1 | `data/compare.py` | 🔲 | 비교 유형 판정 + 데이터 비교 |
| 2 | `data/style_classifier.py` | 🔲 | 투자자 스타일 분류 (Growth/Value/Balanced) |
| 3 | `agents/compare_agent.py` | 🔲 | AI 비교 분석 (same/cross 프롬프트 분기) |
| 4 | `data/watchlist.py` | 🔲 | Watchlist CRUD + 등락률 조회 |
| 5 | `data/guide_content.py` | 🔲 | 가이드 콘텐츠 딕셔너리 |
| 6 | `data/market_overview.py` | 🔲 | 시장 지수 + 급등락 + 뉴스 |

---

## Compare Mode — 비교 유형 판정 (compare.py)

### 목적
2~3 종목이 같은 섹터인지 다른 섹터인지 자동 감지

### 핵심 함수
```python
def detect_comparison_type(tickers: list[str]) -> str:
    """
    4단계 판정 로직:
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
- related_industries.json에 없는 조합은 기본값 "cross_sector" (안전한 쪽)
- sector/industry 빈 값이면 "Unknown" → "cross_sector"
- Quick Look 데이터의 sector/industry 재사용 (추가 API 호출 없음)

---

## Compare Mode — 투자 스타일 분류 (style_classifier.py)

### 목적
각 종목을 Growth / Value / Balanced로 분류

### 핵심 함수
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
|------|--------|-------|----------|
| 매출 성장률 (YoY) | 20%+ | < 10% | 10~20% |
| Forward P/E | 25+ | < 18 | 18~25 |
| 배당 수익률 | < 0.5% | 2%+ | 0.5~2% |

### 설계 결정 사항
- 코드가 1차 분류, AI가 맥락 보정 (Phase에서는 코드 분류만)
- Growth 체크를 먼저 하는 이유: 성장이 압도적이면 PE 높아도 Growth

---

## Compare Mode — AI 비교 분석 (compare_agent.py)

### 목적
비교 유형에 따라 다른 프롬프트로 AI 비교 분석

### 핵심 함수
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
- 섹터 맥락 (각 종목의 드라이버)
- 밸류에이션: 자기 섹터 평균 대비 (AAPL PE 28 vs 소비자전자 평균 25)
- 섹터 무관 지표 (FCF yield, ROE, D/E)
- 매크로 시나리오별 반응 (금리 유지, 경기 침체)
- 포트폴리오 분산 관점
- 투자 성향별 추천 + Blind spots

---

## Watchlist (watchlist.py)

### 목적
관심 종목 관리 + 등락률 조회

### 핵심 함수
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
- 데이터 로직만. session_state 연동은 UI Phase에서
- ±5% 판정: `abs(change_percent) >= 5.0` → `highlight: True` 플래그

---

## Beginner's Guide (guide_content.py)

### 목적
가이드 콘텐츠를 딕셔너리로 관리

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
            ...
        ]
    },
    "key_metrics": { ... },
    "technicals": { ... },
    "market_concepts": { ... },
    "investment_styles": { ... }
}
```

### 설계 결정 사항
- 정적 콘텐츠. API 호출 없음
- 카테고리 5개: 차트, 핵심 지표, 기술적 지표, 시장 개념, 투자 스타일
- 난이도: beginner / intermediate / advanced
- 각 주제: What → How → When → Example 구조

---

## Market Overview (market_overview.py)

### 목적
시장 지수 + 급등/급락 + 뉴스 데이터 수집

### 핵심 함수
```python
def get_market_indices() -> list[dict]:
    """S&P 500, NASDAQ, DOW, VIX → 현재가 + 등락률"""

def get_top_movers() -> dict:
    """급등 Top 5 + 급락 Top 5"""

def get_market_news(limit=5) -> list[dict]:
    """주요 뉴스 헤드라인 (Finnhub News)"""
```

### 설계 결정 사항
- yfinance: ^GSPC, ^IXIC, ^DJI, ^VIX
- Finnhub 또는 yfinance screener로 급등/급락
- Finnhub News API로 헤드라인

---

## 선행 조건 및 의존성

- Phase 2: Quick Look 데이터 함수 (시세, 재무, 기술지표)
- Phase 3: Claude 호출 구조 (compare_agent용)
- config/related_industries.json 존재

---

## 개발 시 주의사항

- 이 Phase에서 Streamlit 코드 작성 금지. 순수 함수/클래스만
- 화면 전환 로직(session_state.mode 관리)은 Phase 6으로 이동됨
- compare.py의 sector/industry 필드명은 Phase 2의 fundamentals와 동일하게 유지
- AI 비교 분석은 1회 호출. same_sector가 토큰 적고, cross_sector가 토큰 많음

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-06 | 최초 작성 |
