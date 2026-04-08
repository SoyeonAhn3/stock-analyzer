"""FRED 래퍼 — 연준 금리, CPI, 실업률 등 매크로 경제 지표."""

import logging
from typing import Any, Optional

import requests

from config.api_config import FRED_API_KEY, FRED_BASE_URL, API_TIMEOUT

logger = logging.getLogger(__name__)

# 주요 FRED 시리즈 ID
SERIES_MAP = {
    "fed_rate": "FEDFUNDS",
    "cpi": "CPIAUCSL",
    "unemployment": "UNRATE",
    "gdp": "GDP",
    "treasury_10y": "DGS10",
    "treasury_2y": "DGS2",
    "inflation_expectation": "T5YIE",
}


class FREDClient:
    """FRED API 래퍼. 무료 (무제한)."""

    def __init__(self):
        self._call_count = 0

    @property
    def call_count(self) -> int:
        return self._call_count

    def _get_series(self, series_id: str, limit: int = 12) -> Optional[list[dict]]:
        if not FRED_API_KEY:
            logger.warning("FRED API key not set")
            return None
        try:
            self._call_count += 1
            params = {
                "series_id": series_id,
                "api_key": FRED_API_KEY,
                "file_type": "json",
                "sort_order": "desc",
                "limit": limit,
            }
            resp = requests.get(f"{FRED_BASE_URL}/series/observations", params=params, timeout=API_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            observations = data.get("observations", [])
            return [{"date": o["date"], "value": float(o["value"])} for o in observations if o["value"] != "."]
        except Exception as e:
            logger.warning("FRED %s failed: %s", series_id, e)
            return None

    def get_fed_rate(self) -> Optional[dict[str, Any]]:
        """연준 기준금리."""
        data = self._get_series(SERIES_MAP["fed_rate"], limit=6)
        if not data:
            return None
        return {"source": "fred", "indicator": "fed_rate", "latest": data[0], "history": data}

    def get_cpi(self) -> Optional[dict[str, Any]]:
        """소비자물가지수."""
        data = self._get_series(SERIES_MAP["cpi"], limit=12)
        if not data:
            return None
        return {"source": "fred", "indicator": "cpi", "latest": data[0], "history": data}

    def get_unemployment(self) -> Optional[dict[str, Any]]:
        """실업률."""
        data = self._get_series(SERIES_MAP["unemployment"], limit=12)
        if not data:
            return None
        return {"source": "fred", "indicator": "unemployment", "latest": data[0], "history": data}

    def get_treasury_spread(self) -> Optional[dict[str, Any]]:
        """10Y-2Y 국채 스프레드 (경기침체 지표)."""
        t10 = self._get_series(SERIES_MAP["treasury_10y"], limit=1)
        t2 = self._get_series(SERIES_MAP["treasury_2y"], limit=1)
        if not t10 or not t2:
            return None
        spread = round(t10[0]["value"] - t2[0]["value"], 3)
        return {
            "source": "fred",
            "indicator": "treasury_spread_10y_2y",
            "spread": spread,
            "treasury_10y": t10[0]["value"],
            "treasury_2y": t2[0]["value"],
            "inverted": spread < 0,
        }

    def get_macro_summary(self) -> Optional[dict[str, Any]]:
        """매크로 지표 종합 요약."""
        fed = self.get_fed_rate()
        cpi = self.get_cpi()
        unemp = self.get_unemployment()
        spread = self.get_treasury_spread()
        if not any([fed, cpi, unemp, spread]):
            return None
        return {
            "source": "fred",
            "fed_rate": fed["latest"] if fed else None,
            "cpi": cpi["latest"] if cpi else None,
            "unemployment": unemp["latest"] if unemp else None,
            "treasury_spread": spread if spread else None,
        }
