# Phase 4 — Sector Screening `✅ Completed`

> Sector selection → 3-stage filter (common/preset/adaptive relaxation) → AI batch analysis → Top 5 recommendation

**Completed**: 2026-04-14
**Status**: ✅ Completed
**Prerequisites**: Phase 3 completed (AI call structure reused)

---

## Overview

When a user selects a GICS sector or custom theme, stocks are filtered through a 3-stage pipeline, then analyzed by AI in a single batch call to produce a Top 5 recommendation. Since applying identical filters to all sectors would wipe out biotech while passing all big tech, 4 preset types + adaptive relaxation accommodate sector characteristics. Custom theme creation is also supported.

---

## Deliverables

| # | Module | Status | Type |
|---|---|---|---|
| 1 | `data/sector_data.py` | ✅ | project-specific |
| 2 | `data/theme_manager.py` | ✅ | project-specific |
| 3 | `data/stock_filter.py` | ✅ | project-specific |
| 4 | `agents/sector_analyzer.py` | ✅ | project-specific |

---

## Sector Data (sector_data.py)

### Purpose
Query stock lists for GICS 11 sectors.

### Implementation Files
- `data/sector_data.py`

### Core Structure

```python
def get_sector_tickers(sector: str) -> list[str]:
    """Query sector stocks via FMP Stock Screener API"""

def get_preset_for_sector(sector: str) -> str:
    """GICS sector → preset mapping"""
    SECTOR_PRESET_MAP = {
        "Information Technology": "large_stable",
        "Financials": "large_stable",
        "Communication Services": "large_stable",
        "Consumer Discretionary": "large_stable",
        "Industrials": "mid_growth",
        "Energy": "mid_growth",
        "Materials": "mid_growth",
        "Consumer Staples": "mid_growth",
        "Health Care": "early_growth",
        "Utilities": "dividend",
        "Real Estate": "dividend",
    }
```

---

## Theme Manager (theme_manager.py)

### Purpose
CRUD operations for themes.json.

### Implementation Files
- `data/theme_manager.py`

### Core Structure

```python
def load_themes() -> dict
def create_theme(name: str, tickers: list, preset: str) -> None
def delete_theme(name: str) -> None
```

### Design Decisions

| Decision | Reason |
|---|---|
| Minimum 5 tickers enforced | Fewer tickers make filtering meaningless |
| Only 4 preset types allowed | Consistent filter behavior |
| Auto-create 5 default themes if themes.json missing | Zero-config first run |

---

## 3-Stage Filter (stock_filter.py)

### Purpose
Filter sector stocks down to AI analysis candidates.

### Implementation Files
- `data/stock_filter.py`

### Core Structure

```python
def filter_stocks(tickers: list, preset: str) -> tuple[list, bool, str | None]:
    """Returns: (filtered tickers, relaxation applied, warning message)"""
```

### Stage Details

**Stage 1 — Common Filter** (remove bad data)
- Exclude zero average daily volume
- Exclude missing key financial data
- US-listed only (exclude OTC)

**Stage 2 — Preset Filter** (4 types)

| Preset | Market Cap | Profitability | Special |
|---|---|---|---|
| `large_stable` | $50B+ | PE positive | — |
| `mid_growth` | $10B+ | PE positive | — |
| `early_growth` | $2B+ | Any | Revenue growth 20%+ |
| `dividend` | $5B+ | PE positive | Dividend yield 2%+ |

**Stage 3 — Adaptive Relaxation** (auto-adjust by pass count)

| Pass Count | Action | Relaxed |
|---|---|---|
| 10+ | Take top 10 | False |
| 5–9 | Pass all | False |
| 3–4 | Relax market cap 1 tier ($50B→$20B, $10B→$5B, $2B→$1B) | True |
| 0–2 | Ignore filters, take top 10 by market cap | True + warning |

---

## AI Batch Analysis (sector_analyzer.py)

### Purpose
Condensed AI analysis for filtered stocks (max 10) → select Top 5.

### Implementation Files
- `agents/sector_analyzer.py`

### Core Structure

```python
def run_sector_screening(sector_or_theme: str) -> dict:
    """
    Returns: {
        "sector": "Information Technology",
        "filter_applied": "large_stable",
        "relaxed": False,
        "relaxation_message": None,
        "top5": [
            {"ticker": "LMT", "score": 82, "reason": "NATO spending beneficiary"},
            ...
        ]
    }
    """
```

