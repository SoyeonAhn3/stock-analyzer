# Phase 6 — FastAPI Backend `✅ Completed`

> Expose existing data/agents functions as HTTP REST API via FastAPI server

**Completed**: 2026-04-14
**Status**: ✅ Completed
**Prerequisites**: Phase 5 completed (all data/AI logic implemented)

---

## Overview

The Python functions built in Phase 1–5 can only be called directly. For a React frontend to use them, an HTTP API server is needed. This phase wraps existing functions with FastAPI to create REST API endpoints. The data/agents layer is not modified — only wrapped.

---

## Deliverables

| # | Module | Status | Type |
|---|---|---|---|
| 1 | `backend/main.py` | ✅ | project-specific |
| 2 | `backend/routers/quote.py` | ✅ | project-specific |
| 3 | `backend/routers/market.py` | ✅ | project-specific |
| 4 | `backend/routers/analysis.py` | ✅ | project-specific |
| 5 | `backend/routers/sector.py` | ✅ | project-specific |
| 6 | `backend/routers/compare.py` | ✅ | project-specific |
| 7 | `backend/routers/watchlist.py` | ✅ | project-specific |
| 8 | `backend/routers/guide.py` | ✅ | project-specific |
| 9 | `backend/routers/search.py` | ✅ | project-specific |
| 10 | `backend/routers/alerts.py` | ✅ | project-specific |

---

## FastAPI App (main.py)

### Purpose
Create the FastAPI application, configure CORS, register routers, and initialize the database.

### Implementation Files
- `backend/main.py`

### Core Structure

```python
app = FastAPI(title="AI Stock Analyzer API", version="1.0")

# CORS — local dev + Netlify production (dynamic via env var)
_origins = ["http://localhost:3000", "http://localhost:5173"]
_extra = os.environ.get("CORS_ORIGINS", "")
if _extra:
    _origins.extend([o.strip() for o in _extra.split(",") if o.strip()])

app.add_middleware(CORSMiddleware, allow_origins=_origins, ...)

# Router registration
app.include_router(quote.router,     prefix="/api", tags=["Quote"])
app.include_router(market.router,    prefix="/api", tags=["Market"])
app.include_router(analysis.router,  prefix="/api", tags=["Analysis"])
app.include_router(sector.router,    prefix="/api", tags=["Sector"])
app.include_router(compare.router,   prefix="/api", tags=["Compare"])
app.include_router(watchlist.router, prefix="/api", tags=["Watchlist"])
app.include_router(guide.router,     prefix="/api", tags=["Guide"])
app.include_router(search.router,    prefix="/api", tags=["Search"])
app.include_router(alerts.router,    prefix="/api", tags=["Alerts"])

# DB init on startup
init_db()
```

### Design Decisions

| Decision | Reason |
|---|---|
| Dynamic CORS via `CORS_ORIGINS` env var | Support both local dev and production deployment |
| `init_db()` on startup | Auto-create tables + migrate JSON data on first run |
| `/api` prefix for all routes | Clean separation, easy proxy configuration |

---

## API Endpoints

### quote.py — Stock Data

| Method | Path | Function | Description |
|:---:|---|---|---|
| GET | `/api/quote/{ticker}` | `get_quote()` | Current quote |
| GET | `/api/fundamentals/{ticker}` | `get_fundamentals()` | Financial metrics |
| GET | `/api/technicals/{ticker}` | `get_technicals()` | Technical indicators (RSI, MACD, Bollinger) |
| GET | `/api/history/{ticker}` | `get_history()` | Chart data (OHLCV) |
| GET | `/api/premarket/{ticker}` | `get_premarket()` | Pre-market data |

### market.py — Market Data

| Method | Path | Function | Description |
|:---:|---|---|---|
| GET | `/api/market/indices` | `get_market_indices()` | 6 indices (SPY–VIX) |
| GET | `/api/market/movers` | `get_top_movers()` | Top 5 gainers/losers |
| GET | `/api/market/news` | `get_market_news()` | News headlines |

