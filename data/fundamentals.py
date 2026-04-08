"""재무 지표 모듈 — PE, EPS, PEG, 시가총액, 섹터 등.

사용법:
    from data.fundamentals import get_fundamentals
    f = get_fundamentals("NVDA")
    # {"pe": 35.2, "eps": 4.05, "sector": "Technology", ...}
"""

import logging
from typing import Any, Optional

from data.api_client import api_client

logger = logging.getLogger(__name__)


def get_fundamentals(ticker: str, force_fallback: bool = False) -> Optional[dict[str, Any]]:
    """기업 재무 지표 조회. yfinance → FMP 폴백.

    Args:
        ticker: 종목 코드
        force_fallback: True면 1순위 건너뛰고 FMP 직접 호출 (테스트용)

    Returns:
        {
            "ticker", "pe", "forward_pe", "eps", "peg",
            "market_cap", "week52_high", "week52_low",
            "dividend_yield", "de_ratio",
            "sector", "industry", "employees", "country",
            "source"
        }
        실패 시 None.
    """
    if force_fallback:
        raw = api_client.fmp.get_fundamentals(ticker)
    else:
        raw = api_client.get_fundamentals(ticker)

    if raw is None:
        return None

    return {
        "ticker": ticker,
        "pe": raw.get("pe_ratio"),
        "forward_pe": raw.get("forward_pe"),
        "eps": raw.get("eps"),
        "peg": raw.get("peg_ratio"),
        "market_cap": raw.get("market_cap"),
        "week52_high": raw.get("52w_high"),
        "week52_low": raw.get("52w_low"),
        "dividend_yield": raw.get("dividend_yield"),
        "de_ratio": raw.get("debt_to_equity"),
        "sector": raw.get("sector"),
        "industry": raw.get("industry"),
        "employees": raw.get("employees"),
        "country": raw.get("country"),
        "source": raw.get("source"),
    }
