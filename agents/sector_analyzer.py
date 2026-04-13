"""섹터 AI 축약 분석 모듈 - 필터 통과 종목 일괄 분석 -> Top 5 선정.

사용법:
    from agents.sector_analyzer import run_sector_screening
    result = await run_sector_screening("Information Technology")
    # 또는 커스텀 테마:
    result = await run_sector_screening("AI_semiconductor")
"""

import asyncio
import json
import logging
from typing import Any, Optional

from agents.claude_client import call_claude, CLAUDE_MAX_TOKENS
from data.sector_data import (
    get_sector_tickers, get_theme_tickers, get_preset_for_sector,
    get_preset_for_theme, is_theme, GICS_SECTORS,
)
from data.stock_filter import filter_stocks
from data.fundamentals import get_fundamentals
from data.quote import get_quote
from data.cache import cache
from config.api_config import CACHE_TTL

logger = logging.getLogger(__name__)

SECTOR_ANALYZER_MAX_TOKENS = 4096


def _build_stock_data(tickers: list[str]) -> list[dict[str, Any]]:
    """티커 리스트에서 분석용 데이터를 수집한다."""
    stocks = []
    for ticker in tickers:
        quote = get_quote(ticker)
        fundamentals = get_fundamentals(ticker)

        stock = {"ticker": ticker}
        if quote:
            stock.update({
                "price": quote.get("price"),
                "change_percent": quote.get("change_percent"),
                "volume": quote.get("volume"),
            })
        if fundamentals:
            stock.update({
                "pe": fundamentals.get("pe"),
                "forward_pe": fundamentals.get("forward_pe"),
                "eps": fundamentals.get("eps"),
                "market_cap": fundamentals.get("market_cap"),
                "dividend_yield": fundamentals.get("dividend_yield"),
                "sector": fundamentals.get("sector"),
                "industry": fundamentals.get("industry"),
            })
        stocks.append(stock)
    return stocks


def _build_prompt(stocks_data: list[dict], sector_or_theme: str) -> tuple[str, str]:
    """Claude 프롬프트를 생성한다."""
    system_prompt = (
        "너는 주식 섹터 분석 전문가야. "
        "주어진 종목들의 데이터를 분석하고 점수를 매겨 Top 5를 선정해. "
        "반드시 JSON 형식으로만 응답해. "
        "모든 종목을 동일한 깊이로 분석해 - 후반부 종목도 소홀히 하지 마."
    )

    stocks_text = json.dumps(stocks_data, ensure_ascii=False, default=str)

    user_message = f"""다음은 '{sector_or_theme}' 섹터/테마의 후보 종목 {len(stocks_data)}개 데이터입니다.

{stocks_text}

각 종목을 분석하고 0~100점 점수를 매겨 Top 5를 선정해주세요.

반드시 아래 JSON 형식으로 응답해주세요:
{{
  "analysis": [
    {{
      "ticker": "AAPL",
      "score": 82,
      "news_sentiment": "뉴스 감성 요약 (1줄)",
      "financials": "핵심 재무 지표 해석 (1줄)",
      "technical_signal": "기술적 신호 요약 (1줄)",
      "reason": "추천 이유 한 줄"
    }}
  ],
  "sector_outlook": "섹터 전체 전망 (2~3줄)",
  "risk_factors": ["리스크1", "리스크2"]
}}

주의사항:
- 아래 데이터에 없는 숫자를 만들어내지 마세요
- 모든 후보 종목을 분석하되, Top 5만 analysis 배열에 포함
- score 기준: 재무 건전성(30%), 성장성(30%), 기술적 신호(20%), 리스크(20%)
"""
    return system_prompt, user_message


