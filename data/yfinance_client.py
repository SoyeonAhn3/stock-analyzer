"""yfinance 래퍼 — 주가, 재무제표, 히스토리, 시장 지수."""

import logging
from typing import Any, Optional

import yfinance as yf

from config.api_config import API_TIMEOUT

logger = logging.getLogger(__name__)


class YFinanceClient:
    """yfinance API 래퍼. API 키 불필요."""

    def __init__(self):
        self._call_count = 0

    @property
    def call_count(self) -> int:
        return self._call_count

    def get_quote(self, ticker: str) -> Optional[dict[str, Any]]:
        """현재 시세 조회."""
        try:
            self._call_count += 1
            stock = yf.Ticker(ticker)
            info = stock.fast_info
            return {
                "source": "yfinance",
                "ticker": ticker,
                "price": info.last_price,
                "previous_close": info.previous_close,
                "open": info.open,
                "day_high": info.day_high,
                "day_low": info.day_low,
                "volume": info.last_volume,
                "market_cap": info.market_cap,
            }
        except Exception as e:
            logger.warning("yfinance get_quote failed for %s: %s", ticker, e)
            return None

    def get_history(self, ticker: str, period: str = "1y", interval: str = "1d") -> Optional[dict[str, Any]]:
        """주가 히스토리 조회."""
        try:
            self._call_count += 1
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval, timeout=API_TIMEOUT)
            if df.empty:
                return None
            return {
                "source": "yfinance",
                "ticker": ticker,
                "period": period,
                "interval": interval,
                "data": df.reset_index().to_dict(orient="records"),
                "columns": list(df.columns),
            }
        except Exception as e:
            logger.warning("yfinance get_history failed for %s: %s", ticker, e)
            return None

    def get_fundamentals(self, ticker: str) -> Optional[dict[str, Any]]:
        """기업 재무 지표 조회."""
        try:
            self._call_count += 1
            stock = yf.Ticker(ticker)
            info = stock.info
            if not info or "symbol" not in info:
                return None
            return {
                "source": "yfinance",
                "ticker": ticker,
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "eps": info.get("trailingEps"),
                "peg_ratio": info.get("pegRatio"),
                "dividend_yield": info.get("dividendYield"),
                "debt_to_equity": info.get("debtToEquity"),
                "52w_high": info.get("fiftyTwoWeekHigh"),
                "52w_low": info.get("fiftyTwoWeekLow"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "employees": info.get("fullTimeEmployees"),
                "city": info.get("city"),
                "country": info.get("country"),
            }
        except Exception as e:
            logger.warning("yfinance get_fundamentals failed for %s: %s", ticker, e)
            return None

    def get_market_indices(self) -> Optional[dict[str, Any]]:
        """시장 지수 조회 (S&P500, NASDAQ, DOW, VIX)."""
        indices = {"SPY": "^GSPC", "NASDAQ": "^IXIC", "DOW": "^DJI", "VIX": "^VIX"}
        try:
            self._call_count += 1
            result = {}
            for name, symbol in indices.items():
                t = yf.Ticker(symbol)
                info = t.fast_info
                result[name] = {
                    "price": info.last_price,
                    "previous_close": info.previous_close,
                    "change_pct": round((info.last_price - info.previous_close) / info.previous_close * 100, 2),
                }
            return {"source": "yfinance", "indices": result}
        except Exception as e:
            logger.warning("yfinance get_market_indices failed: %s", e)
            return None
