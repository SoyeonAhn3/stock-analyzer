# Phase 2 — Quick Look `✅ Completed`

> Data collection layer that returns quotes, charts, fundamentals, and technicals for any given ticker

**Completed**: 2026-04-08
**Status**: ✅ Completed
**Prerequisites**: Phase 1 completion (API wrappers + caching available)

---

## Overview

Quick Look is a pure data collection feature with no AI involvement. Given a ticker, it collects quotes, price history, fundamentals, and technical indicators from 4 APIs in parallel and returns them as dict/DataFrame. This data is reused in Phase 3 (AI Agents), making this Phase the **data foundation for the entire project**. Screen rendering is handled in the UI Phases; this Phase only develops data collection functions.

---

## Deliverables

| # | Module | Status | Type |
|---|---|---|---|
| 1 | `data/quote.py` | ✅ | project-specific |
| 2 | `data/history.py` | ✅ | project-specific |
| 3 | `data/fundamentals.py` | ✅ | project-specific |
| 4 | `data/technicals.py` | ✅ | project-specific |
| 5 | `utils/indicators.py` | ✅ | general |
| 6 | `utils/chart_builder.py` | ✅ | project-specific |
| 7 | `utils/tooltips.py` | ✅ | project-specific |

---

## Quote Collection (quote.py)

### Purpose

Collect current price, change, volume, intraday range, and pre/post-market quotes.

### Implementation Files

- `data/quote.py`

### Core Structure

```python
def get_quote(ticker: str) -> dict | None:
    """Finnhub → yfinance fallback"""
    return {
        "price": 142.50, "change": 3.20, "change_percent": 2.3,
        "volume": 45_000_000, "day_high": 144.00, "day_low": 140.10,
        "source": "finnhub"
    }

def get_premarket(ticker: str) -> dict | None:
    """Pre/post-market quote. Returns None if unavailable."""
```

### Design Decisions

| Decision | Reason |
|---|---|
| Finnhub first, yfinance fallback | Finnhub is near-real-time |
| Return `None` for invalid tickers | No exceptions, caller handles display |
| Include `source` field | Track data provenance |
| Cache TTL 60s for quotes | Quotes change frequently; other data uses 5min |

---

## Price History (history.py)

### Purpose

Return period-based OHLCV DataFrames for charting.

### Implementation Files

- `data/history.py`

### Core Structure

```python
def get_history(ticker: str, period: str) -> pd.DataFrame | None:
    """period: '1W','1M','3M','6M','1Y','5Y'"""
    # Returns: Date, Open, High, Low, Close, Volume columns
```

### Design Decisions

| Decision | Reason |
|---|---|
| yfinance as sole source | Most comprehensive free history data |
| MA50/MA200 added as DataFrame columns | Pre-computed for chart overlay |
| Period string mapped to yfinance parameter | User-friendly input |

---

## Fundamentals (fundamentals.py)

### Purpose

PE, Forward PE, EPS, PEG, market cap, 52-week range, dividend yield, D/E, sector, industry.

### Implementation Files

- `data/fundamentals.py`

### Core Structure

```python
def get_fundamentals(ticker: str, force_fallback=False) -> dict | None:
    """yfinance (.info) → Finviz fallback"""
    return {
        "pe": 35.2, "forward_pe": 28.1, "eps": 4.05,
        "peg": 1.8, "market_cap": 3_500_000_000_000,
        "week52_high": 153.0, "week52_low": 76.0,
        "dividend_yield": 0.0003, "de_ratio": 0.41,
        "sector": "Technology", "industry": "Semiconductors",
        "source": "yfinance"
    }
```

### Design Decisions

| Decision | Reason |
|---|---|
| yfinance first, Finviz fallback | FMP free plan returns 403, replaced by Finviz |
| `force_fallback=True` parameter | Test Finviz fallback path |
| sector/industry fields preserved | Reused by Phase 5 Compare Mode for sector detection |

---

## Technical Indicators (technicals.py)

### Purpose

RSI, MACD, Bollinger Bands, MA, volume trend + signal determination.

### Implementation Files

- `data/technicals.py`
- `utils/indicators.py` (Python calculation fallback)

### Core Structure

```python
def get_technicals(ticker: str, force_fallback=False) -> dict | None:
    """Twelve Data → Python direct calculation fallback"""
    return {
        "rsi": {"value": 62, "signal": "neutral"},
        "macd": {"signal": "bullish", "detail": "bullish crossover 3 days"},
        "bollinger": {"position": "middle", "signal": "neutral"},
        "ma50": {"vs_price": "+3.1%", "signal": "bullish"},
        "ma200": {"vs_price": "+17.3%", "signal": "bullish"},
        "volume": {"vs_20d_avg": "+15%", "signal": "neutral"}
    }
```

### Design Decisions

| Decision | Reason |
|---|---|
| Twelve Data first (API computes indicators) | Pre-computed values, no local math needed |
| Fallback: `indicators.py` calculates from yfinance price data | Works without Twelve Data API |
| Each indicator has `signal` field: "bullish"/"neutral"/"bearish" | Standardized interpretation |
| RSI 70+ → bearish (overbought), 30- → bullish (oversold) | Standard RSI interpretation |

