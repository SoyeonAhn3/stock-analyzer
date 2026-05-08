# Phase 1 — API Integration `✅ Completed`

> Project structure setup, 6 financial API wrappers, fallback logic, and caching module

**Completed**: 2026-04-08
**Status**: ✅ Completed
**Prerequisites**: None (initial Phase)

---

## Overview

Sets up the project directory structure and develops wrapper classes for 6 financial data APIs (yfinance, Finnhub, Twelve Data, FMP, FRED, Finviz). Includes automatic fallback logic when an API fails and a caching module to prevent duplicate calls. Once this Phase is complete, all subsequent Phases can reliably fetch data with a single call like `api_client.get_quote("NVDA")`.

---

## Deliverables

| # | Module | Status | Type |
|---|---|---|---|
| 1 | `config/api_config.py` | ✅ | project-specific |
| 2 | `config/themes.json` | ✅ | project-specific |
| 3 | `config/related_industries.json` | ✅ | project-specific |
| 4 | `data/yfinance_client.py` | ✅ | project-specific |
| 5 | `data/finnhub_client.py` | ✅ | project-specific |
| 6 | `data/twelvedata_client.py` | ✅ | project-specific |
| 7 | `data/fmp_client.py` | ✅ | project-specific |
| 8 | `data/fred_client.py` | ✅ | project-specific |
| 9 | `data/finviz_client.py` | ✅ | project-specific |
| 10 | `data/api_client.py` | ✅ | general |
| 11 | `data/cache.py` | ✅ | general |
| 12 | `utils/usage_tracker.py` | ✅ | general |

---

## API Clients

### Purpose

Wrapper classes for 6 external APIs + a unified client with fallback.

### Implementation Files

```
config/
├── api_config.py              # API key loading, endpoints, timeouts
├── themes.json                # Custom theme ticker lists
└── related_industries.json    # Related industry mapping table

data/
├── yfinance_client.py         # yfinance wrapper (no API key needed)
├── finnhub_client.py          # Finnhub wrapper (60 req/min free)
├── twelvedata_client.py       # Twelve Data wrapper (800/day free)
├── fmp_client.py              # FMP wrapper (fallback only, free plan limited)
├── fred_client.py             # FRED wrapper (macroeconomic data)
├── finviz_client.py           # Finviz wrapper (FMP replacement for sector/PE)
├── api_client.py              # Unified API client (fallback logic)
└── cache.py                   # In-memory TTL cache
```

### Design Decisions

| Decision | Reason |
|---|---|
| Common interface per wrapper (`get_quote()`, `get_history()`, `get_fundamentals()`) | Consistent API, easy fallback switching |
| 15-second timeout | Prevents blocking on slow APIs |
| Return `None` on error (no exceptions raised) | Caller decides fallback behavior |
| Built-in call counter per wrapper | Daily rate limit tracking |
| Unified client auto-executes fallback based on priority table | Transparent failover |
| Include `"source"` field in results | Track which API provided the data |
| FMP free plan 403 → Finviz replacement | FMP free tier too limited for production use |

---

## Caching Module

### Purpose

Prevent duplicate API calls for the same data.

### Implementation Files

- `data/cache.py`

### Design Decisions

| Decision | Reason |
|---|---|
| Key: (function_name, ticker, parameters) tuple | Unique per request |
| TTL: quote 60s, Quick Look 5min, AI results 1hr, Sector 6hr | Match data volatility |
| Storage: in-memory dictionary | No persistence needed for cache |
| Manual invalidation: `cache.invalidate(ticker)` | Allow forced refresh |
| `cache.force_expire()` for testing | Test convenience |

---

## Prerequisites & Dependencies

- `.env` file with 5 API keys:
  - `FINNHUB_API_KEY`
  - `TWELVEDATA_API_KEY`
  - `FMP_API_KEY` (fallback only due to free plan limits)
  - `FRED_API_KEY`
  - `ANTHROPIC_API_KEY`
