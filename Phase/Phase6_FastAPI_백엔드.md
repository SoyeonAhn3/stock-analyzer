# Phase 6 — FastAPI 백엔드 `✅ 완료`

> 기존 data/agents 함수를 HTTP API로 노출하는 FastAPI 서버 구축

**상태**: ✅ 완료
**선행 조건**: Phase 5 완료 (모든 데이터/AI 로직 구현 완료)
**기술 스택**: Python, FastAPI, Uvicorn, Pydantic

---

## 개요

Phase 1~5에서 만든 Python 함수들은 직접 호출해야만 쓸 수 있다. React 프론트엔드가 이 함수들을 사용하려면, HTTP 요청으로 접근할 수 있는 **API 서버**가 필요하다. FastAPI로 기존 함수를 감싸서 REST API 엔드포인트를 만든다.

### Java 비유

```
Java Spring의 Controller = FastAPI의 Router
Java Spring의 Service    = 기존 data/, agents/ 모듈
Java Spring의 DTO        = Pydantic 모델 (schemas.py)
```

---

## 완료 예정 / 완료 항목

| # | 모듈 | 상태 | 설명 |
|---|---|---|---|
| # | 모듈 | 상태 | 설명 |
|---|---|---|---|
| 1 | `backend/main.py` | ✅ | FastAPI 앱 생성 + CORS(동적) + 라우터 등록 + DB 초기화 |
| 2 | `backend/routers/quote.py` | ✅ | 시세/재무/기술지표/차트 엔드포인트 |
| 3 | `backend/routers/market.py` | ✅ | 시장 지수/급등락/뉴스 엔드포인트 |
| 4 | `backend/routers/analysis.py` | ✅ | AI 분석 실행 엔드포인트 (async) |
| 5 | `backend/routers/sector.py` | ✅ | 섹터 스크리닝/테마 엔드포인트 |
| 6 | `backend/routers/compare.py` | ✅ | 종목 비교 엔드포인트 |
| 7 | `backend/routers/watchlist.py` | ✅ | 관심종목 CRUD 엔드포인트 |
| 8 | `backend/routers/guide.py` | ✅ | 가이드 콘텐츠 엔드포인트 |
| 9 | `backend/routers/search.py` | ✅ | 검색 자동완성 엔드포인트 (Phase 10 연계) |
| 10 | `backend/routers/alerts.py` | ✅ | 가격 알림 CRUD 엔드포인트 (Phase 10 연계) |

---

## 프로젝트 구조

```
stock-analyzer/
├── data/                    ← 터치 안 함 (Phase 1~5)
├── agents/                  ← 터치 안 함 (Phase 1~5)
├── config/                  ← 터치 안 함
├── utils/                   ← 터치 안 함
│
├── backend/                 ← 🆕 이 Phase에서 생성
│   ├── __init__.py
│   ├── main.py              FastAPI 앱 + CORS + 라우터 등록
│   ├── schemas.py           Pydantic 모델 (요청/응답 타입)
│   └── routers/
│       ├── __init__.py
│       ├── quote.py         /api/quote/* (시세, 재무, 기술지표, 차트)
│       ├── market.py        /api/market/* (지수, 급등락, 뉴스)
│       ├── analysis.py      /api/analysis/* (AI 분석)
│       ├── sector.py        /api/sector/* (섹터 스크리닝, 테마)
│       ├── compare.py       /api/compare/* (종목 비교)
│       ├── watchlist.py     /api/watchlist/* (관심종목 CRUD)
│       └── guide.py         /api/guide/* (가이드 콘텐츠)
│
└── requirements.txt         ← fastapi, uvicorn 추가
```

---

## FastAPI 앱 (main.py)

### 핵심 코드 구조

