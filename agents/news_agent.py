"""뉴스 감성 분석 Agent — 뉴스 + 실적 + 애널리스트 의견 종합.

사용법:
    from agents.news_agent import run
    result = await run("NVDA", quick_look_data)
"""

import json
import logging
from typing import Any, Optional

from data.api_client import api_client
from agents.claude_client import call_claude

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """너는 주식 뉴스 분석 전문가야.
아래 제공된 뉴스, 애널리스트 추천, 시세 데이터를 분석하여 종합적인 뉴스 감성을 판단해.

규칙:
- 주어진 데이터만 해석해. 새로운 숫자를 만들지 마.
- 뉴스가 없으면 "데이터 부족"으로 판단해.
- Reuters, Bloomberg, CNBC, WSJ 출처의 뉴스에 더 높은 가중치를 부여해.

반드시 아래 JSON 형식으로만 답변해:
{
    "overall_sentiment": "positive" | "negative" | "neutral" | "mixed",
    "sentiment_score": 0.0 ~ 1.0,
    "recent_news": [
        {"headline": "뉴스 제목", "sentiment": "positive|negative|neutral", "impact": "high|medium|low"}
    ],
    "earnings": "beat" | "miss" | "inline" | "unknown",
    "analyst_consensus": "strong_buy" | "buy" | "hold" | "sell" | "strong_sell",
    "key_events_upcoming": ["이벤트 설명"],
    "summary": "2~3문장 요약"
}"""


_ALLOWED_KEYS = {
    "overall_sentiment", "sentiment_score", "recent_news", "earnings",
    "analyst_consensus", "key_events_upcoming", "summary",
}


async def run(ticker: str, quick_look_data: dict) -> dict[str, Any]:
    """뉴스 Agent 실행.

    Args:
        ticker: 종목 코드
        quick_look_data: Phase 2에서 수집한 데이터

    Returns:
        뉴스 감성 분석 결과 dict. 실패 시 예외 발생.
    """
    # 1단계: 데이터 수집
    news = api_client.get_news(ticker)
    analyst = api_client.get_analyst(ticker)

    # 2단계: 프롬프트 구성
    user_message = _build_message(ticker, quick_look_data, news, analyst)

    # 3단계: Claude 호출
    result = call_claude(SYSTEM_PROMPT, user_message)

    if result["parsed"]:
        filtered = {k: v for k, v in result["data"].items() if k in _ALLOWED_KEYS}
        return {
            "agent": "news",
            "status": "success",
            **filtered,
        }

    # JSON 파싱 실패해도 raw_output이 있으면 부분 성공으로 처리
    if result.get("raw_output"):
        logger.warning("News Agent: JSON 파싱 실패, raw_output 반환")
        return {
            "agent": "news",
            "status": "partial",
            "raw_output": result["raw_output"],
            "summary": result["raw_output"][:500],
        }

    raise RuntimeError(f"News Agent 실패: {result.get('error', 'unknown')}")


def _build_message(
    ticker: str,
    quick_look_data: dict,
    news: Optional[dict],
    analyst: Optional[dict],
) -> str:
    """Claude에게 보낼 user_message를 조립한다."""
    parts = [f"종목: {ticker}"]

    # 시세 정보
    price = quick_look_data.get("price")
    change_pct = quick_look_data.get("change_percent")
    if price is not None:
        parts.append(f"현재 주가: ${price} ({change_pct:+.2f}%)" if change_pct else f"현재 주가: ${price}")

    sector = quick_look_data.get("sector")
    if sector:
        parts.append(f"섹터: {sector}")

    # 뉴스
    if news and news.get("articles"):
        articles = news["articles"][:15]
        news_text = json.dumps(
            [{"headline": a.get("headline"), "source": a.get("source"), "summary": a.get("summary")}
             for a in articles],
            ensure_ascii=False, indent=2,
        )
        parts.append(f"\n최근 뉴스 ({len(articles)}건):\n{news_text}")
    else:
        parts.append("\n최근 뉴스: 없음")

    # 애널리스트 추천
    if analyst:
        parts.append(
            f"\n애널리스트 추천:\n"
            f"  Strong Buy: {analyst.get('strong_buy', 0)}\n"
            f"  Buy: {analyst.get('buy', 0)}\n"
            f"  Hold: {analyst.get('hold', 0)}\n"
            f"  Sell: {analyst.get('sell', 0)}\n"
            f"  Strong Sell: {analyst.get('strong_sell', 0)}"
        )
    else:
        parts.append("\n애널리스트 추천: 데이터 없음")

    return "\n".join(parts)
