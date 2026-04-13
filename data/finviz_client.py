"""Finviz 래퍼 — 섹터 스크리닝, 섹터 평균 PE (FMP 대체)."""

import logging
from typing import Any, Optional

from finvizfinance.screener.overview import Overview

from config.api_config import API_TIMEOUT

logger = logging.getLogger(__name__)

# Finviz 섹터명 매핑 (yfinance/FMP 섹터명 → Finviz 섹터명)
SECTOR_MAP = {
    "technology": "Technology",
    "healthcare": "Healthcare",
    "financial services": "Financial",
    "financials": "Financial",
    "financial": "Financial",
    "consumer cyclical": "Consumer Cyclical",
    "consumer defensive": "Consumer Defensive",
    "energy": "Energy",
    "industrials": "Industrials",
    "basic materials": "Basic Materials",
    "real estate": "Real Estate",
    "utilities": "Utilities",
    "communication services": "Communication Services",
}


class FinvizClient:
    """Finviz 스크리너 래퍼. API 키 불필요."""

    def __init__(self):
        self._call_count = 0

    @property
    def call_count(self) -> int:
        return self._call_count

    def _normalize_sector(self, sector: str) -> str:
        """섹터명을 Finviz 형식으로 정규화."""
        return SECTOR_MAP.get(sector.lower(), sector)

    def screen_stocks(self, sector: str = None, market_cap_min: int = None,
                      market_cap_max: int = None, limit: int = 50) -> Optional[dict[str, Any]]:
        """섹터 기반 종목 스크리닝."""
        try:
            self._call_count += 1
            foverview = Overview()
            filters = {}

            if sector:
                filters["Sector"] = self._normalize_sector(sector)

            # 시가총액 필터 — Large cap 이상으로 제한하여 속도 확보
            if market_cap_min and market_cap_min >= 200_000_000_000:
                filters["Market Cap."] = "Mega ($200bln and more)"
            elif market_cap_min and market_cap_min >= 10_000_000_000:
                filters["Market Cap."] = "+Large (over $10bln)"
            elif market_cap_min and market_cap_min >= 2_000_000_000:
                filters["Market Cap."] = "+Mid (over $2bln)"
            else:
                # 기본: Large cap 이상 (속도 + 의미 있는 종목)
                filters["Market Cap."] = "+Large (over $10bln)"

            foverview.set_filter(filters_dict=filters)
            df = foverview.screener_view()

            if df is None or df.empty:
                return None

            stocks = []
            for _, row in df.head(limit).iterrows():
                stocks.append({
                    "ticker": row.get("Ticker"),
                    "name": row.get("Company"),
                    "market_cap": row.get("Market Cap"),
                    "sector": row.get("Sector"),
                    "industry": row.get("Industry"),
                    "price": row.get("Price"),
                    "volume": row.get("Volume"),
                    "pe_ratio": row.get("P/E"),
                    "change_pct": row.get("Change"),
                })

            return {
                "source": "finviz",
                "sector": sector,
                "stocks": stocks,
                "total_count": len(df),
            }
        except Exception as e:
            logger.warning("Finviz screen_stocks failed: %s", e)
            return None

    def get_sector_pe(self, sector: str) -> Optional[dict[str, Any]]:
        """섹터 평균(중앙값) PE 계산."""
        try:
            self._call_count += 1
            foverview = Overview()
            filters = {
                "Sector": self._normalize_sector(sector),
                "Market Cap.": "+Large (over $10bln)",
            }
            foverview.set_filter(filters_dict=filters)
            df = foverview.screener_view()

            if df is None or df.empty:
                return None

            pe_values = df["P/E"].dropna()
            pe_values = pe_values[pe_values > 0]

            if len(pe_values) == 0:
                return None

            median_pe = round(float(pe_values.median()), 2)

            return {
                "source": "finviz",
                "sector": sector,
                "median_pe": median_pe,
                "sample_size": len(pe_values),
            }
        except Exception as e:
            logger.warning("Finviz get_sector_pe failed: %s", e)
            return None

    def get_fundamentals(self, ticker: str) -> Optional[dict[str, Any]]:
        """개별 종목 기본 정보 (스크리너 결과에서 추출)."""
        try:
            self._call_count += 1
            foverview = Overview()
            foverview.set_filter(ticker=ticker)
            df = foverview.screener_view()

            if df is None or df.empty:
                return None

            row = df.iloc[0]
            return {
                "source": "finviz",
                "ticker": row.get("Ticker"),
                "name": row.get("Company"),
                "market_cap": row.get("Market Cap"),
                "sector": row.get("Sector"),
                "industry": row.get("Industry"),
                "pe_ratio": row.get("P/E"),
                "price": row.get("Price"),
                "country": row.get("Country"),
            }
        except Exception as e:
            logger.warning("Finviz get_fundamentals failed for %s: %s", ticker, e)
            return None