```python
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import quote, market, analysis, sector, compare, watchlist, guide, search, alerts
from data.database import init_db

app = FastAPI(title="AI Stock Analyzer API", version="1.0",
              description="Multi-Agent 미국 주식 종합 분석 시스템 API")

# CORS — 로컬 개발 + Netlify 프로덕션 도메인 허용 (환경변수로 동적 설정)
_origins = ["http://localhost:3000", "http://localhost:5173"]
_extra = os.environ.get("CORS_ORIGINS", "")
if _extra:
    _origins.extend([o.strip() for o in _extra.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록 (태그 포함)
app.include_router(quote.router,     prefix="/api", tags=["Quote"])
app.include_router(market.router,    prefix="/api", tags=["Market"])
app.include_router(analysis.router,  prefix="/api", tags=["Analysis"])
app.include_router(sector.router,    prefix="/api", tags=["Sector"])
app.include_router(compare.router,   prefix="/api", tags=["Compare"])
app.include_router(watchlist.router, prefix="/api", tags=["Watchlist"])
app.include_router(guide.router,     prefix="/api", tags=["Guide"])
app.include_router(search.router,    prefix="/api", tags=["Search"])
app.include_router(alerts.router,    prefix="/api", tags=["Alerts"])

# DB 초기화 (테이블 생성 + JSON 마이그레이션)
init_db()
```

### CORS란?
브라우저 보안 정책상, React(localhost:3000)에서 FastAPI(localhost:8000)로 요청하면 기본적으로 차단된다. CORS 설정은 "이 주소에서 오는 요청은 허용해" 라고 서버에 알려주는 것이다.

---

## API 엔드포인트 목록

### quote.py — 종목 데이터

| 메서드 | 경로 | 호출 함수 | 설명 |
|:------:|------|----------|------|
| GET | `/api/quote/{ticker}` | `get_quote()` | 현재 시세 |
| GET | `/api/fundamentals/{ticker}` | `get_fundamentals()` | 재무 지표 |
| GET | `/api/technicals/{ticker}` | `get_technicals()` | 기술 지표 (RSI, MACD, Bollinger) |
| GET | `/api/history/{ticker}` | `get_history()` | 차트 데이터 (OHLCV) |
| GET | `/api/premarket/{ticker}` | `get_premarket()` | 프리마켓 데이터 |

**특이사항**: `get_history()`는 DataFrame을 반환하므로 JSON 변환 필요:
```python
@router.get("/history/{ticker}")
def history(ticker: str, period: str = "1Y"):
    df = get_history(ticker, period)
    if df is None:
        raise HTTPException(404, "No history data")
    return df.to_dict(orient="records")
```

### market.py — 시장 데이터

| 메서드 | 경로 | 호출 함수 | 설명 |
|:------:|------|----------|------|
| GET | `/api/market/indices` | `get_market_indices()` | 지수 6개 (SPY~VIX) |
| GET | `/api/market/movers` | `get_top_movers()` | 급등/급락 Top 5 |
| GET | `/api/market/news` | `get_market_news()` | 뉴스 헤드라인 |

### analysis.py — AI 분석

| 메서드 | 경로 | 호출 함수 | 설명 |
|:------:|------|----------|------|
| POST | `/api/analysis/{ticker}` | `run_analysis()` | AI 5-Agent 분석 실행 |

**특이사항**: `run_analysis()`는 async 함수. 분석에 1~2분 걸리므로:
- 방법 A: 단순 await (클라이언트가 1~2분 대기)
- 방법 B: WebSocket으로 진행 상태 실시간 전송 (Phase 9에서 개선)
- Phase 6에서는 **방법 A**로 단순 구현

```python
@router.post("/analysis/{ticker}")
async def analyze(ticker: str):
    # quick_look 데이터 먼저 수집
    quick_look_data = {
        "quote": get_quote(ticker),
        "fundamentals": get_fundamentals(ticker),
        "technicals": get_technicals(ticker),
    }
    result = await run_analysis(quick_look_data)
    return result
```

### sector.py — 섹터 스크리닝

