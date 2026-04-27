"""포트폴리오 API — 현재가 일괄조회, 메타데이터, 분석, 티커 검증."""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from data.portfolio import get_portfolio_quotes, get_ticker_meta, validate_ticker
from services.portfolio_calculator import run_analysis
from agents.portfolio_agent import generate_report

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Request Models ──────────────────────────────────────────────

class HoldingItem(BaseModel):
    ticker: str
    shares: int = Field(gt=0)
    avg_cost: float = Field(gt=0)
    currency: str = "USD"
    purchase_date: str | None = None
    memo: str | None = Field(None, max_length=100)


class QuotesRequest(BaseModel):
    tickers: list[str] = Field(min_length=1, max_length=50)


class AnalyzeRequest(BaseModel):
    holdings: list[HoldingItem] = Field(min_length=1, max_length=50)


# ── Endpoints ───────────────────────────────────────────────────

@router.post("/portfolio/quotes")
def portfolio_quotes(req: QuotesRequest):
    """보유 종목 현재가 일괄 조회."""
    tickers = [t.upper() for t in req.tickers]
    quotes = get_portfolio_quotes(tickers)

    if not quotes:
        raise HTTPException(502, "현재가를 조회할 수 없습니다. 잠시 후 재시도해주세요.")

    return {"quotes": quotes}


@router.get("/portfolio/meta/{ticker}")
def portfolio_meta(ticker: str):
    """종목 메타데이터 조회 (회사명, 섹터, 국가)."""
    meta = get_ticker_meta(ticker.upper())
    if meta is None:
        raise HTTPException(404, f"{ticker.upper()} 종목 정보를 찾을 수 없습니다.")
    return meta


@router.get("/portfolio/validate/{ticker}")
def portfolio_validate(ticker: str):
    """티커 유효성 검증."""
    return validate_ticker(ticker.upper())


@router.post("/portfolio/analyze")
async def portfolio_analyze(req: AnalyzeRequest):
    """포트폴리오 정량 분석 + AI 리포트.

    holdings를 받아서 분석 결과를 JSON으로 반환한다.
    서버에 사용자 데이터를 저장하지 않는다.
    """
    holdings = [
        {
            "ticker": h.ticker.upper(),
            "shares": h.shares,
            "avg_cost": h.avg_cost,
            "currency": h.currency,
            "purchase_date": h.purchase_date,
            "memo": h.memo,
        }
        for h in req.holdings
    ]

    try:
        analysis = run_analysis(holdings)
    except Exception as e:
        logger.error("Portfolio analysis failed: %s", e, exc_info=True)
        raise HTTPException(502, "포트폴리오 분석 중 오류가 발생했습니다.")

    perf = analysis.get("performance", {})
    summary = perf.get("summary", {})

    return {
        "summary": {
            "total_market_value": summary.get("total_market_value"),
            "total_cost_basis": summary.get("total_cost_basis"),
            "total_pnl": summary.get("total_pnl"),
            "total_pnl_pct": perf.get("total_return"),
            "holdings_count": len(req.holdings),
        },
        "analysis": analysis,
        "ai_report": generate_report(analysis),
    }
