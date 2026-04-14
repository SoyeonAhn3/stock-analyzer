"""시장 개요 모듈 — 지수, 급등/급락, 뉴스.

사용법:
    from data.market_overview import get_market_indices, get_top_movers, get_market_news
    indices = get_market_indices()
    movers = get_top_movers()
    news = get_market_news(limit=5)
"""

import logging
from typing import Any, Optional

from data.api_client import api_client
from data.cache import cache

logger = logging.getLogger(__name__)

# 캐시 TTL (초)
_INDICES_TTL = 60     # 1분
_MOVERS_TTL = 300     # 5분
_NEWS_TTL = 300       # 5분

# 지수 매핑 (표시명 → yfinance 심볼)
INDEX_MAP = {
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW": "^DJI",
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "VIX": "^VIX",
}


def get_market_indices() -> Optional[list[dict[str, Any]]]:
    """주요 시장 지수 조회.

    Returns:
        [
            {"symbol": "S&P 500", "price": 5200.5, "change_percent": 0.82, ...},
            {"symbol": "NASDAQ", "price": 16300.2, "change_percent": 1.1, ...},
            ...
        ]
        실패 시 None.
    """
    cached = cache.get("market_indices", "overview")
    if cached is not None:
        return cached

    raw = api_client.get_market_indices()
    if raw is None:
        return None

    # raw = {"source": "yfinance", "indices": {"SPY": {...}, ...}}
    indices_data = raw.get("indices", raw)

    results = []
    for display_name, yf_symbol in INDEX_MAP.items():
        key = display_name.replace("&", "").replace(" ", "")
        api_key_map = {
            "SP500": "SPY", "NASDAQ": "NASDAQ", "DOW": "DOW",
            "BTC": "BTC", "ETH": "ETH", "VIX": "VIX",
        }
        api_key = api_key_map.get(key, key)
        idx_data = indices_data.get(api_key, {})
        if idx_data:
            price = idx_data.get("price")
            prev = idx_data.get("previous_close")
            change = round(price - prev, 2) if price and prev else idx_data.get("change")
            change_pct = idx_data.get("change_pct") or idx_data.get("change_percent")
            results.append({
                "symbol": display_name,
                "yf_symbol": yf_symbol,
                "price": price,
                "change": change,
                "change_percent": change_pct,
            })

    if results:
        cache.set("market_indices", "overview", results, _INDICES_TTL)

    return results if results else None


def get_top_movers() -> Optional[dict[str, Any]]:
    """급등 Top 5 + 급락 Top 5.

    Returns:
        {
            "gainers": [{"ticker": "...", "name": "...", "change_pct": 12.5, "price": ...}, ...],
            "losers": [{"ticker": "...", "name": "...", "change_pct": -8.3, "price": ...}, ...],
        }
        실패 시 None.
    """
    cached = cache.get("top_movers", "daily")
    if cached is not None:
        return cached

    try:
        from finvizfinance.screener.overview import Overview

        # 급등 Top 5
        gainers_screen = Overview()
        gainers_screen.set_filter(filters_dict={
            "Market Cap.": "+Mid (over $2bln)",
            "Change": "Up 5%",
        })
        gainers_screen.set_filter(signal="Top Gainers")
        gainers_df = gainers_screen.screener_view()

        gainers = []
        if gainers_df is not None and not gainers_df.empty:
            for _, row in gainers_df.head(5).iterrows():
                gainers.append({
                    "ticker": row.get("Ticker"),
                    "name": row.get("Company"),
                    "change_pct": row.get("Change"),
                    "price": row.get("Price"),
                    "volume": row.get("Volume"),
                })

        # 급락 Top 5
        losers_screen = Overview()
        losers_screen.set_filter(filters_dict={
            "Market Cap.": "+Mid (over $2bln)",
            "Change": "Down 5%",
        })
        losers_screen.set_filter(signal="Top Losers")
        losers_df = losers_screen.screener_view()

        losers = []
        if losers_df is not None and not losers_df.empty:
            for _, row in losers_df.head(5).iterrows():
                losers.append({
                    "ticker": row.get("Ticker"),
                    "name": row.get("Company"),
                    "change_pct": row.get("Change"),
                    "price": row.get("Price"),
                    "volume": row.get("Volume"),
                })

        result = {"gainers": gainers, "losers": losers}
        cache.set("top_movers", "daily", result, _MOVERS_TTL)
        return result

    except Exception as e:
        logger.warning("get_top_movers failed: %s", e)
        return None


def get_market_news(limit: int = 5) -> Optional[list[dict[str, Any]]]:
    """주요 시장 뉴스 헤드라인.

    Returns:
        [
            {"headline": "...", "source": "...", "url": "...", "datetime": ...},
            ...
        ]
        실패 시 None.
    """
    cached = cache.get("market_news", "general")
    if cached is not None:
        return cached

    raw = api_client.finnhub.get_market_news()
    if raw is None:
        return None

    articles = raw.get("articles", [])[:limit]
    if articles:
        cache.set("market_news", "general", articles, _NEWS_TTL)

    return articles if articles else None