- yfinance and Finviz require no API keys

---

## Development Notes

- yfinance is unofficial — use as first-try source only, not sole dependency
- Finnhub free tier quotes are ~15min delayed — do not label as "real-time"
- FMP free 250/day, Twelve Data free 800/day — monitor test usage
- `.env` must be in `.gitignore`
- Financial APIs may be blocked on certain networks — run integration tests where access is available
- Test file: `tests/test_phase1_real_api.py` — 27 real API tests: 24 PASSED, 3 SKIPPED (FMP 403)

---

## Phase 1 Skill Classification

| Skill | Classification | Reason |
|---|---|---|
| API wrapper pattern | General | Reusable client pattern for any external API |
| Fallback logic | General | Applicable to any multi-source data system |
| TTL cache | General | Standard caching pattern |
| Financial API specifics | Project-specific | Tied to yfinance, Finnhub, etc. |

---

## Change Log

| Date | Description |
|---|---|
| 2026-04-06 | Initial creation |
| 2026-04-08 | Network constraint notes + test strategy added |
| 2026-04-08 | Phase 1 complete — 11 modules implemented, 19 tests PASSED |
| 2026-04-13 | FMP free plan 403 discovered → Finviz wrapper added, fallback priority changed |
| 2026-04-13 | Real API tests — 27 tests: 24 PASSED, 3 SKIPPED (FMP) |

---
---

# Phase 1 — API 연동 `✅ 완료`

> 프로젝트 구조 세팅, 6개 금융 API 래퍼 개발, 폴백 로직, 캐싱 모듈 완성

**완료일**: 2026-04-08
**상태**: ✅ 완료
**선행 조건**: 없음 (최초 Phase)

---

## 개요

프로젝트 디렉토리 구조를 잡고, 6개 금융 데이터 API(yfinance, Finnhub, Twelve Data, FMP, FRED, Finviz)의 래퍼 클래스를 개발한다. API 실패 시 자동으로 대체 소스를 시도하는 폴백 로직과, 중복 호출을 방지하는 캐싱 모듈을 포함한다. 이 Phase가 완료되면 이후 모든 Phase에서 `api_client.get_quote("NVDA")` 한 줄로 안정적인 데이터를 받을 수 있다.

---

## 완료 예정 / 완료 항목

| # | Skill / 모듈 | 상태 | 스킬 타입 |
|---|---|---|---|
| 1 | `config/api_config.py` | ✅ | project-specific |
| 2 | `config/themes.json` | ✅ | project-specific |
| 3 | `config/related_industries.json` | ✅ | project-specific |
| 4 | `data/yfinance_client.py` | ✅ | project-specific |
| 5 | `data/finnhub_client.py` | ✅ | project-specific |
| 6 | `data/twelvedata_client.py` | ✅ | project-specific |
| 7 | `data/fmp_client.py` | ✅ | project-specific |
| 8 | `data/fred_client.py` | ✅ | project-specific |
| 9 | `data/finviz_client.py` | ✅ | project-specific |
| 10 | `data/api_client.py` | ✅ | general |
| 11 | `data/cache.py` | ✅ | general |
| 12 | `utils/usage_tracker.py` | ✅ | general |

---

## API 클라이언트

### 목적

6개 외부 API 각각의 래퍼 클래스 + 통합 클라이언트 (폴백 포함)

### 구현 파일

```
config/
├── api_config.py              # API 키 로딩, 엔드포인트, 타임아웃
├── themes.json                # 커스텀 테마 종목 리스트
└── related_industries.json    # 관련 업종 매핑 테이블

data/
├── yfinance_client.py         # yfinance 래퍼 (API 키 불필요)
├── finnhub_client.py          # Finnhub 래퍼 (무료 60회/분)
├── twelvedata_client.py       # Twelve Data 래퍼 (무료 800/일)
├── fmp_client.py              # FMP 래퍼 (폴백 전용, 무료 플랜 제한)
├── fred_client.py             # FRED 래퍼 (거시경제 데이터)
├── finviz_client.py           # Finviz 래퍼 (FMP 대체 — 섹터 스크리닝/PE)
├── api_client.py              # 통합 API 클라이언트 (폴백 로직)
└── cache.py                   # 인메모리 TTL 캐시
```