### analysis.py — AI Analysis

| Method | Path | Function | Description |
|:---:|---|---|---|
| POST | `/api/analysis/{ticker}` | `run_analysis()` | 5-agent AI analysis |

### sector.py — Sector Screening

| Method | Path | Function | Description |
|:---:|---|---|---|
| POST | `/api/sector/{name}` | `run_sector_screening()` | Sector AI screening |
| GET | `/api/themes` | `load_themes()` | Theme list |
| POST | `/api/themes` | `create_theme()` | Create theme |
| DELETE | `/api/themes/{name}` | `delete_theme()` | Delete theme |

### compare.py — Stock Comparison

| Method | Path | Function | Description |
|:---:|---|---|---|
| POST | `/api/compare` | `detect_comparison_type()` + `get_comparison_data()` | Comparison data |
| POST | `/api/compare/analyze` | `run_compare_analysis()` | AI comparison analysis |

### watchlist.py — Watchlist

| Method | Path | Function | Description |
|:---:|---|---|---|
| GET | `/api/watchlist` | `load_watchlist()` + `get_watchlist_quotes()` | List + quotes |
| POST | `/api/watchlist/{ticker}` | `add_to_watchlist()` | Add |
| DELETE | `/api/watchlist/{ticker}` | `remove_from_watchlist()` | Remove |

### guide.py — Guide Content

| Method | Path | Function | Description |
|:---:|---|---|---|
| GET | `/api/guide/categories` | `get_categories()` | Category list |
| GET | `/api/guide/{category}` | `get_topics()` | Topics per category |
| GET | `/api/guide/{category}/{index}` | `get_topic_detail()` | Topic detail |

---

## Error Handling

```python
from fastapi import HTTPException

@router.get("/quote/{ticker}")
def quote(ticker: str):
    result = get_quote(ticker)
    if result is None:
        raise HTTPException(status_code=404, detail=f"{ticker} not found")
    return result
```

| HTTP Status | Meaning | When Used |
|:---:|---|---|
| 200 | Success | Normal response |
| 404 | Not found | Ticker not found |
| 422 | Validation error | Invalid parameters |
| 500 | Server error | API call failure |

---

## Running

```bash
pip install fastapi uvicorn
uvicorn backend.main:app --reload --port 8000
# Auto API docs: http://localhost:8000/docs
```

---

## Phase 6 Skill Classification

