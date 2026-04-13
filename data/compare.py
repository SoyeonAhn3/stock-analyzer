"""비교 모듈 — 비교 유형 판정 + 데이터 수집.

사용법:
    from data.compare import detect_comparison_type, get_comparison_data
    ctype = detect_comparison_type(["AAPL", "MSFT"])  # "same_sector"
    data = get_comparison_data(["AAPL", "MSFT"])
"""

import json
import logging
import os
from typing import Any, Optional

from data.fundamentals import get_fundamentals
from data.quote import get_quote
from data.technicals import get_technicals

logger = logging.getLogger(__name__)

RELATED_INDUSTRIES_PATH = os.path.join(
    os.path.dirname(__file__), "..", "config", "related_industries.json"
)


def _load_related_industries() -> dict[str, list[str]]:
    """related_industries.json 로드."""
    try:
        with open(RELATED_INDUSTRIES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.warning("related_industries.json 로드 실패")
        return {}


def _are_industries_related(industry_a: str, industry_b: str,
                            related: dict[str, list[str]]) -> bool:
    """두 industry가 관련 업종인지 판정."""
    if industry_a == industry_b:
        return True
    related_a = related.get(industry_a, [])
    related_b = related.get(industry_b, [])
    return industry_b in related_a or industry_a in related_b


def detect_comparison_type(tickers: list[str]) -> str:
    """2~3 종목의 비교 유형 판정.

    4단계 로직:
    1. 각 티커의 sector + industry 조회
    2. sector가 다르면 → "cross_sector"
    3. sector + industry 모두 같으면 → "same_sector"
    4. sector 같고 industry 다르면 → related_industries.json 참조

    Returns:
        "same_sector" | "cross_sector"
    """
    if len(tickers) < 2:
        return "same_sector"

    # 각 티커의 sector/industry 수집
    info = []
    for ticker in tickers:
        f = get_fundamentals(ticker)
        sector = (f.get("sector") if f else None) or "Unknown"
        industry = (f.get("industry") if f else None) or "Unknown"
        info.append({"ticker": ticker, "sector": sector, "industry": industry})

    # Unknown이 포함되면 안전하게 cross_sector
    if any(i["sector"] == "Unknown" for i in info):
        return "cross_sector"

    # sector가 전부 같은지 확인
    sectors = {i["sector"] for i in info}
    if len(sectors) > 1:
        return "cross_sector"

    # sector 같고, industry도 전부 같은지 확인
    industries = {i["industry"] for i in info}
    if len(industries) == 1:
        return "same_sector"

    # sector 같고 industry 다른 경우 → 관련 업종 체크
    related = _load_related_industries()
    industry_list = [i["industry"] for i in info]
    for i in range(len(industry_list)):
        for j in range(i + 1, len(industry_list)):
            if not _are_industries_related(industry_list[i], industry_list[j], related):
                return "cross_sector"

    return "same_sector"


def get_comparison_data(tickers: list[str]) -> dict[str, Any]:
    """2~3 종목의 비교 데이터 수집.

    Returns:
        {
            "tickers": ["AAPL", "MSFT"],
            "comparison_type": "same_sector" | "cross_sector",
            "data": {
                "AAPL": {"quote": {...}, "fundamentals": {...}, "technicals": {...}},
                "MSFT": {"quote": {...}, "fundamentals": {...}, "technicals": {...}},
            }
        }
    """
    comparison_type = detect_comparison_type(tickers)

    data = {}
    for ticker in tickers:
        data[ticker] = {
            "quote": get_quote(ticker),
            "fundamentals": get_fundamentals(ticker),
            "technicals": get_technicals(ticker),
        }

    return {
        "tickers": tickers,
        "comparison_type": comparison_type,
        "data": data,
    }