---

## Cache TTL Separation Policy

| Data Type | TTL | Reason |
|---|---|---|
| Quote | 60s | Stock prices change in real-time |
| Fundamentals / Chart / Technicals | 5min | PE, RSI, chart history barely change within 1 minute |
| AI analysis results | 1hr | AI interpretation doesn't change short-term |
| Sector data | 6hr | Sector composition rarely changes |

---

## Prerequisites & Dependencies

- Phase 1 complete: API wrappers, caching, api_config available
- pip: `yfinance`, `plotly`, `pandas`, `requests`

---

## Development Notes

- All functions are pure Python — no Streamlit dependency
- Return `None` on error; display "N/A" is the UI Phase's responsibility
- `get_fundamentals` sector/industry field names are reused in Phase 5 Compare Mode — do not rename
- Quick Look data as a whole dict is passed to Phase 3 Agents

---

## Phase 2 Skill Classification

| Skill | Classification | Reason |
|---|---|---|
| Data collection pattern | General | Reusable multi-source data aggregation |
| TTL separation policy | General | Applicable to any multi-frequency data system |
| Financial indicator calculation | Project-specific | Tied to specific financial metrics |
| Chart builder (Plotly) | Project-specific | Specific visualization library |

---

## Change Log

| Date | Description |
|---|---|
| 2026-04-06 | Initial creation |
| 2026-04-08 | Phase 2 complete — 7 modules implemented, 31 tests PASSED |
| 2026-04-10 | Cache TTL separation policy added — quote 60s vs others 5min |
| 2026-04-13 | fundamentals.py force_fallback target changed from FMP → Finviz |
| 2026-04-13 | Real API tests — 19 tests: 18 PASSED, 1 SKIPPED(FMP) → fixed → 19 PASSED |

---
---

# Phase 2 — Quick Look `✅ 완료`

> 티커 입력 시 시세, 차트, 재무 지표, 기술적 지표를 즉시 반환하는 데이터 수집 계층 완성

**완료일**: 2026-04-08
**상태**: ✅ 완료
**선행 조건**: Phase 1 완료 (API 래퍼 + 캐싱 사용 가능)

---

## 개요

Quick Look은 AI를 사용하지 않는 순수 데이터 조회 기능이다. 티커를 받으면 4개 API에서 병렬로 시세, 히스토리, 재무, 기술지표를 수집하여 dict/DataFrame으로 반환한다. 이 데이터는 Phase 3(AI Agent)에서 재사용되므로 **이 Phase가 전체 프로젝트의 데이터 기반**이 된다. 화면 렌더링은 UI Phase에서 처리하고, 여기서는 데이터 수집 함수만 개발한다.

---

## 완료 예정 / 완료 항목

| # | Skill / 모듈 | 상태 | 스킬 타입 |
|---|---|---|---|
| 1 | `data/quote.py` | ✅ | project-specific |
| 2 | `data/history.py` | ✅ | project-specific |
| 3 | `data/fundamentals.py` | ✅ | project-specific |
| 4 | `data/technicals.py` | ✅ | project-specific |
| 5 | `utils/indicators.py` | ✅ | general |
| 6 | `utils/chart_builder.py` | ✅ | project-specific |
| 7 | `utils/tooltips.py` | ✅ | project-specific |

---

## 시세 수집 (quote.py)

### 목적

현재가, 등락, 거래량, 일중 범위, 장 전/후 시세 수집

### 구현 파일

- `data/quote.py`

### 핵심 클래스 / 구조

```python
def get_quote(ticker: str) -> dict | None:
    """Finnhub → yfinance 폴백"""
    return {
        "price": 142.50, "change": 3.20, "change_percent": 2.3,
        "volume": 45_000_000, "day_high": 144.00, "day_low": 140.10,
        "source": "finnhub"
    }

def get_premarket(ticker: str) -> dict | None:
    """장 전/장 후 시세. 없으면 None"""
```

### 설계 결정 사항

| 결정 | 이유 |
|---|---|
| Finnhub 1순위, yfinance 폴백 | Finnhub이 준실시간 |
| 잘못된 티커 시 `None` 반환 | 예외 미발생, 호출자가 표시 처리 |
| `source` 필드 포함 | 데이터 출처 추적 |
| 시세 캐시 TTL 60초 | 시세는 실시간 변동, 다른 데이터(5분)보다 짧게 |

---

## 주가 히스토리 (history.py)

### 목적

기간별 OHLCV 데이터프레임 반환 (차트용)

### 구현 파일

- `data/history.py`

### 핵심 클래스 / 구조

```python
def get_history(ticker: str, period: str) -> pd.DataFrame | None:
    """period: '1W','1M','3M','6M','1Y','5Y'"""
    # 반환: Date, Open, High, Low, Close, Volume 컬럼
```

### 설계 결정 사항