| Skill | Classification | Reason |
|---|---|---|
| main.py | project-specific | FastAPI app setup + CORS + router registration |
| routers/* | project-specific | REST API wrappers for data/agents functions |

---

## Prerequisites & Dependencies

- Phase 1–5 all completed
- pip: `fastapi`, `uvicorn[standard]`
- Added to requirements.txt

---

## Development Notes

- data/ and agents/ code must NOT be modified — wrap only
- CORS: allow `localhost:3000` for dev, actual domain for production
- AI analysis (POST) takes 1–2 minutes — watch timeout settings
- Caching is handled by existing cache.py — no additional FastAPI-level caching needed

---

## Change Log

| Date | Description |
|---|---|
| 2026-04-06 | Initial creation (Streamlit UI-based) |
| 2026-04-14 | React transition — full rewrite as FastAPI backend |
| 2026-04-14 | ✅ Implementation complete — 9 routers + dynamic CORS + init_db() |
| 2026-04-15 | search.py, alerts.py routers added (Phase 10 integration) |

---
---

# Phase 6 — FastAPI 백엔드 `✅ 완료`

> 기존 data/agents 함수를 HTTP REST API로 노출하는 FastAPI 서버 구축

**완료일**: 2026-04-14
**상태**: ✅ 완료
**선행 조건**: Phase 5 완료 (모든 데이터/AI 로직 구현 완료)

---

## 개요

Phase 1~5에서 만든 Python 함수들은 직접 호출해야만 사용할 수 있다. React 프론트엔드가 이 함수들을 사용하려면, HTTP 요청으로 접근할 수 있는 API 서버가 필요하다. FastAPI로 기존 함수를 감싸서 REST API 엔드포인트를 만든다. data/agents 레이어는 수정하지 않고 감싸기만 한다.

---

## 완료 항목

| # | 모듈 | 상태 | 스킬 타입 |
|---|---|---|---|
| 1 | `backend/main.py` | ✅ | project-specific |
| 2 | `backend/routers/quote.py` | ✅ | project-specific |
| 3 | `backend/routers/market.py` | ✅ | project-specific |
| 4 | `backend/routers/analysis.py` | ✅ | project-specific |
| 5 | `backend/routers/sector.py` | ✅ | project-specific |
| 6 | `backend/routers/compare.py` | ✅ | project-specific |
| 7 | `backend/routers/watchlist.py` | ✅ | project-specific |
| 8 | `backend/routers/guide.py` | ✅ | project-specific |
| 9 | `backend/routers/search.py` | ✅ | project-specific |
| 10 | `backend/routers/alerts.py` | ✅ | project-specific |

---

## FastAPI 앱 (main.py)

### 목적
FastAPI 애플리케이션 생성, CORS 설정, 라우터 등록, 데이터베이스 초기화.

### 구현 파일
- `backend/main.py`

### 핵심 구조

```python
app = FastAPI(title="AI Stock Analyzer API", version="1.0")

# CORS — 로컬 개발 + Netlify 프로덕션 (환경변수로 동적 설정)
_origins = ["http://localhost:3000", "http://localhost:5173"]
_extra = os.environ.get("CORS_ORIGINS", "")
if _extra:
    _origins.extend([o.strip() for o in _extra.split(",") if o.strip()])

app.add_middleware(CORSMiddleware, allow_origins=_origins, ...)

# 라우터 등록
app.include_router(quote.router,     prefix="/api", tags=["Quote"])
# ... (9개 추가 라우터)

# DB 초기화 (테이블 생성 + JSON 마이그레이션)
init_db()
```

### 설계 결정 사항

| 결정 | 이유 |
|---|---|
| `CORS_ORIGINS` 환경변수로 동적 CORS | 로컬 개발과 프로덕션 배포 모두 지원 |
| 시작 시 `init_db()` 호출 | 첫 실행 시 테이블 자동 생성 + JSON 데이터 마이그레이션 |
| 모든 경로에 `/api` 접두사 | 깔끔한 분리, 프록시 설정 용이 |

---

## API 엔드포인트 목록

### quote.py — 종목 데이터

| 메서드 | 경로 | 호출 함수 | 설명 |
|:---:|---|---|---|
| GET | `/api/quote/{ticker}` | `get_quote()` | 현재 시세 |
| GET | `/api/fundamentals/{ticker}` | `get_fundamentals()` | 재무 지표 |
| GET | `/api/technicals/{ticker}` | `get_technicals()` | 기술 지표 (RSI, MACD, Bollinger) |
| GET | `/api/history/{ticker}` | `get_history()` | 차트 데이터 (OHLCV) |
| GET | `/api/premarket/{ticker}` | `get_premarket()` | 프리마켓 데이터 |

### market.py — 시장 데이터

| 메서드 | 경로 | 호출 함수 | 설명 |
|:---:|---|---|---|
| GET | `/api/market/indices` | `get_market_indices()` | 지수 6개 (SPY~VIX) |
| GET | `/api/market/movers` | `get_top_movers()` | 급등/급락 Top 5 |
| GET | `/api/market/news` | `get_market_news()` | 뉴스 헤드라인 |

### analysis.py — AI 분석

| 메서드 | 경로 | 호출 함수 | 설명 |
|:---:|---|---|---|
| POST | `/api/analysis/{ticker}` | `run_analysis()` | 5-Agent AI 분석 실행 |

### sector.py — 섹터 스크리닝

| 메서드 | 경로 | 호출 함수 | 설명 |
|:---:|---|---|---|
| POST | `/api/sector/{name}` | `run_sector_screening()` | 섹터 AI 스크리닝 |
| GET | `/api/themes` | `load_themes()` | 테마 목록 |
| POST | `/api/themes` | `create_theme()` | 테마 생성 |
| DELETE | `/api/themes/{name}` | `delete_theme()` | 테마 삭제 |

### compare.py — 종목 비교

| 메서드 | 경로 | 호출 함수 | 설명 |
|:---:|---|---|---|
| POST | `/api/compare` | `detect_comparison_type()` + `get_comparison_data()` | 비교 데이터 |
| POST | `/api/compare/analyze` | `run_compare_analysis()` | AI 비교 분석 |

### watchlist.py — 관심종목

| 메서드 | 경로 | 호출 함수 | 설명 |
|:---:|---|---|---|
| GET | `/api/watchlist` | `load_watchlist()` + `get_watchlist_quotes()` | 목록 + 시세 |
| POST | `/api/watchlist/{ticker}` | `add_to_watchlist()` | 추가 |
| DELETE | `/api/watchlist/{ticker}` | `remove_from_watchlist()` | 삭제 |

### guide.py — 가이드 콘텐츠

| 메서드 | 경로 | 호출 함수 | 설명 |
|:---:|---|---|---|
| GET | `/api/guide/categories` | `get_categories()` | 카테고리 목록 |
| GET | `/api/guide/{category}` | `get_topics()` | 카테고리별 주제 |
| GET | `/api/guide/{category}/{index}` | `get_topic_detail()` | 주제 상세 |

---

## 에러 처리

```python
from fastapi import HTTPException

@router.get("/quote/{ticker}")
def quote(ticker: str):
    result = get_quote(ticker)
    if result is None:
        raise HTTPException(status_code=404, detail=f"{ticker} not found")
    return result
```

| HTTP 상태 코드 | 의미 | 사용 시점 |
|:---:|---|---|
| 200 | 성공 | 정상 응답 |
| 404 | 없음 | 티커를 찾을 수 없을 때 |
| 422 | 유효성 오류 | 잘못된 파라미터 |
| 500 | 서버 오류 | API 호출 실패 등 |

---

## 실행 방법

```bash
pip install fastapi uvicorn
uvicorn backend.main:app --reload --port 8000
# 자동 API 문서: http://localhost:8000/docs
```

---

## Phase 6 스킬 범용/전용 분류

| 스킬 | 분류 | 이유 |
|---|---|---|
| main.py | project-specific | FastAPI 앱 설정 + CORS + 라우터 등록 |
| routers/* | project-specific | data/agents 함수의 REST API 래퍼 |

---

## 선행 조건 및 의존성

- Phase 1~5 전부 완료
- pip: `fastapi`, `uvicorn[standard]`
- requirements.txt에 추가

---

## 개발 시 주의사항

- data/, agents/ 코드는 **절대 수정하지 않는다** — 감싸기만
- CORS는 개발 시 `localhost:3000` 허용, 배포 시 실제 도메인으로 변경
- AI 분석(POST)은 1~2분 소요 — 타임아웃 설정 주의
- 캐싱은 기존 cache.py가 처리하므로 FastAPI 레벨에서 추가 캐싱 불필요

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-06 | 최초 작성 (Streamlit UI 기반) |
| 2026-04-14 | React 전환 — FastAPI 백엔드로 전면 재작성 |
| 2026-04-14 | ✅ 구현 완료 — 9개 라우터 + 동적 CORS + init_db() 연동 |
| 2026-04-15 | search.py, alerts.py 라우터 추가 (Phase 10 연계) |
