"""종목 데이터 엔드포인트 — 시세, 재무, 기술지표, 차트, 프리마켓."""

from fastapi import APIRouter, HTTPException

from data.quote import get_quote, get_premarket
from data.fundamentals import get_fundamentals
from data.technicals import get_technicals
from data.history import get_history

router = APIRouter()


@router.get("/quote/{ticker}")
def quote(ticker: str):
    """현재 시세 조회."""
    result = get_quote(ticker.upper())
    if result is None:
        raise HTTPException(404, f"Quote not found for {ticker}")
    return result


@router.get("/fundamentals/{ticker}")
def fundamentals(ticker: str):
    """재무 지표 조회 (PE, EPS, Market Cap 등)."""
    result = get_fundamentals(ticker.upper())
    if result is None:
        raise HTTPException(404, f"Fundamentals not found for {ticker}")
    return result


@router.get("/technicals/{ticker}")
def technicals(ticker: str):
    """기술 지표 조회 (RSI, MACD, Bollinger, MA)."""
    result = get_technicals(ticker.upper())
    if result is None:
        raise HTTPException(404, f"Technicals not found for {ticker}")
    return result


@router.get("/history/{ticker}")
def history(ticker: str, period: str = "1Y"):
    """주가 히스토리 (OHLCV + MA). period: 1D,1W,1M,3M,6M,1Y,5Y"""
    df = get_history(ticker.upper(), period=period)
    if df is None:
        raise HTTPException(404, f"History not found for {ticker}")
    return df.to_dict(orient="records")


@router.get("/premarket/{ticker}")
def premarket(ticker: str):
    """프리마켓/애프터마켓 데이터."""
    result = get_premarket(ticker.upper())
    if result is None:
        raise HTTPException(404, f"Premarket data not available for {ticker}")
    return result
