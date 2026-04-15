"""FastAPI 메인 앱 — CORS 설정 + 라우터 등록."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import quote, market, analysis, sector, compare, watchlist, guide, search, alerts
from data.database import init_db

app = FastAPI(
    title="AI Stock Analyzer API",
    version="1.0",
    description="Multi-Agent 미국 주식 종합 분석 시스템 API",
)

# CORS — 로컬 개발 + Netlify 프로덕션 도메인 허용
_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]
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

# 라우터 등록
app.include_router(quote.router, prefix="/api", tags=["Quote"])
app.include_router(market.router, prefix="/api", tags=["Market"])
app.include_router(analysis.router, prefix="/api", tags=["Analysis"])
app.include_router(sector.router, prefix="/api", tags=["Sector"])
app.include_router(compare.router, prefix="/api", tags=["Compare"])
app.include_router(watchlist.router, prefix="/api", tags=["Watchlist"])
app.include_router(guide.router, prefix="/api", tags=["Guide"])
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(alerts.router, prefix="/api", tags=["Alerts"])


# DB 초기화 (테이블 생성 + JSON 마이그레이션)
init_db()


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "AI Stock Analyzer API"}