async def run_sector_screening(sector_or_theme: str) -> dict[str, Any]:
    """섹터/테마 스크리닝 전체 파이프라인.

    Args:
        sector_or_theme: GICS 섹터명 또는 커스텀 테마명

    Returns:
        {
            "sector": "Information Technology",
            "is_theme": False,
            "filter_applied": "large_stable",
            "relaxed": False,
            "relaxation_message": None,
            "candidates_count": 10,
            "top5": [{"ticker", "score", "reason", ...}, ...],
            "sector_outlook": "...",
            "risk_factors": [...],
            "status": "success" | "partial" | "failed",
            "error": None | "에러 메시지",
        }
    """
    logger.info("=== Sector Screening 시작: %s ===", sector_or_theme)

    # 캐시 확인
    cached = cache.get("sector_screening", sector_or_theme)
    if cached is not None:
        logger.info("캐시 적중: %s", sector_or_theme)
        return cached

    # 테마 vs GICS 섹터 분기
    theme = is_theme(sector_or_theme)
    if theme:
        preset = get_preset_for_theme(sector_or_theme)
        tickers = get_theme_tickers(sector_or_theme)
        if tickers is None:
            return _fail_result(sector_or_theme, theme, "테마를 찾을 수 없습니다.")
        # 테마 티커로 데이터 수집
        stocks_data = _build_stock_data(tickers)
    else:
        preset = get_preset_for_sector(sector_or_theme)
        raw_stocks = get_sector_tickers(sector_or_theme)
        if raw_stocks is None:
            return _fail_result(sector_or_theme, theme, "섹터 종목 조회 실패")
        stocks_data = raw_stocks

    logger.info("종목 수집 완료: %d개, preset=%s", len(stocks_data), preset)

    # 3단계 필터
    filtered, relaxed, warning = filter_stocks(stocks_data, preset)
    logger.info("필터 결과: %d개 (relaxed=%s)", len(filtered), relaxed)

    if not filtered:
        return _fail_result(sector_or_theme, theme, "필터 통과 종목 없음")

    # 테마인 경우 필터 후 상세 데이터 보강
    if theme:
        # stocks_data가 이미 상세 데이터를 포함
        analysis_stocks = filtered
    else:
        # Finviz 스크리너 결과에서 티커만 추출해서 상세 데이터 수집
        tickers_for_analysis = [s["ticker"] for s in filtered if s.get("ticker")]
        analysis_stocks = _build_stock_data(tickers_for_analysis)

    # AI 축약 분석
    logger.info("AI 분석 시작 (%d개 종목)", len(analysis_stocks))
    ai_result = _run_ai_analysis(analysis_stocks, sector_or_theme)

    if ai_result is None:
        # AI 실패 - 필터 결과만 반환 (partial)
        result = {
            "sector": sector_or_theme,
            "is_theme": theme,
            "filter_applied": preset,
            "relaxed": relaxed,
            "relaxation_message": warning,
            "candidates_count": len(filtered),
            "top5": [{"ticker": s.get("ticker"), "score": None, "reason": "AI 분석 실패"} for s in filtered[:5]],
            "sector_outlook": None,
            "risk_factors": [],
            "status": "partial",
            "error": "AI 분석 실패 - 필터 결과만 표시",
        }
        cache.set("sector_screening", sector_or_theme, result, CACHE_TTL["ai_result"])
        return result

    result = {
        "sector": sector_or_theme,
        "is_theme": theme,
        "filter_applied": preset,
        "relaxed": relaxed,
        "relaxation_message": warning,
        "candidates_count": len(filtered),
        "top5": ai_result.get("analysis", [])[:5],
        "sector_outlook": ai_result.get("sector_outlook"),
        "risk_factors": ai_result.get("risk_factors", []),
        "status": "success",
        "error": None,
    }

    cache.set("sector_screening", sector_or_theme, result, CACHE_TTL["ai_result"])
    logger.info("=== Sector Screening 완료: %s, Top 5 선정 ===", sector_or_theme)
    return result


def _run_ai_analysis(stocks_data: list[dict], sector_or_theme: str) -> Optional[dict]:
    """Claude AI로 종목 일괄 분석. 실패 시 1회 재시도."""
    system_prompt, user_message = _build_prompt(stocks_data, sector_or_theme)

    for attempt in range(2):
        result = call_claude(system_prompt, user_message)
        if result["parsed"]:
            return result["data"]
        logger.warning("AI 분석 파싱 실패 (시도 %d/2): %s", attempt + 1, result.get("error", ""))
        if attempt == 0:
            import time
            time.sleep(3)

    logger.error("AI 분석 2회 시도 모두 실패")
    return None


def _fail_result(sector_or_theme: str, is_theme_flag: bool, error: str) -> dict:
    """실패 결과 생성."""
    return {
        "sector": sector_or_theme,
        "is_theme": is_theme_flag,
        "filter_applied": None,
        "relaxed": False,
        "relaxation_message": None,
        "candidates_count": 0,
        "top5": [],
        "sector_outlook": None,
        "risk_factors": [],
        "status": "failed",
        "error": error,
    }