### 설계 결정 사항

| 결정 | 이유 |
|---|---|
| 래퍼별 공통 인터페이스 (`get_quote()`, `get_history()`, `get_fundamentals()`) | 일관된 API, 폴백 전환 용이 |
| 15초 타임아웃 | 느린 API에서 블로킹 방지 |
| 에러 시 `None` 반환 (예외 미발생) | 호출자가 폴백 판단 |
| 래퍼별 내장 호출 카운터 | 일일 제한 추적 |
| 통합 클라이언트 — 우선순위 테이블 기반 자동 폴백 | 투명한 장애 전환 |
| 결과에 `"source"` 필드 포함 | 데이터 출처 추적 |
| FMP 무료 플랜 403 → Finviz 대체 | FMP 무료 티어 제한으로 프로덕션 부적합 |

---

## 캐싱 모듈

### 목적

동일 데이터 중복 호출 방지

### 구현 파일

- `data/cache.py`

### 설계 결정 사항

| 결정 | 이유 |
|---|---|
| 키: (함수명, 티커, 파라미터) 조합 | 요청별 고유 |
| TTL: 시세 60초, Quick Look 5분, AI 결과 1시간, 섹터 6시간 | 데이터 변동성에 맞춤 |
| 저장: 인메모리 딕셔너리 | 캐시에 영속성 불필요 |
| 수동 무효화: `cache.invalidate(ticker)` | 강제 갱신 허용 |
| `cache.force_expire()` — 테스트용 | 테스트 편의 |

---

## 선행 조건 및 의존성

- `.env`에 API 키 5개 세팅 필요:
  - `FINNHUB_API_KEY`
  - `TWELVEDATA_API_KEY`
  - `FMP_API_KEY` (무료 플랜 제한으로 폴백 전용)
  - `FRED_API_KEY`
  - `ANTHROPIC_API_KEY`
- yfinance, Finviz는 API 키 불필요

---

## 개발 시 주의사항

- yfinance는 비공식 라이브러리 — 1순위 시도 소스로만 사용, 메인 의존 금지
- Finnhub 무료 시세는 약 15분 지연 — "실시간"이라 표현하지 않기
- FMP 무료 일 250회, Twelve Data 일 800회 — 테스트 시 과다 호출 주의
- `.env` 파일은 반드시 `.gitignore`에 추가
- 네트워크 환경에 따라 금융 API 접속 차단 가능 — 접속 가능한 환경에서 통합 테스트 수행
- 테스트 파일: `tests/test_phase1_real_api.py` — 27개 실제 API 테스트: 24 PASSED, 3 SKIPPED (FMP 403)

---

## Phase 1 스킬 범용/전용 분류

| 스킬 | 분류 | 이유 |
|---|---|---|
| API 래퍼 패턴 | 범용 | 모든 외부 API에 재사용 가능한 클라이언트 패턴 |
| 폴백 로직 | 범용 | 다중 소스 데이터 시스템에 적용 가능 |
| TTL 캐시 | 범용 | 표준 캐싱 패턴 |
| 금융 API 세부 사항 | 전용 | yfinance, Finnhub 등 특정 API에 종속 |

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-06 | 최초 작성 |
| 2026-04-08 | 네트워크 제약 대비 및 테스트 전략 기록 |
| 2026-04-08 | Phase 1 전체 완료 — 11개 모듈 구현, 19개 테스트 PASSED |
| 2026-04-13 | FMP 무료 플랜 403 제한 발견 → Finviz 래퍼 추가, 폴백 우선순위 변경 |
| 2026-04-13 | 실제 API 테스트 수행 — 27개 테스트 중 24 PASSED, 3 SKIPPED (FMP) |
