"""섹터 데이터 모듈 - GICS 섹터 종목 조회 + 프리셋 매핑.

사용법:
    from data.sector_data import get_sector_tickers, get_preset_for_sector
    tickers = get_sector_tickers("Information Technology")
    preset = get_preset_for_sector("Information Technology")  # "large_stable"
"""

import logging
from typing import Any, Optional

from data.api_client import api_client
from data.theme_manager import load_themes

logger = logging.getLogger(__name__)

# GICS 11개 섹터 → 프리셋 매핑
SECTOR_PRESET_MAP = {
    "Information Technology": "large_stable",
    "Technology": "large_stable",
    "Financials": "large_stable",
    "Financial": "large_stable",
    "Communication Services": "large_stable",
    "Consumer Discretionary": "large_stable",
    "Consumer Cyclical": "large_stable",
    "Industrials": "mid_growth",
    "Energy": "mid_growth",
    "Materials": "mid_growth",
    "Basic Materials": "mid_growth",
    "Consumer Staples": "mid_growth",
    "Consumer Defensive": "mid_growth",
    "Health Care": "early_growth",
    "Healthcare": "early_growth",
    "Utilities": "dividend",
    "Real Estate": "dividend",
}

# GICS 표준 섹터 목록 (UI 표시용)
GICS_SECTORS = [
    "Information Technology",
    "Health Care",
    "Financials",
    "Consumer Discretionary",
    "Communication Services",
    "Industrials",
    "Consumer Staples",
    "Energy",
    "Utilities",
    "Real Estate",
    "Materials",
]


def get_sector_tickers(sector: str) -> Optional[list[dict[str, Any]]]:
    """섹터에 속한 종목 리스트 조회.

    Finviz 스크리너를 사용하여 해당 섹터의 종목을 가져온다.
    시총 $2B 이상으로 제한하여 의미 있는 종목만 반환.

    Args:
        sector: GICS 섹터명 (예: "Information Technology")

    Returns:
        [{"ticker": "AAPL", "name": "Apple Inc.", "market_cap": ..., "pe_ratio": ..., ...}, ...]
        실패 시 None.
    """
    result = api_client.get_sector_stocks(sector, market_cap_min=2_000_000_000, limit=100)
    if result is None or not result.get("stocks"):
        logger.warning("섹터 종목 조회 실패: %s", sector)
        return None
    return result["stocks"]


def get_theme_tickers(theme_name: str) -> Optional[list[str]]:
    """커스텀 테마의 티커 리스트 반환.

    Args:
        theme_name: 테마 이름 (예: "AI_semiconductor")

    Returns:
        ["NVDA", "AMD", ...] 또는 None (테마 없음)
    """
    themes = load_themes()
    theme = themes.get(theme_name)
    if theme is None:
        return None
    return theme["tickers"]


def get_preset_for_sector(sector: str) -> str:
    """GICS 섹터에 대응하는 프리셋 반환.

    매핑에 없으면 "mid_growth"를 기본값으로 반환.
    """
    return SECTOR_PRESET_MAP.get(sector, "mid_growth")


def get_preset_for_theme(theme_name: str) -> str:
    """커스텀 테마의 프리셋 반환. 테마 없으면 "mid_growth"."""
    themes = load_themes()
    theme = themes.get(theme_name)
    if theme is None:
        return "mid_growth"
    return theme.get("preset", "mid_growth")


def is_theme(name: str) -> bool:
    """주어진 이름이 커스텀 테마인지 확인."""
    themes = load_themes()
    return name in themes
