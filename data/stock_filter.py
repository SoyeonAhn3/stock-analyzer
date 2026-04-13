"""3단계 주식 필터 모듈 - 공통 필터 + 프리셋 필터 + 적응형 완화.

사용법:
    from data.stock_filter import filter_stocks
    filtered, relaxed, warning = filter_stocks(stocks, "large_stable")
"""

import logging
from typing import Any, Optional

from data.api_client import api_client
from data.fundamentals import get_fundamentals
from data.quote import get_quote

logger = logging.getLogger(__name__)

# 프리셋별 필터 기준
PRESET_CRITERIA = {
    "large_stable": {
        "market_cap_min": 50_000_000_000,   # $50B
        "pe_positive": True,
        "revenue_growth_min": None,
        "dividend_yield_min": None,
    },
    "mid_growth": {
        "market_cap_min": 10_000_000_000,   # $10B
        "pe_positive": True,
        "revenue_growth_min": None,
        "dividend_yield_min": None,
    },
    "early_growth": {
        "market_cap_min": 2_000_000_000,    # $2B
        "pe_positive": False,
        "revenue_growth_min": 20,           # 20%+
        "dividend_yield_min": None,
    },
    "dividend": {
        "market_cap_min": 5_000_000_000,    # $5B
        "pe_positive": True,
        "revenue_growth_min": None,
        "dividend_yield_min": 2.0,          # 2%+
    },
}

# 적응형 완화 시 시총 하향 매핑
RELAXED_MARKET_CAP = {
    50_000_000_000: 20_000_000_000,   # $50B → $20B
    10_000_000_000: 5_000_000_000,    # $10B → $5B
    5_000_000_000: 2_000_000_000,     # $5B  → $2B
    2_000_000_000: 1_000_000_000,     # $2B  → $1B
}


def filter_stocks(stocks: list[dict[str, Any]], preset: str) -> tuple[list[dict], bool, Optional[str]]:
    """3단계 필터로 종목을 걸러낸다.

    Args:
        stocks: 종목 리스트. 각 항목은 Finviz 스크리너 결과 또는
                get_fundamentals 결과와 유사한 dict.
                필수 키: "ticker". 선택: "market_cap", "pe_ratio", "volume" 등.
        preset: 프리셋 ("large_stable", "mid_growth", "early_growth", "dividend")

    Returns:
        (filtered_stocks, relaxed, warning_message)
        - filtered_stocks: 필터 통과 종목 리스트 (최대 10개)
        - relaxed: 적응형 완화 적용 여부
        - warning_message: 완화 시 경고 메시지 (미적용 시 None)
    """
    if not stocks:
        return [], False, "종목 데이터가 없습니다."

    criteria = PRESET_CRITERIA.get(preset)
    if criteria is None:
        logger.warning("Unknown preset: %s, falling back to mid_growth", preset)
        criteria = PRESET_CRITERIA["mid_growth"]

    # 1단계: 공통 필터 (불량 데이터 제거)
    stage1 = _apply_common_filter(stocks)
    logger.info("Stage 1 (common filter): %d -> %d", len(stocks), len(stage1))

    # 2단계: 프리셋 필터
    stage2 = _apply_preset_filter(stage1, criteria)
    logger.info("Stage 2 (preset %s): %d -> %d", preset, len(stage1), len(stage2))

    # 3단계: 적응형 완화
    return _apply_adaptive_relaxation(stage1, stage2, criteria, preset)


def _apply_common_filter(stocks: list[dict]) -> list[dict]:
    """1단계 공통 필터 - 불량 데이터 제거."""
    result = []
    for s in stocks:
        # 거래량 0 제외
        volume = s.get("volume")
        if volume is not None and _to_number(volume) == 0:
            continue
        # 티커 없으면 제외
        if not s.get("ticker"):
            continue
        result.append(s)
    return result


def _apply_preset_filter(stocks: list[dict], criteria: dict) -> list[dict]:
    """2단계 프리셋 필터."""
    result = []
    for s in stocks:
        if not _passes_preset(s, criteria):
            continue
        result.append(s)
    return result


def _passes_preset(stock: dict, criteria: dict) -> bool:
    """단일 종목이 프리셋 기준을 통과하는지 판정."""
    # 시총 체크
    market_cap = _to_number(stock.get("market_cap"))
    cap_min = criteria["market_cap_min"]
    if market_cap is not None and market_cap < cap_min:
        return False

    # PE 양수 체크
    if criteria["pe_positive"]:
        pe = _to_number(stock.get("pe_ratio", stock.get("pe")))
        if pe is not None and pe <= 0:
            return False

    # 배당률 체크 — 값이 없으면 미통과 (배당 데이터가 있어야 함)
    div_min = criteria.get("dividend_yield_min")
    if div_min is not None:
        div_yield = _to_number(stock.get("dividend_yield"))
        if div_yield is None or div_yield < div_min:
            return False

    return True


def _apply_adaptive_relaxation(
    stage1: list[dict],
    stage2: list[dict],
    criteria: dict,
    preset: str,
) -> tuple[list[dict], bool, Optional[str]]:
    """3단계 적응형 완화."""
    count = len(stage2)

    # 10개 이상: 시총 기준 상위 10개
    if count >= 10:
        sorted_stocks = _sort_by_market_cap(stage2)
        return sorted_stocks[:10], False, None

    # 5~9개: 전부 통과
    if count >= 5:
        return stage2, False, None

    # 3~4개: 시총 기준 1단계 완화 후 재필터
    if count >= 3:
        relaxed_criteria = criteria.copy()
        original_cap = criteria["market_cap_min"]
        relaxed_cap = RELAXED_MARKET_CAP.get(original_cap, original_cap // 2)
        relaxed_criteria["market_cap_min"] = relaxed_cap

        relaxed_result = _apply_preset_filter(stage1, relaxed_criteria)
        relaxed_result = _sort_by_market_cap(relaxed_result)[:10]

        msg = (f"필터 기준 완화 적용: 시총 ${_format_cap(original_cap)} "
               f"-> ${_format_cap(relaxed_cap)} ({preset})")
        logger.info(msg)
        return relaxed_result, True, msg

    # 0~2개: 프리셋 필터 무시, 시총 상위 10개
    sorted_all = _sort_by_market_cap(stage1)[:10]
    msg = "필터 기준 미달 - 시총 상위 종목 표시"
    logger.info(msg)
    return sorted_all, True, msg


def _sort_by_market_cap(stocks: list[dict]) -> list[dict]:
    """시총 기준 내림차순 정렬."""
    return sorted(stocks, key=lambda s: _to_number(s.get("market_cap")) or 0, reverse=True)


def _to_number(value) -> Optional[float]:
    """문자열/숫자를 float로 변환. 실패 시 None."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Finviz 형식: "1.5T", "200B", "15.3%" 등
        value = value.strip().replace(",", "").replace("%", "")
        multipliers = {"T": 1e12, "B": 1e9, "M": 1e6, "K": 1e3}
        for suffix, mult in multipliers.items():
            if value.upper().endswith(suffix):
                try:
                    return float(value[:-1]) * mult
                except ValueError:
                    return None
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _format_cap(value: float) -> str:
    """시총을 읽기 쉬운 형태로 포맷."""
    if value >= 1e12:
        return f"{value / 1e12:.0f}T"
    if value >= 1e9:
        return f"{value / 1e9:.0f}B"
    if value >= 1e6:
        return f"{value / 1e6:.0f}M"
    return str(int(value))
