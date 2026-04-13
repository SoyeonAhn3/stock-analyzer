"""통합 API 클라이언트 — 폴백 로직 포함.

사용법:
    from data.api_client import api_client
    result = api_client.get_quote("NVDA")
    # result["source"] == "finnhub" or "yfinance"
    # 전부 실패 시 None 반환
"""

import logging
from typing import Any, Optional

from config.api_config import FALLBACK_PRIORITY, CACHE_TTL
from data.cache import cache
from data.yfinance_client import YFinanceClient
from data.finnhub_client import FinnhubClient
from data.twelvedata_client import TwelveDataClient
from data.fmp_client import FMPClient
from data.fred_client import FREDClient
from data.finviz_client import FinvizClient

logger = logging.getLogger(__name__)


class APIClient:
    """통합 API 클라이언트.

    데이터 유형별 우선순위에 따라 API를 호출하고,
    1순위 실패 시 자동으로 2순위로 폴백한다.
    전부 실패하면 None을 반환한다 ("데이터 없음").
    """

    def __init__(self):
        self.yfinance = YFinanceClient()
        self.finnhub = FinnhubClient()
        self.twelvedata = TwelveDataClient()
        self.fmp = FMPClient()
        self.fred = FREDClient()
        self.finviz = FinvizClient()

        self._clients = {
            "yfinance": self.yfinance,
            "finnhub": self.finnhub,
            "twelvedata": self.twelvedata,
            "fmp": self.fmp,
            "fred": self.fred,
            "finviz": self.finviz,
        }

    def _try_fallback(self, data_type: str, method_name: str, cache_category: str = "quick_look", **kwargs) -> Optional[dict[str, Any]]:
        """폴백 우선순위에 따라 순서대로 시도."""
        # Check cache first
        ticker = kwargs.get("ticker", "")
        cached = cache.get(f"{data_type}_{method_name}", ticker, **{k: v for k, v in kwargs.items() if k != "ticker"})
        if cached is not None:
            return cached

        sources = FALLBACK_PRIORITY.get(data_type, [])
        for source_name in sources:
            if source_name == "python_calc":
                continue  # Python 계산 폴백은 호출자가 처리
            client = self._clients.get(source_name)
            if client is None:
                continue
            method = getattr(client, method_name, None)
            if method is None:
                continue
            try:
                result = method(**kwargs)
                if result is not None:
                    ttl = CACHE_TTL.get(cache_category, CACHE_TTL["quick_look"])
                    cache.set(f"{data_type}_{method_name}", ticker, result, ttl,
                              **{k: v for k, v in kwargs.items() if k != "ticker"})
                    return result
            except Exception as e:
                logger.warning("Fallback %s.%s failed: %s", source_name, method_name, e)
                continue

        logger.info("All sources failed for %s.%s(%s)", data_type, method_name, kwargs)
        return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_quote(self, ticker: str) -> Optional[dict[str, Any]]:
        """시세 조회. Finnhub → yfinance. 캐시 TTL 60초."""
        return self._try_fallback("quote", "get_quote", cache_category="quote", ticker=ticker)

    def get_history(self, ticker: str, period: str = "1y", interval: str = "1d") -> Optional[dict[str, Any]]:
        """주가 히스토리. yfinance → Twelve Data."""
        return self._try_fallback("history", "get_history", ticker=ticker, period=period, interval=interval)

    def get_fundamentals(self, ticker: str) -> Optional[dict[str, Any]]:
        """기업 재무 지표. yfinance → FMP."""
        return self._try_fallback("fundamentals", "get_fundamentals", ticker=ticker)

    def get_technicals(self, ticker: str) -> Optional[dict[str, Any]]:
        """기술적 지표 종합. Twelve Data 1순위, 실패 시 None (호출자가 Python 계산)."""
        cached = cache.get("technicals", ticker)
        if cached is not None:
            return cached

        try:
            rsi = self.twelvedata.get_rsi(ticker)
            macd = self.twelvedata.get_macd(ticker)
            bbands = self.twelvedata.get_bbands(ticker)
            ma50 = self.twelvedata.get_ma(ticker, time_period=50)
            ma200 = self.twelvedata.get_ma(ticker, time_period=200)

            if not any([rsi, macd, bbands]):
                return None

            result = {
                "source": "twelvedata",
                "ticker": ticker,
                "rsi": rsi,
                "macd": macd,
                "bbands": bbands,
                "ma50": ma50,
                "ma200": ma200,
            }
            cache.set("technicals", ticker, result, CACHE_TTL["quick_look"])
            return result
        except Exception as e:
            logger.warning("get_technicals failed for %s: %s", ticker, e)
            return None

    def get_news(self, ticker: str) -> Optional[dict[str, Any]]:
        """뉴스 조회. Finnhub."""
        return self._try_fallback("news", "get_news", ticker=ticker)

    def get_analyst(self, ticker: str) -> Optional[dict[str, Any]]:
        """애널리스트 추천. Finnhub."""
        return self._try_fallback("analyst", "get_analyst_recommendations", ticker=ticker)

    def get_sector_stocks(self, sector: str, **kwargs) -> Optional[dict[str, Any]]:
        """섹터 스크리닝. Finviz → FMP 폴백."""
        cached = cache.get("sector_screen", sector)
        if cached is not None:
            return cached
        # Finviz 1순위
        result = self.finviz.screen_stocks(sector=sector, **kwargs)
        # FMP 폴백
        if result is None:
            result = self.fmp.screen_stocks(sector=sector, **kwargs)
        if result:
            cache.set("sector_screen", sector, result, CACHE_TTL["sector"])
        return result

    def get_sector_pe(self, sector: str) -> Optional[dict[str, Any]]:
        """섹터 평균 PE. Finviz → FMP 폴백."""
        cached = cache.get("sector_pe", sector)
        if cached is not None:
            return cached
        result = self.finviz.get_sector_pe(sector)
        if result is None:
            result = self.fmp.get_sector_pe(sector)
        if result:
            cache.set("sector_pe", sector, result, CACHE_TTL["sector"])
        return result

    def get_macro(self) -> Optional[dict[str, Any]]:
        """매크로 경제 지표. FRED."""
        cached = cache.get("macro", "summary")
        if cached is not None:
            return cached
        result = self.fred.get_macro_summary()
        if result:
            cache.set("macro", "summary", result, CACHE_TTL["quick_look"])
        return result

    def get_market_indices(self) -> Optional[dict[str, Any]]:
        """시장 지수 조회."""
        cached = cache.get("market_indices", "all")
        if cached is not None:
            return cached
        result = self.yfinance.get_market_indices()
        if result:
            cache.set("market_indices", "all", result, CACHE_TTL["quick_look"])
        return result


# Global singleton
api_client = APIClient()
