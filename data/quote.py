"""시세 수집 모듈 — 현재가, 등락, 거래량, 장전/장후 시세.

사용법:
    from data.quote import get_quote, get_premarket
    q = get_quote("NVDA")
    # {"price": 120.5, "change": 2.2, "change_percent": 1.86, ...}
"""

import logging
from typing import Any, Optional

from data.api_client import api_client

logger = logging.getLogger(__name__)


def get_quote(ticker: str) -> Optional[dict[str, Any]]:
    """현재 시세 조회. Finnhub → yfinance 폴백.

    Returns:
        {
            "ticker", "price", "change", "change_percent",
            "volume", "day_high", "day_low", "open", "previous_close",
            "market_cap", "source"
        }
        실패 시 None.
    """
    raw = api_client.get_quote(ticker)
    if raw is None:
        return None

    price = raw.get("price", 0)
    prev_close = raw.get("previous_close", 0)

    if raw.get("change") is not None:
        change = raw["change"]
        change_pct = raw.get("change_pct", raw.get("change_percent", 0))
    elif prev_close and price:
        change = round(price - prev_close, 4)
        change_pct = round(change / prev_close * 100, 2) if prev_close else 0
    else:
        change = 0
        change_pct = 0

    return {
        "ticker": ticker,
        "price": price,
        "change": change,
        "change_percent": change_pct,
        "volume": raw.get("volume", raw.get("last_volume")),
        "day_high": raw.get("day_high", raw.get("high")),
        "day_low": raw.get("day_low", raw.get("low")),
        "open": raw.get("open"),
        "previous_close": prev_close,
        "market_cap": raw.get("market_cap"),
        "source": raw.get("source"),
    }


def get_premarket(ticker: str) -> Optional[dict[str, Any]]:
    """장 전/장 후 시세. yfinance에서 조회, 없으면 None."""
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info = stock.info
        pre = info.get("preMarketPrice")
        post = info.get("postMarketPrice")
        if not pre and not post:
            return None
        return {
            "ticker": ticker,
            "pre_market_price": pre,
            "pre_market_change_pct": info.get("preMarketChangePercent"),
            "post_market_price": post,
            "post_market_change_pct": info.get("postMarketChangePercent"),
        }
    except Exception as e:
        logger.warning("get_premarket failed for %s: %s", ticker, e)
        return None
