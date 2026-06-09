"""시장 데이터 엔드포인트 — 지수, 급등락, 뉴스.

외부 소스(yahoo/finviz/finnhub)가 사내망 방화벽 등으로 차단되면
get_* 함수가 None을 반환한다. 이때 503으로 실패시키는 대신
정적 더미 데이터(data.fallback_data)를 반환하고 응답 헤더에
X-Data-Fallback: 1 을 실어 프론트가 '샘플 데이터' 안내를 띄우게 한다.
"""

from fastapi import APIRouter, Response

from data.market_overview import get_market_indices, get_top_movers, get_market_news
from data.fallback_data import FALLBACK_INDICES, FALLBACK_MOVERS, FALLBACK_NEWS

router = APIRouter()


def _fallback(response: Response, data):
    """더미 데이터 반환 시 X-Data-Fallback 헤더를 세팅."""
    response.headers["X-Data-Fallback"] = "1"
    return data


@router.get("/market/indices")
def indices(response: Response):
    """주요 시장 지수 조회 (SPY, QQQ, DIA, BTC, ETH, VIX)."""
    result = get_market_indices()
    if result is None:
        return _fallback(response, FALLBACK_INDICES)
    return result


@router.get("/market/movers")
def movers(response: Response):
    """급등 Top 5 + 급락 Top 5."""
    result = get_top_movers()
    if result is None:
        return _fallback(response, FALLBACK_MOVERS)
    return result


@router.get("/market/news")
def news(response: Response, limit: int = 5):
    """시장 뉴스 헤드라인."""
    result = get_market_news(limit=limit)
    if result is None:
        return _fallback(response, FALLBACK_NEWS[:limit])
    return result
