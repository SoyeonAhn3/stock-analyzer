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
                         ticker_data: dict[str, Any],
                         sector_pe: dict[str, Any] | None = None,
                         macro: dict[str, Any] | None = None) -> dict[str, Any]:
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
    system_prompt, user_message = _build_prompt(tickers, comparison_type, ticker_data,
                                                sector_pe=sector_pe, macro=macro)

    # Claude 호출 (비교 분석은 응답이 길어 토큰 확장)
    result = call_claude(system_prompt, user_message, max_tokens=COMPARE_MAX_TOKENS)

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
                  ticker_data: dict[str, Any],
                  sector_pe: dict[str, Any] | None = None,
                  macro: dict[str, Any] | None = None) -> tuple[str, str]:
    """비교 유형에 따라 프롬프트 생성."""
    if comparison_type == "same_sector":
        return _build_same_sector_prompt(tickers, ticker_data)
    return _build_cross_sector_prompt(tickers, ticker_data, sector_pe=sector_pe, macro=macro)


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
                               ticker_data: dict[str, Any],
                               sector_pe: dict[str, Any] | None = None,
                               macro: dict[str, Any] | None = None) -> tuple[str, str]:
    """다른 섹터 상대 비교 프롬프트."""
    system_prompt = (
        "너는 크로스 섹터 비교 분석 전문가야. "
        "서로 다른 섹터의 종목들을 각 섹터 맥락에서 비교해. "
        "제공된 섹터 평균 PE, 매크로 경제 데이터, 기술 지표를 반드시 분석에 활용해. "
        "반드시 JSON 형식으로만 응답해."
    )

    data_text = json.dumps(ticker_data, ensure_ascii=False, default=str)

    # 섹터 PE 벤치마크 텍스트
    sector_pe_text = ""
    if sector_pe:
        lines = []
        for sector, pe_data in sector_pe.items():
            avg_pe = pe_data.get("average_pe") or pe_data.get("pe")
            if avg_pe:
                lines.append(f"  - {sector}: 평균 PE = {avg_pe}")
        if lines:
            sector_pe_text = "\n\n[섹터 평균 PE 벤치마크]\n" + "\n".join(lines)

    # 매크로 경제 데이터 텍스트
    macro_text = ""
    if macro:
        parts = []
        for key in ("fed_rate", "cpi", "gdp_growth", "unemployment"):
            val = macro.get(key)
            if val is not None:
                label = {"fed_rate": "Fed Rate", "cpi": "CPI", "gdp_growth": "GDP Growth", "unemployment": "Unemployment"}.get(key, key)
                parts.append(f"{label}: {val}%")
        if parts:
            macro_text = "\n\n[현재 매크로 경제 지표]\n  " + ", ".join(parts)

    ticker_placeholders = {t: t for t in tickers}
    tickers_str = ", ".join(tickers)

    user_message = f"""다음은 서로 다른 섹터에 속한 {len(tickers)}개 종목의 데이터입니다: {tickers_str}

{data_text}{sector_pe_text}{macro_text}

[기술 지표 해석 가이드]
- RSI: 30 이하 과매도(매수 기회), 70 이상 과매수(주의)
- MACD: 히스토그램 양전환은 상승 추세, 음전환은 하락 추세
- MA50/MA200 대비 가격 위치: 위에 있으면 상승 추세, 아래면 하락 추세
- Bollinger: 하단 밴드 근처면 과매도, 상단 근처면 과매수

아래 JSON 형식으로 크로스 섹터 비교 분석을 해주세요:
{{
  "sector_context": {{
    "{tickers[0]}": "섹터명. 핵심 동력 설명. 현재 섹터 전망 2~3문장.",
    "{tickers[1]}": "섹터명. 핵심 동력 설명. 현재 섹터 전망 2~3문장."
  }},
  "valuation_vs_sector": {{
    "{tickers[0]}": "섹터 평균 PE 대비 프리미엄/할인율 수치 포함 평가. 2~3문장.",
    "{tickers[1]}": "섹터 평균 PE 대비 프리미엄/할인율 수치 포함 평가. 2~3문장."
  }},
  "sector_neutral_metrics": {{
    "{tickers[0]}": "ROE, Profit Margin, FCF, D/E, Beta 수치를 포함하여 2~3문장으로 요약.",
    "{tickers[1]}": "ROE, Profit Margin, FCF, D/E, Beta 수치를 포함하여 2~3문장으로 요약."
  }},
  "technical_comparison": {{
    "{tickers[0]}": "RSI, MACD, MA50/200 기반 현재 기술적 위치와 추세 2~3문장.",
    "{tickers[1]}": "RSI, MACD, MA50/200 기반 현재 기술적 위치와 추세 2~3문장."
  }},
  "macro_scenarios": {{
    "rate_cut": "금리 인하 시 유리한 종목과 구체적 이유.",
    "rate_hold": "금리 동결 시 유리한 종목과 구체적 이유.",
    "recession": "경기 침체 시 방어적인 종목과 구체적 이유.",
    "inflation_spike": "인플레이션 급등 시 유리한 종목과 구체적 이유.",
    "sector_rotation": "섹터 로테이션 발생 시 수혜 종목과 구체적 이유."
  }},
  "diversification_value": "포트폴리오 분산 관점에서 두 종목의 상관관계와 분산 효과 평가. Beta 차이 포함.",
  "recommendation_by_style": {{
    "growth_investor": "추천 종목과 구체적 근거(매출성장률, PEG 등)를 2문장으로.",
    "value_investor": "추천 종목과 구체적 근거(PE할인율, FCF Yield 등)를 2문장으로.",
    "balanced_investor": "추천 종목과 구체적 근거(리스크 대비 수익, 분산 효과 등)를 2문장으로."
  }},
  "key_risks": {{
    "{tickers[0]}": ["구체적 리스크1", "구체적 리스크2"],
    "{tickers[1]}": ["구체적 리스크1", "구체적 리스크2"]
  }},
  "blind_spots": ["분석에서 놓치기 쉬운 주의점1", "주의점2"],
  "summary": "3~4줄 종합 요약. 어떤 투자자에게 어떤 종목이 적합한지 명확히."
}}

주의: 모든 값은 반드시 문자열(string)로 작성해. 중첩 객체(object)를 값으로 쓰지 마.
제공된 데이터의 실제 수치를 인용하여 근거를 제시해. 데이터에 없는 숫자를 만들어내지 마세요."""

    return system_prompt, user_message
