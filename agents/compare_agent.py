"""AI 비교 분석 모듈 — same_sector / cross_sector 프롬프트 분기.

사용법:
    from agents.compare_agent import run_compare_analysis
    result = run_compare_analysis(
        tickers=["AAPL", "MSFT"],
        comparison_type="same_sector",
        ticker_data={"AAPL": {...}, "MSFT": {...}}
    )
"""

import json
import logging
from typing import Any

from agents.claude_client import call_claude
from data.cache import cache
from config.api_config import CACHE_TTL

logger = logging.getLogger(__name__)

COMPARE_MAX_TOKENS = 4096


def run_compare_analysis(tickers: list[str], comparison_type: str,
                         ticker_data: dict[str, Any]) -> dict[str, Any]:
    """AI 비교 분석 실행.

    Args:
        tickers: 비교 대상 티커 리스트 (2~3개)
        comparison_type: "same_sector" | "cross_sector"
        ticker_data: {ticker: {"quote": {...}, "fundamentals": {...}, "technicals": {...}}, ...}

    Returns:
        {
            "status": "success" | "failed",
            "comparison_type": "same_sector" | "cross_sector",
            "tickers": [...],
            "analysis": {...} | None,
            "error": None | "에러 메시지"
        }
    """
    logger.info("=== Compare Analysis 시작: %s (%s) ===", tickers, comparison_type)

    # 캐시 확인
    cache_key = "_".join(sorted(tickers))
    cached = cache.get("compare", cache_key)
    if cached is not None:
        logger.info("캐시 적중: %s", cache_key)
        return cached

    # 프롬프트 생성
    system_prompt, user_message = _build_prompt(tickers, comparison_type, ticker_data)

    # Claude 호출
    result = call_claude(system_prompt, user_message)

    if result["parsed"]:
        output = {
            "status": "success",
            "comparison_type": comparison_type,
            "tickers": tickers,
            "analysis": result["data"],
            "error": None,
        }
        cache.set("compare", cache_key, output, CACHE_TTL["ai_result"])
        logger.info("=== Compare Analysis 완료 ===")
        return output

    logger.error("Compare Analysis 실패: %s", result.get("error", ""))
    return {
        "status": "failed",
        "comparison_type": comparison_type,
        "tickers": tickers,
        "analysis": None,
        "error": result.get("error", "AI 분석 실패"),
    }


def _build_prompt(tickers: list[str], comparison_type: str,
                  ticker_data: dict[str, Any]) -> tuple[str, str]:
    """비교 유형에 따라 프롬프트 생성."""
    if comparison_type == "same_sector":
        return _build_same_sector_prompt(tickers, ticker_data)
    return _build_cross_sector_prompt(tickers, ticker_data)


def _build_same_sector_prompt(tickers: list[str],
                              ticker_data: dict[str, Any]) -> tuple[str, str]:
    """동일 섹터 직접 비교 프롬프트."""
    system_prompt = (
        "너는 주식 비교 분석 전문가야. "
        "같은 섹터에 속한 종목들을 직접 비교하여 투자 판단에 도움을 줘. "
        "반드시 JSON 형식으로만 응답해."
    )

    data_text = json.dumps(ticker_data, ensure_ascii=False, default=str)

    user_message = f"""다음은 같은 섹터에 속한 {len(tickers)}개 종목의 데이터입니다: {', '.join(tickers)}

{data_text}

아래 JSON 형식으로 직접 비교 분석을 해주세요:
{{
  "rankings": {{
    "growth": [{{"ticker": "...", "rank": 1, "reason": "..."}}, ...],
    "valuation": [{{"ticker": "...", "rank": 1, "reason": "..."}}, ...],
    "financial_health": [{{"ticker": "...", "rank": 1, "reason": "..."}}, ...],
    "technical_position": [{{"ticker": "...", "rank": 1, "reason": "..."}}, ...]
  }},
  "key_risks": {{
    "{tickers[0]}": ["리스크1", "리스크2"],
    "{tickers[1]}": ["리스크1", "리스크2"]
  }},
  "recommendation_by_style": {{
    "growth_investor": "추천 종목과 이유를 한 문장으로.",
    "value_investor": "추천 종목과 이유를 한 문장으로.",
    "balanced_investor": "추천 종목과 이유를 한 문장으로."
  }},
  "blind_spots": ["주의점1", "주의점2"],
  "summary": "2~3줄 요약"
}}

주의: 모든 값은 반드시 문자열(string)로 작성해. 중첩 객체(object)를 값으로 쓰지 마.
아래 데이터에 없는 숫자를 만들어내지 마세요."""

    return system_prompt, user_message


def _build_cross_sector_prompt(tickers: list[str],
                               ticker_data: dict[str, Any]) -> tuple[str, str]:
    """다른 섹터 상대 비교 프롬프트."""
    system_prompt = (
        "너는 크로스 섹터 비교 분석 전문가야. "
        "서로 다른 섹터의 종목들을 각 섹터 맥락에서 비교해. "
        "반드시 JSON 형식으로만 응답해."
    )

    data_text = json.dumps(ticker_data, ensure_ascii=False, default=str)

    user_message = f"""다음은 서로 다른 섹터에 속한 {len(tickers)}개 종목의 데이터입니다: {', '.join(tickers)}

{data_text}

아래 JSON 형식으로 크로스 섹터 비교 분석을 해주세요:
{{
  "sector_context": {{
    "{tickers[0]}": "섹터명. 핵심 동력 설명. 전망 한 줄.",
    "{tickers[1]}": "섹터명. 핵심 동력 설명. 전망 한 줄."
  }},
  "valuation_vs_sector": {{
    "{tickers[0]}": "섹터 평균 PER 대비 평가 한 줄.",
    "{tickers[1]}": "섹터 평균 PER 대비 평가 한 줄."
  }},
  "sector_neutral_metrics": {{
    "{tickers[0]}": "FCF Yield, ROE, D/E 요약 한 줄.",
    "{tickers[1]}": "FCF Yield, ROE, D/E 요약 한 줄."
  }},
  "macro_scenarios": {{
    "rate_hold": "유리한 종목과 이유를 한 문장으로.",
    "recession": "유리한 종목과 이유를 한 문장으로."
  }},
  "diversification_value": "포트폴리오 분산 관점 평가",
  "recommendation_by_style": {{
    "growth_investor": "추천 종목과 이유를 한 문장으로.",
    "value_investor": "추천 종목과 이유를 한 문장으로.",
    "balanced_investor": "추천 종목과 이유를 한 문장으로."
  }},
  "blind_spots": ["주의점1", "주의점2"],
  "summary": "2~3줄 요약"
}}

주의: 모든 값은 반드시 문자열(string)로 작성해. 중첩 객체(object)를 값으로 쓰지 마.
아래 데이터에 없는 숫자를 만들어내지 마세요."""

    return system_prompt, user_message