### Design Decisions

| Decision | Reason |
|---|---|
| Batch call: 10 stocks in 1 Claude call | 85% cost reduction ($0.90 → $0.15) vs per-stock calls |
| max_tokens: 4096 | Prevent response truncation for 10-stock analysis |
| Prompt: "Analyze all stocks with equal depth" | Prevent quality degradation for later stocks |
| Condensed format: sentiment(1 line) + financials(1 line) + technicals(1 line) + score 0–100 + reason | Fits 10 stocks in one response |
| 1 retry on failure | Batch failure loses all 10 stocks, so retry is worthwhile |

---

## Phase 4 Skill Classification

| Skill | Classification | Reason |
|---|---|---|
| sector_data | project-specific | GICS sector stock query |
| theme_manager | project-specific | Custom theme CRUD |
| stock_filter | project-specific | Financial stock filtering pipeline |
| sector_analyzer | project-specific | AI batch stock screening |

---

## Prerequisites & Dependencies

- Phase 3: Claude call structure (`claude_client.py`) reused
- Phase 2: Quick Look data collection functions reused
- `config/themes.json` must exist

---

## Development Notes

- FMP free tier: 250/day. Sector query 1 + financial data N calls. Watch for excessive calls during testing
- Adaptive relaxation warning message must always be returned — UI must display it to the user
- themes.json file I/O concurrency is not an issue (single-process app)

---

## Change Log

| Date | Description |
|---|---|
| 2026-04-06 | Initial creation |
| 2026-04-10 | AI analysis changed from per-stock (10 calls) to batch (1 call) |
| 2026-04-13 | Phase 4 implementation complete — 4 modules, tests passed |
| 2026-04-14 | Status updated to ✅ Completed |

---
---

# Phase 4 — Sector Screening `✅ 완료`

> 섹터 선택 → 3단계 필터(공통/프리셋/적응형 완화) → AI 일괄 분석 → Top 5 추천

**완료일**: 2026-04-14
**상태**: ✅ 완료
**선행 조건**: Phase 3 완료 (AI 호출 구조 재사용)

---

## 개요

사용자가 GICS 섹터 또는 커스텀 테마를 선택하면, 3단계 필터로 종목을 걸러낸 뒤 AI 일괄 분석으로 Top 5를 추천한다. 모든 섹터에 동일 필터를 적용하면 바이오는 전멸하고 빅테크는 전부 통과하므로, 4종 프리셋 + 적응형 완화로 섹터 특성을 반영한다. 커스텀 테마 생성 기능도 포함.

---

## 완료 항목

| # | 모듈 | 상태 | 스킬 타입 |
|---|---|---|---|
| 1 | `data/sector_data.py` | ✅ | project-specific |
| 2 | `data/theme_manager.py` | ✅ | project-specific |
| 3 | `data/stock_filter.py` | ✅ | project-specific |
| 4 | `agents/sector_analyzer.py` | ✅ | project-specific |

---

## 섹터 데이터 (sector_data.py)

### 목적
GICS 11개 섹터의 종목 리스트를 조회한다.

### 구현 파일
- `data/sector_data.py`

### 핵심 구조

```python
def get_sector_tickers(sector: str) -> list[str]:
    """FMP Stock Screener API로 섹터별 종목 조회"""

def get_preset_for_sector(sector: str) -> str:
    """GICS 섹터 → 프리셋 매핑"""
    SECTOR_PRESET_MAP = {
        "Information Technology": "large_stable",
        "Financials": "large_stable",
        "Communication Services": "large_stable",
        "Consumer Discretionary": "large_stable",
        "Industrials": "mid_growth",
        "Energy": "mid_growth",
        "Materials": "mid_growth",
        "Consumer Staples": "mid_growth",
        "Health Care": "early_growth",
        "Utilities": "dividend",
        "Real Estate": "dividend",
    }
```

---

## 테마 매니저 (theme_manager.py)

### 목적
themes.json CRUD 관리.

### 구현 파일
- `data/theme_manager.py`

### 핵심 구조

```python
def load_themes() -> dict
def create_theme(name: str, tickers: list, preset: str) -> None
def delete_theme(name: str) -> None
```

### 설계 결정 사항

| 결정 | 이유 |
|---|---|
| 최소 5개 티커 강제 | 티커 수가 적으면 필터링이 무의미 |
| 4종 프리셋만 허용 | 일관된 필터 동작 보장 |
| themes.json 없으면 기본 5개 테마 자동 생성 | 설정 없이 즉시 사용 가능 |