| 결정 | 이유 |
|---|---|
| yfinance 단일 소스 | 히스토리 데이터는 yfinance가 가장 풍부 |
| MA50/MA200을 DataFrame 컬럼에 추가 | 차트 오버레이용 사전 계산 |
| 기간 문자열을 yfinance 파라미터로 매핑 | 사용자 친화적 입력 |

---

## 재무 지표 (fundamentals.py)

### 목적

PE, Forward PE, EPS, PEG, 시가총액, 52주 고저, 배당률, D/E, 섹터, 산업

### 구현 파일

- `data/fundamentals.py`

### 핵심 클래스 / 구조

```python
def get_fundamentals(ticker: str, force_fallback=False) -> dict | None:
    """yfinance (.info) → Finviz 폴백"""
    return {
        "pe": 35.2, "forward_pe": 28.1, "eps": 4.05,
        "peg": 1.8, "market_cap": 3_500_000_000_000,
        "week52_high": 153.0, "week52_low": 76.0,
        "dividend_yield": 0.0003, "de_ratio": 0.41,
        "sector": "Technology", "industry": "Semiconductors",
        "source": "yfinance"
    }
```

### 설계 결정 사항

| 결정 | 이유 |
|---|---|
| yfinance 1순위, Finviz 폴백 | FMP 무료 플랜 403 제한으로 Finviz 대체 |
| `force_fallback=True` 파라미터 | 테스트에서 Finviz 폴백 경로 강제 확인용 |
| sector, industry 필드명 유지 | Phase 5 Compare Mode 섹터 판정에 재사용 |

---

## 기술적 지표 (technicals.py)

### 목적

RSI, MACD, 볼린저밴드, MA, 거래량 추이 + 신호 판정

### 구현 파일

- `data/technicals.py`
- `utils/indicators.py` (Python 직접 계산 폴백)

### 핵심 클래스 / 구조

```python
def get_technicals(ticker: str, force_fallback=False) -> dict | None:
    """Twelve Data → Python 직접 계산 폴백"""
    return {
        "rsi": {"value": 62, "signal": "neutral"},
        "macd": {"signal": "bullish", "detail": "bullish crossover 3일째"},
        "bollinger": {"position": "middle", "signal": "neutral"},
        "ma50": {"vs_price": "+3.1%", "signal": "bullish"},
        "ma200": {"vs_price": "+17.3%", "signal": "bullish"},
        "volume": {"vs_20d_avg": "+15%", "signal": "neutral"}
    }
```

### 설계 결정 사항

| 결정 | 이유 |
|---|---|
| Twelve Data 1순위 (API가 지표 직접 계산) | 사전 계산된 값 반환, 로컬 계산 불필요 |
| 폴백: `indicators.py`에서 yfinance 가격 데이터로 Python 직접 계산 | Twelve Data API 없이도 동작 |
| 각 지표에 `signal` 필드: "bullish"/"neutral"/"bearish" | 표준화된 해석 |
| RSI 70+ → bearish(과매수), 30- → bullish(과매도) | 표준 RSI 해석 |

---

## 캐시 TTL 분리 정책

| 데이터 종류 | TTL | 이유 |
|---|---|---|
| 시세 (quote) | 60초 | 주가는 실시간 변동 |
| 재무/차트/기술지표 | 5분 | PER, RSI, 차트 히스토리는 1분 내 거의 변하지 않음 |
| AI 분석 결과 | 1시간 | AI 해석은 단기간에 바뀌지 않음 |
| 섹터 정보 | 6시간 | 섹터 구성은 거의 변하지 않음 |

---

## 선행 조건 및 의존성

- Phase 1 완료: API 래퍼, 캐싱, api_config 사용 가능
- pip: `yfinance`, `plotly`, `pandas`, `requests`

---

## 개발 시 주의사항

- 모든 함수는 Streamlit 의존 없이 순수 Python으로 작성
- 에러 시 `None` 반환. "N/A" 표시는 UI Phase의 책임
- `get_fundamentals`의 sector/industry 필드명은 Phase 5 Compare Mode에서 재사용 — 키 이름 변경 금지
- Quick Look 데이터 전체를 dict로 묶어 Phase 3 Agent에 전달

---

## Phase 2 스킬 범용/전용 분류

| 스킬 | 분류 | 이유 |
|---|---|---|
| 데이터 수집 패턴 | 범용 | 다중 소스 데이터 집계에 재사용 가능 |
| TTL 분리 정책 | 범용 | 다중 빈도 데이터 시스템에 적용 가능 |
| 금융 지표 계산 | 전용 | 특정 금융 메트릭에 종속 |
| 차트 빌더 (Plotly) | 전용 | 특정 시각화 라이브러리 |

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-06 | 최초 작성 |
| 2026-04-08 | Phase 2 전체 완료 — 7개 모듈 구현, 31개 테스트 PASSED |
| 2026-04-10 | 캐시 TTL 분리 정책 추가 — 시세(60초) vs 나머지(5분) |
| 2026-04-13 | fundamentals.py force_fallback 대상을 FMP → Finviz로 변경 |
| 2026-04-13 | 실제 API 테스트 수행 — 19개 테스트 중 18 PASSED, 1 SKIPPED(FMP) → 코드 수정 후 19 PASSED |
