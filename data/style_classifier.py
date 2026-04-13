"""투자 스타일 분류 모듈 — Growth / Value / Balanced.

사용법:
    from data.style_classifier import classify_style, classify_multiple
    style = classify_style({"forward_pe": 30, "dividend_yield": 0.2})  # "Growth"
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def classify_style(ticker_data: dict[str, Any]) -> str:
    """단일 종목의 투자 스타일 분류.

    분류 순서 (중요 — Growth를 먼저 체크):
    1. Growth: forward_pe >= 25 (매출 성장률 >= 20% 이면 보강)
    2. Value: forward_pe < 18 AND (dividend_yield >= 2% OR de_ratio 낮음)
    3. 기본값: Balanced

    Args:
        ticker_data: fundamentals 결과 dict.
            사용 키: forward_pe, pe, dividend_yield, peg, eps

    Returns:
        "Growth" | "Value" | "Balanced"
    """
    forward_pe = _to_float(ticker_data.get("forward_pe"))
    pe = _to_float(ticker_data.get("pe"))
    dividend_yield = _to_float(ticker_data.get("dividend_yield"))
    peg = _to_float(ticker_data.get("peg"))

    # Growth 체크
    if _is_growth(forward_pe, pe, peg):
        return "Growth"

    # Value 체크
    if _is_value(forward_pe, pe, dividend_yield):
        return "Value"

    return "Balanced"


def classify_multiple(tickers_data: dict[str, dict]) -> dict[str, str]:
    """여러 종목의 스타일 일괄 분류.

    Args:
        tickers_data: {ticker: fundamentals_dict, ...}

    Returns:
        {"AAPL": "Growth", "JNJ": "Value", ...}
    """
    return {ticker: classify_style(data) for ticker, data in tickers_data.items()}


def _is_growth(forward_pe: Optional[float], pe: Optional[float],
               peg: Optional[float]) -> bool:
    """Growth 판정."""
    effective_pe = forward_pe if forward_pe is not None else pe
    if effective_pe is not None and effective_pe >= 25:
        return True
    # PEG가 높으면 성장 기대가 높다는 의미
    if peg is not None and peg > 2.0 and effective_pe is not None and effective_pe >= 20:
        return True
    return False


def _is_value(forward_pe: Optional[float], pe: Optional[float],
              dividend_yield: Optional[float]) -> bool:
    """Value 판정."""
    effective_pe = forward_pe if forward_pe is not None else pe
    if effective_pe is None:
        return False
    if effective_pe >= 18:
        return False
    # PE 낮고 + 배당 2%+ 이면 Value
    if dividend_yield is not None and dividend_yield >= 2.0:
        return True
    # PE 매우 낮으면 (< 12) 그 자체로 Value
    if effective_pe < 12:
        return True
    return False


def _to_float(value: Any) -> Optional[float]:
    """숫자 변환. 실패 시 None."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