---

## 3단계 필터 (stock_filter.py)

### 목적
섹터 종목을 AI 분석 대상으로 축소한다.

### 구현 파일
- `data/stock_filter.py`

### 핵심 구조

```python
def filter_stocks(tickers: list, preset: str) -> tuple[list, bool, str | None]:
    """반환: (필터된 티커 리스트, 완화 적용 여부, 경고 메시지)"""
```

### 단계 상세

**1단계 — 공통 필터** (불량 데이터 제거)
- 일평균 거래량 0 제외
- 주요 재무 데이터 누락 제외
- 미국 상장만 (OTC 제외)

**2단계 — 유형별 프리셋** (4종)

| 프리셋 | 시총 | 수익성 | 특수 조건 |
|---|---|---|---|
| `large_stable` | $50B+ | PE 양수 | — |
| `mid_growth` | $10B+ | PE 양수 | — |
| `early_growth` | $2B+ | 무관 | 매출 성장 20%+ |
| `dividend` | $5B+ | PE 양수 | 배당률 2%+ |

**3단계 — 적응형 완화** (통과 종목 수에 따라 자동 조정)

| 통과 수 | 처리 | 완화 |
|---|---|---|
| 10개+ | 상위 10개 선정 | False |
| 5~9개 | 전부 통과 | False |
| 3~4개 | 시총 기준 1단계 완화 ($50B→$20B, $10B→$5B, $2B→$1B) | True |
| 0~2개 | 필터 무시, 시총 상위 10개 | True + 경고 메시지 |

---

## AI 일괄 분석 (sector_analyzer.py)

### 목적
필터 통과 종목(최대 10개)에 대해 축약 AI 분석 → Top 5 선정.

### 구현 파일
- `agents/sector_analyzer.py`

### 핵심 구조

```python
def run_sector_screening(sector_or_theme: str) -> dict:
    """
    반환: {
        "sector": "Information Technology",
        "filter_applied": "large_stable",
        "relaxed": False,
        "relaxation_message": None,
        "top5": [
            {"ticker": "LMT", "score": 82, "reason": "NATO 지출 확대 수혜"},
            ...
        ]
    }
    """
```

### 설계 결정 사항

| 결정 | 이유 |
|---|---|
| 일괄 호출: 10개 종목을 1회 Claude 호출로 분석 | 종목별 호출 대비 85% 비용 절감 ($0.90 → $0.15) |
| max_tokens: 4096 | 10개 종목 분석 응답이 잘리지 않도록 확보 |
| 프롬프트: "모든 종목을 동일한 깊이로 분석해" | 후반부 품질 저하 방지 |
| 축약 형식: 감성(1줄) + 재무(1줄) + 기술(1줄) + 점수 0~100 + 이유 | 10개 종목이 하나의 응답에 수용 가능 |
| 실패 시 1회 재시도 | 일괄 실패 시 10개 전부 재시도할 가치 있음 |

---

## Phase 4 스킬 범용/전용 분류

| 스킬 | 분류 | 이유 |
|---|---|---|
| sector_data | project-specific | GICS 섹터 종목 조회 |
| theme_manager | project-specific | 커스텀 테마 CRUD |
| stock_filter | project-specific | 금융 종목 필터 파이프라인 |
| sector_analyzer | project-specific | AI 일괄 종목 스크리닝 |

---

## 선행 조건 및 의존성

- Phase 3: Claude 호출 구조 (`claude_client.py`) 재사용
- Phase 2: Quick Look 데이터 수집 함수 재사용
- `config/themes.json` 존재

---

## 개발 시 주의사항

- FMP 무료 일 250회. 섹터 조회 1회 + 재무 데이터 N회 소모. 테스트 시 과다 호출 주의
- 적응형 완화 시 경고 메시지를 반드시 반환 — UI에서 사용자에게 표시해야 함
- themes.json 파일 I/O 동시성 이슈 없음 (단일 프로세스 앱)

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-06 | 최초 작성 |
| 2026-04-10 | AI 분석 방식 변경 — 종목별 호출(10회) → 일괄 호출(1회) |
| 2026-04-13 | Phase 4 구현 완료 — 4개 모듈, 테스트 PASSED |
| 2026-04-14 | 상태 ✅ 완료로 업데이트 |
