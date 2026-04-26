"""거시경제 분석 Agent — 금리, CPI, 실업률, 섹터 트렌드 해석.

사용법:
    from agents.macro_agent import run
    result = await run("NVDA", quick_look_data)
"""

import asyncio
import json
import logging
from typing import Any

from data.api_client import api_client
from agents.claude_client import call_claude

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """너는 거시경제 분석 전문가야.
아래 제공된 경제 지표(금리, CPI, 실업률 등)와 종목 정보를 분석하여
현재 거시경제 환경이 해당 종목/섹터에 미치는 영향을 판단해.

규칙:
- 주어진 데이터만 해석해. 새로운 숫자를 만들지 마.
- 금리, 물가, 고용 지표의 추세와 방향성을 판단해.
- 해당 섹터에 대한 거시적 영향을 연결해서 분석해.

반드시 아래 JSON 형식으로만 답변해:
{
    "fed_rate": "현재 연준 금리",
    "rate_outlook": "인상" | "동결" | "인하" | "불확실",
    "inflation": {
        "current": "현재 CPI 수치",
        "trend": "상승" | "하락" | "안정"
    },
    "employment": {
        "unemployment_rate": "실업률",
        "assessment": "양호" | "우려"
    },
    "sector_trend": "해당 섹터의 거시적 전망",
    "market_sentiment": "bullish" | "bearish" | "neutral",
    "risk_factors": ["리스크 요인 리스트"],
    "summary": "2~3문장 종합 요약"
}"""


_ALLOWED_KEYS = {
    "fed_rate", "rate_outlook", "inflation", "employment",
    "sector_trend", "market_sentiment", "risk_factors", "summary",
}


async def run(ticker: str, quick_look_data: dict) -> dict[str, Any]:
    """Macro Agent 실행.

    Args:
        ticker: 종목 코드
        quick_look_data: Phase 2에서 수집한 데이터

    Returns:
        거시경제 분석 결과 dict. 실패 시 예외 발생.
    """
    # 1단계: 매크로 데이터 수집 (FRED API)
    macro = api_client.get_macro()

    # 2단계: 프롬프트 구성
    user_message = _build_message(ticker, quick_look_data, macro)

    # 3단계: Claude 호출 (동기 함수를 별도 스레드에서 실행하여 이벤트 루프 블로킹 방지)
    result = await asyncio.to_thread(call_claude, SYSTEM_PROMPT, user_message)

    if result["parsed"]:
        filtered = {k: v for k, v in result["data"].items() if k in _ALLOWED_KEYS}
        return {
            "agent": "macro",
            "status": "success",
            **filtered,
        }

    if result.get("raw_output"):
        logger.warning("Macro Agent: JSON 파싱 실패, raw_output 반환")
        return {
            "agent": "macro",
            "status": "partial",
            "raw_output": result["raw_output"],
            "summary": result["raw_output"][:500],
        }

    raise RuntimeError(f"Macro Agent 실패: {result.get('error', 'unknown')}")


def _build_message(ticker: str, quick_look_data: dict, macro: dict | None) -> str:
    """Claude에게 보낼 user_message를 조립한다."""
    parts = [f"종목: {ticker}"]

    sector = quick_look_data.get("sector")
    industry = quick_look_data.get("industry")
    if sector:
        parts.append(f"섹터: {sector}")
    if industry:
        parts.append(f"산업: {industry}")

    price = quick_look_data.get("price")
    if price is not None:
        parts.append(f"현재 주가: ${price}")

    # 매크로 경제 지표
    if macro:
        parts.append("\n거시경제 지표:")
        for key, label in [
            ("fed_rate", "연준 기준금리"),
            ("cpi", "CPI (소비자물가지수)"),
            ("cpi_yoy", "CPI 전년비"),
            ("unemployment", "실업률"),
            ("gdp_growth", "GDP 성장률"),
            ("ten_year_yield", "10년 국채 수익률"),
            ("vix", "VIX (공포지수)"),
        ]:
            val = macro.get(key)
            if val is not None:
                parts.append(f"  {label}: {val}")
    else:
        parts.append("\n거시경제 지표: 데이터 없음 (FRED API 실패)")

    return "\n".join(parts)
