"""포트폴리오 데이터 처리 — 현재가 일괄 조회 + 종목 메타 + 분석 요청 중계.

사용법:
    from data.portfolio import get_portfolio_quotes, get_ticker_meta
    quotes = get_portfolio_quotes(["AAPL", "NVDA", "MSFT"])
    meta = get_ticker_meta("AAPL")
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Optional

from data.quote import get_quote
from data.fundamentals import get_fundamentals

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=10)


def get_portfolio_quotes(tickers: list[str]) -> dict[str, dict[str, Any]]:
    """여러 종목의 현재가를 병렬로 조회한다.

    Returns:
        {"AAPL": {"price": 273.05, "change": 1.25, ...}, ...}
        조회 실패한 종목은 결과에서 제외.
    """
    results: dict[str, dict[str, Any]] = {}
    futures = {_executor.submit(get_quote, t): t for t in tickers}

    for future in as_completed(futures):
        ticker = futures[future]
        try:
            q = future.result()
            if q and q.get("price"):
                results[ticker] = q
            else:
                logger.warning("No quote data for %s", ticker)
        except Exception as e:
            logger.warning("Quote fetch failed for %s: %s", ticker, e)

    return results


def get_ticker_meta(ticker: str) -> Optional[dict[str, Any]]:
    """종목 메타데이터 조회 (회사명, 섹터, 국가 등)."""
    fund = get_fundamentals(ticker)
    if fund is None:
        return None

    return {
        "ticker": ticker,
        "name": _get_company_name(ticker),
        "sector": fund.get("sector"),
        "industry": fund.get("industry"),
        "country": fund.get("country"),
        "market_cap": fund.get("market_cap"),
    }


def validate_ticker(ticker: str) -> dict[str, Any]:
    """티커 유효성 검증. 현재가를 조회할 수 있으면 유효."""
    q = get_quote(ticker)
    if q and q.get("price"):
        meta = get_ticker_meta(ticker)
        return {
            "valid": True,
            "ticker": ticker,
            "name": meta.get("name", ticker) if meta else ticker,
            "sector": meta.get("sector") if meta else None,
        }
    return {"valid": False, "ticker": ticker}


def _get_company_name(ticker: str) -> str:
    """ticker_list에서 회사명을 찾는다. 없으면 티커 자체를 반환."""
    try:
        from data.ticker_list import TICKER_DB
        for t, name in TICKER_DB:
            if t == ticker:
                return name
    except Exception:
        pass
    return ticker