| 메서드 | 경로 | 호출 함수 | 설명 |
|:------:|------|----------|------|
| POST | `/api/sector/{name}` | `run_sector_screening()` | 섹터 AI 스크리닝 |
| GET | `/api/themes` | `load_themes()` | 테마 목록 |
| POST | `/api/themes` | `create_theme()` | 테마 생성 |
| DELETE | `/api/themes/{name}` | `delete_theme()` | 테마 삭제 |

### compare.py — 종목 비교

| 메서드 | 경로 | 호출 함수 | 설명 |
|:------:|------|----------|------|
| POST | `/api/compare` | `detect_comparison_type()` + `get_comparison_data()` | 비교 데이터 |
| POST | `/api/compare/analyze` | `run_compare_analysis()` | AI 비교 분석 |

### watchlist.py — 관심종목

| 메서드 | 경로 | 호출 함수 | 설명 |
|:------:|------|----------|------|
| GET | `/api/watchlist` | `load_watchlist()` + `get_watchlist_quotes()` | 목록 + 시세 |
| POST | `/api/watchlist/{ticker}` | `add_to_watchlist()` | 추가 |
| DELETE | `/api/watchlist/{ticker}` | `remove_from_watchlist()` | 삭제 |

### guide.py — 가이드 콘텐츠

| 메서드 | 경로 | 호출 함수 | 설명 |
|:------:|------|----------|------|
| GET | `/api/guide/categories` | `get_categories()` | 카테고리 목록 |
| GET | `/api/guide/{category}` | `get_topics()` | 카테고리별 주제 |
| GET | `/api/guide/{category}/{index}` | `get_topic_detail()` | 주제 상세 |

---

## Pydantic 모델 (schemas.py)

Java의 DTO와 같은 역할. API 응답의 타입을 명시적으로 정의:

```python
from pydantic import BaseModel
from typing import Optional

class QuoteResponse(BaseModel):
    ticker: str
    price: float
    change: float
    change_percent: float
    volume: Optional[float]
    market_cap: Optional[float]
    source: str

class AnalysisResponse(BaseModel):
    agent: str
    status: str    # "success" | "partial" | "failed"
    verdict: str   # "BUY" | "HOLD" | "SELL"
    confidence: str  # "high" | "medium" | "low"
    summary: str
    # ...
```

---

## 실행 방법

```bash
# 설치
pip install fastapi uvicorn

# 서버 실행
uvicorn backend.main:app --reload --port 8000

# 자동 API 문서 확인 (브라우저)
# http://localhost:8000/docs
```

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
|:--------------:|------|----------|
| 200 | 성공 | 정상 응답 |
| 404 | 없음 | 티커를 찾을 수 없을 때 |
| 422 | 유효성 오류 | 잘못된 파라미터 |
| 500 | 서버 오류 | API 호출 실패 등 |

---

## 테스트 방법

1. **자동 문서**: `localhost:8000/docs`에서 모든 API를 브라우저에서 직접 테스트
2. **curl**: `curl localhost:8000/api/quote/NVDA`
3. **pytest**: 기존 테스트 + API 엔드포인트 테스트 추가

---

## 선행 조건 및 의존성

- Phase 1~5 전부 완료
- pip: `fastapi`, `uvicorn[standard]`
- requirements.txt에 추가

---

## 개발 시 주의사항

- data/, agents/ 코드는 **절대 수정하지 않는다** — 감싸기만
- CORS는 개발 시 `localhost:3000` 허용, 배포 시 실제 도메인으로 변경
- AI 분석(POST)은 시간이 오래 걸림 — 타임아웃 설정 주의
- 캐싱은 기존 cache.py가 처리하므로 FastAPI 레벨에서 추가 캐싱 불필요

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-06 | 최초 작성 (Streamlit UI 기반) |
| 2026-04-14 | React 전환 결정 — FastAPI 백엔드로 전면 재작성 |
| 2026-04-14 | ✅ 구현 완료 — 9개 라우터 + CORS 동적 설정 + SQLite init_db() 연동 |
| 2026-04-15 | search.py, alerts.py 라우터 추가 반영 (Phase 10 연계) |
