"""관심종목 CRUD 엔드포인트."""

from fastapi import APIRouter, HTTPException

from data.watchlist import (
    load_watchlist,
    add_to_watchlist,
    remove_from_watchlist,
    get_watchlist_quotes,
)

router = APIRouter()


@router.get("/watchlist")
def watchlist_get():
    """관심종목 목록 + 시세 조회."""
    tickers = load_watchlist()
    quotes = get_watchlist_quotes(tickers) if tickers else []
    return {
        "tickers": tickers,
        "quotes": quotes,
    }


@router.post("/watchlist/{ticker}")
def watchlist_add(ticker: str):
    """관심종목 추가."""
    add_to_watchlist(ticker.upper())
    return {"status": "added", "ticker": ticker.upper()}


@router.delete("/watchlist/{ticker}")
def watchlist_remove(ticker: str):
    """관심종목 삭제."""
    try:
        remove_from_watchlist(ticker.upper())
        return {"status": "removed", "ticker": ticker.upper()}
    except KeyError:
        raise HTTPException(404, f"{ticker.upper()} not in watchlist")
