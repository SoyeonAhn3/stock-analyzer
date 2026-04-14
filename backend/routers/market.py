"""시장 데이터 엔드포인트 — 지수, 급등락, 뉴스."""

from fastapi import APIRouter, HTTPException

from data.market_overview import get_market_indices, get_top_movers, get_market_news

router = APIRouter()


@router.get("/market/indices")
def indices():
    """주요 시장 지수 조회 (SPY, QQQ, DIA, BTC, ETH, VIX)."""
    result = get_market_indices()
    if result is None:
        raise HTTPException(503, "Market indices temporarily unavailable")
    return result


@router.get("/market/movers")
def movers():
    """급등 Top 5 + 급락 Top 5."""
    result = get_top_movers()
    if result is None:
        raise HTTPException(503, "Top movers temporarily unavailable")
    return result


@router.get("/market/news")
def news(limit: int = 5):
    """시장 뉴스 헤드라인."""
    result = get_market_news(limit=limit)
    if result is None:
        raise HTTPException(503, "Market news temporarily unavailable")
    return result
