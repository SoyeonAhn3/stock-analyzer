"""Finnhub 래퍼 — 시세, 뉴스, 애널리스트 추천."""

import logging
from typing import Any, Optional

import requests

from config.api_config import FINNHUB_API_KEY, FINNHUB_BASE_URL, API_TIMEOUT
from data.sanitize import mask_sensitive

logger = logging.getLogger(__name__)


class FinnhubClient:
    """Finnhub API 래퍼. 무료: 분당 60회."""

    def __init__(self):
        self._call_count = 0
        self._headers = {"X-Finnhub-Token": FINNHUB_API_KEY}

    def __repr__(self) -> str:
        return f"FinnhubClient(calls={self._call_count})"

    @property
    def call_count(self) -> int:
        return self._call_count

    def _get(self, endpoint: str, params: Optional[dict] = None) -> Optional[dict]:
        if not FINNHUB_API_KEY:
            logger.warning("Finnhub API key not set")
            return None
        try:
            self._call_count += 1
            url = f"{FINNHUB_BASE_URL}/{endpoint}"
            resp = requests.get(url, headers=self._headers, params=params or {}, timeout=API_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            if not data:
                return None
            return data
        except Exception as e:
            logger.warning("Finnhub %s failed: %s", endpoint, mask_sensitive(str(e)))
            return None

    def get_quote(self, ticker: str) -> Optional[dict[str, Any]]:
        """준실시간 시세 조회 (~15분 지연)."""
        data = self._get("quote", {"symbol": ticker})
        if not data or data.get("c", 0) == 0:
            return None
        return {
            "source": "finnhub",
            "ticker": ticker,
            "price": data["c"],
            "change": data["d"],
            "change_pct": data["dp"],
            "high": data["h"],
            "low": data["l"],
            "open": data["o"],
            "previous_close": data["pc"],
            "timestamp": data.get("t"),
        }

    def get_news(self, ticker: str, days: int = 7) -> Optional[dict[str, Any]]:
        """종목 뉴스 조회."""
        from datetime import datetime, timedelta
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        data = self._get("company-news", {"symbol": ticker, "from": start, "to": end})
        if not data:
            return None
        articles = [
            {
                "headline": a.get("headline"),
                "source": a.get("source"),
                "url": a.get("url"),
                "datetime": a.get("datetime"),
                "summary": a.get("summary"),
            }
            for a in data[:20]
        ]
        return {"source": "finnhub", "ticker": ticker, "articles": articles}

    def get_analyst_recommendations(self, ticker: str) -> Optional[dict[str, Any]]:
        """애널리스트 추천 조회."""
        data = self._get("stock/recommendation", {"symbol": ticker})
        if not data:
            return None
        latest = data[0] if data else {}
        return {
            "source": "finnhub",
            "ticker": ticker,
            "period": latest.get("period"),
            "strong_buy": latest.get("strongBuy", 0),
            "buy": latest.get("buy", 0),
            "hold": latest.get("hold", 0),
            "sell": latest.get("sell", 0),
            "strong_sell": latest.get("strongSell", 0),
        }

    def get_market_news(self, category: str = "general") -> Optional[dict[str, Any]]:
        """시장 뉴스 헤드라인."""
        data = self._get("news", {"category": category})
        if not data:
            return None
        articles = [
            {
                "headline": a.get("headline"),
                "source": a.get("source"),
                "url": a.get("url"),
                "datetime": a.get("datetime"),
            }
            for a in data[:5]
        ]
        return {"source": "finnhub", "articles": articles}
