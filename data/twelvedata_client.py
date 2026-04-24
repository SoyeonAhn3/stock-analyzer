"""Twelve Data 래퍼 — 기술적 지표 (RSI, MACD, 볼린저밴드 등)."""

import logging
from typing import Any, Optional

import requests

from config.api_config import TWELVEDATA_API_KEY, TWELVEDATA_BASE_URL, API_TIMEOUT
from data.sanitize import mask_sensitive

logger = logging.getLogger(__name__)


class TwelveDataClient:
    """Twelve Data API 래퍼. 무료: 일 800회."""

    def __init__(self):
        self._call_count = 0

    def __repr__(self) -> str:
        return f"TwelveDataClient(calls={self._call_count})"

    @property
    def call_count(self) -> int:
        return self._call_count

    def _get(self, endpoint: str, params: dict) -> Optional[Any]:
        if not TWELVEDATA_API_KEY:
            logger.warning("Twelve Data API key not set")
            return None
        try:
            self._call_count += 1
            params["apikey"] = TWELVEDATA_API_KEY
            url = f"{TWELVEDATA_BASE_URL}/{endpoint}"
            resp = requests.get(url, params=params, timeout=API_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            if "code" in data and data["code"] != 200:
                logger.warning("Twelve Data error: %s", data.get("message"))
                return None
            return data
        except Exception as e:
            logger.warning("Twelve Data %s failed: %s", endpoint, mask_sensitive(str(e)))
            return None

    def get_rsi(self, ticker: str, interval: str = "1day", time_period: int = 14) -> Optional[dict[str, Any]]:
        """RSI 조회."""
        data = self._get("rsi", {"symbol": ticker, "interval": interval, "time_period": time_period})
        if not data or "values" not in data:
            return None
        values = data["values"][:30]
        return {
            "source": "twelvedata",
            "ticker": ticker,
            "indicator": "RSI",
            "period": time_period,
            "values": [{"datetime": v["datetime"], "rsi": float(v["rsi"])} for v in values],
        }

    def get_macd(self, ticker: str, interval: str = "1day") -> Optional[dict[str, Any]]:
        """MACD 조회."""
        data = self._get("macd", {"symbol": ticker, "interval": interval})
        if not data or "values" not in data:
            return None
        values = data["values"][:30]
        return {
            "source": "twelvedata",
            "ticker": ticker,
            "indicator": "MACD",
            "values": [
                {
                    "datetime": v["datetime"],
                    "macd": float(v["macd"]),
                    "signal": float(v["macd_signal"]),
                    "histogram": float(v["macd_hist"]),
                }
                for v in values
            ],
        }

    def get_bbands(self, ticker: str, interval: str = "1day", time_period: int = 20) -> Optional[dict[str, Any]]:
        """볼린저밴드 조회."""
        data = self._get("bbands", {"symbol": ticker, "interval": interval, "time_period": time_period})
        if not data or "values" not in data:
            return None
        values = data["values"][:30]
        return {
            "source": "twelvedata",
            "ticker": ticker,
            "indicator": "BBANDS",
            "values": [
                {
                    "datetime": v["datetime"],
                    "upper": float(v["upper_band"]),
                    "middle": float(v["middle_band"]),
                    "lower": float(v["lower_band"]),
                }
                for v in values
            ],
        }

    def get_ma(self, ticker: str, interval: str = "1day", time_period: int = 50) -> Optional[dict[str, Any]]:
        """이동평균 조회."""
        data = self._get("ma", {"symbol": ticker, "interval": interval, "time_period": time_period})
        if not data or "values" not in data:
            return None
        values = data["values"][:30]
        return {
            "source": "twelvedata",
            "ticker": ticker,
            "indicator": f"MA{time_period}",
            "values": [{"datetime": v["datetime"], "ma": float(v["ma"])} for v in values],
        }

    def get_history(self, ticker: str, interval: str = "1day", outputsize: int = 252) -> Optional[dict[str, Any]]:
        """주가 히스토리 (폴백용)."""
        data = self._get("time_series", {"symbol": ticker, "interval": interval, "outputsize": outputsize})
        if not data or "values" not in data:
            return None
        return {
            "source": "twelvedata",
            "ticker": ticker,
            "interval": interval,
            "data": data["values"],
        }
