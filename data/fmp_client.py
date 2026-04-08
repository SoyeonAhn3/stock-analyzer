"""FMP (Financial Modeling Prep) 래퍼 — 섹터 스크리닝, 재무제표."""

import logging
from typing import Any, Optional

import requests

from config.api_config import FMP_API_KEY, FMP_BASE_URL, API_TIMEOUT

logger = logging.getLogger(__name__)


class FMPClient:
    """FMP API 래퍼. 무료: 일 250회."""

    def __init__(self):
        self._call_count = 0

    @property
    def call_count(self) -> int:
        return self._call_count

    def _get(self, endpoint: str, params: Optional[dict] = None) -> Optional[Any]:
        if not FMP_API_KEY:
            logger.warning("FMP API key not set")
            return None
        try:
            self._call_count += 1
            params = params or {}
            params["apikey"] = FMP_API_KEY
            url = f"{FMP_BASE_URL}/{endpoint}"
            resp = requests.get(url, params=params, timeout=API_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict) and "Error Message" in data:
                logger.warning("FMP error: %s", data["Error Message"])
                return None
            return data
        except Exception as e:
            logger.warning("FMP %s failed: %s", endpoint, e)
            return None

    def get_fundamentals(self, ticker: str) -> Optional[dict[str, Any]]:
        """기업 재무 지표 (폴백용)."""
        data = self._get(f"profile/{ticker}")
        if not data or not isinstance(data, list) or len(data) == 0:
            return None
        p = data[0]
        return {
            "source": "fmp",
            "ticker": ticker,
            "market_cap": p.get("mktCap"),
            "pe_ratio": p.get("pe"),
            "eps": p.get("eps"),
            "sector": p.get("sector"),
            "industry": p.get("industry"),
            "dividend_yield": p.get("lastDiv"),
            "52w_high": p.get("range", "").split("-")[-1].strip() if p.get("range") else None,
            "52w_low": p.get("range", "").split("-")[0].strip() if p.get("range") else None,
            "employees": p.get("fullTimeEmployees"),
            "country": p.get("country"),
        }

    def screen_stocks(self, sector: str = None, market_cap_min: int = None,
                      market_cap_max: int = None, limit: int = 50) -> Optional[dict[str, Any]]:
        """섹터 스크리닝."""
        params = {"limit": limit}
        if sector:
            params["sector"] = sector
        if market_cap_min:
            params["marketCapMoreThan"] = market_cap_min
        if market_cap_max:
            params["marketCapLowerThan"] = market_cap_max

        data = self._get("stock-screener", params)
        if not data:
            return None
        stocks = [
            {
                "ticker": s.get("symbol"),
                "name": s.get("companyName"),
                "market_cap": s.get("marketCap"),
                "sector": s.get("sector"),
                "industry": s.get("industry"),
                "price": s.get("price"),
                "volume": s.get("volume"),
            }
            for s in data
        ]
        return {"source": "fmp", "sector": sector, "stocks": stocks}

    def get_sector_pe(self, sector: str) -> Optional[dict[str, Any]]:
        """섹터 평균 PE 조회."""
        data = self._get("stock-screener", {"sector": sector, "limit": 10})
        if not data:
            return None
        pe_values = [s["pe"] for s in data if s.get("pe") and s["pe"] > 0]
        if not pe_values:
            return None
        pe_values.sort()
        mid = len(pe_values) // 2
        median_pe = pe_values[mid] if len(pe_values) % 2 else (pe_values[mid - 1] + pe_values[mid]) / 2
        return {
            "source": "fmp",
            "sector": sector,
            "median_pe": round(median_pe, 2),
            "sample_size": len(pe_values),
        }

    def get_income_statement(self, ticker: str, period: str = "annual", limit: int = 4) -> Optional[dict[str, Any]]:
        """손익계산서 조회."""
        data = self._get(f"income-statement/{ticker}", {"period": period, "limit": limit})
        if not data:
            return None
        return {"source": "fmp", "ticker": ticker, "statements": data}
