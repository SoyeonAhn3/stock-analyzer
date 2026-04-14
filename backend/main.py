"""FastAPI 메인 앱 — CORS 설정 + 라우터 등록."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import quote, market, analysis, sector, compare, watchlist, guide, search, alerts
from data.database import init_db

app = FastAPI(
    title="AI Stock Analyzer API",
    version="1.0",
    description="Multi-Agent 미국 주식 종합 분석 시스템 API",
)

# CORS — React 개발 서버(localhost:5173)에서 접근 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",  # Vite 기본 포트
    ],
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
