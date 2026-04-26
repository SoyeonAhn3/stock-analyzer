"""재무/기술지표 해석 Agent — Quick Look 데이터를 AI가 해석.

사용법:
    from agents.data_agent import run
    result = await run("NVDA", quick_look_data)
"""

import asyncio
import json
import logging
from typing import Any

from agents.claude_client import call_claude

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """너는 주식 재무 분석 전문가야.
아래 제공된 재무 지표와 기술적 지표를 해석하여 종합적인 데이터 분석 결과를 제공해.

규칙:
- 주어진 숫자만 해석해. 새로운 숫자를 만들지 마.
- PER은 섹터 평균과 비교하여 고평가/저평가를 판단해.
- 기술 지표는 현재 추세와 매매 신호를 판단해.
- 재무 건전성은 부채비율(D/E)과 수익성 기반으로 판단해.

반드시 아래 JSON 형식으로만 답변해:
{
    "price_position": "52주 고점/저점 대비 현재 위치 설명",
    "valuation": {
        "assessment": "overvalued" | "undervalued" | "fairly_valued",
        "detail": "PER/PEG 기반 설명"
    },
    "technicals_summary": {
        "trend": "bullish" | "bearish" | "neutral",
        "signals": ["주요 기술 신호 리스트"]
    },
    "financial_health": {
        "rating": "strong" | "moderate" | "weak",
        "detail": "부채비율, 수익성 기반 설명"
    },
    "summary": "2~3문장 종합 요약"
}"""


_ALLOWED_KEYS = {
    "price_position", "valuation", "technicals_summary",
    "financial_health", "summary",
}


async def run(ticker: str, quick_look_data: dict) -> dict[str, Any]:
    """Data Agent 실행.

    핵심: API 재호출 없이 quick_look_data를 그대로 재사용한다.

    Args:
        ticker: 종목 코드
        quick_look_data: Phase 2에서 수집한 데이터 (재사용)

    Returns:
        재무/기술지표 해석 결과 dict. 실패 시 예외 발생.
    """
    # 1단계: 프롬프트 구성 (API 호출 없음, 데이터 재사용)
    user_message = _build_message(ticker, quick_look_data)

    # 2단계: Claude 호출 (동기 함수를 별도 스레드에서 실행하여 이벤트 루프 블로킹 방지)
    result = await asyncio.to_thread(call_claude, SYSTEM_PROMPT, user_message)

    if result["parsed"]:
        filtered = {k: v for k, v in result["data"].items() if k in _ALLOWED_KEYS}
        return {
            "agent": "data",
            "status": "success",
            **filtered,
        }

    if result.get("raw_output"):
        logger.warning("Data Agent: JSON 파싱 실패, raw_output 반환")
        return {
            "agent": "data",
            "status": "partial",
            "raw_output": result["raw_output"],
            "summary": result["raw_output"][:500],
        }

    raise RuntimeError(f"Data Agent 실패: {result.get('error', 'unknown')}")


def _build_message(ticker: str, quick_look_data: dict) -> str:
    """Claude에게 보낼 user_message를 조립한다."""
    parts = [f"종목: {ticker}"]

    # 시세 정보
    price = quick_look_data.get("price")
    if price is not None:
        parts.append(f"현재 주가: ${price}")

    w52_high = quick_look_data.get("week52_high")
    w52_low = quick_look_data.get("week52_low")
    if w52_high and w52_low:
        parts.append(f"52주 범위: ${w52_low} ~ ${w52_high}")

    # 재무 지표
    fundamentals = []
    for key, label in [
        ("pe", "PER"), ("forward_pe", "Forward PER"), ("eps", "EPS"),
        ("peg", "PEG"), ("market_cap", "시가총액"),
        ("dividend_yield", "배당수익률"), ("de_ratio", "부채비율(D/E)"),
    ]:
        val = quick_look_data.get(key)
        if val is not None:
            fundamentals.append(f"  {label}: {val}")

    sector = quick_look_data.get("sector")
    industry = quick_look_data.get("industry")
    if sector:
        fundamentals.append(f"  섹터: {sector}")
    if industry:
        fundamentals.append(f"  산업: {industry}")

    if fundamentals:
        parts.append(f"\n재무 지표:\n" + "\n".join(fundamentals))

    # 기술적 지표
    technicals = []
    rsi = quick_look_data.get("rsi")
    if rsi is not None:
        if isinstance(rsi, dict):
            technicals.append(f"  RSI: {rsi.get('value', rsi)} (신호: {rsi.get('signal', 'N/A')})")
        else:
            technicals.append(f"  RSI: {rsi}")

    macd = quick_look_data.get("macd")
    if macd is not None:
        if isinstance(macd, dict):
            technicals.append(f"  MACD: {macd.get('signal', macd)}")
        else:
            technicals.append(f"  MACD: {macd}")

    ma50 = quick_look_data.get("ma50")
    ma200 = quick_look_data.get("ma200")
    if ma50 is not None:
        technicals.append(f"  50일 이동평균: {ma50}")
    if ma200 is not None:
        technicals.append(f"  200일 이동평균: {ma200}")

    if technicals:
        parts.append(f"\n기술적 지표:\n" + "\n".join(technicals))

    return "\n".join(parts)
