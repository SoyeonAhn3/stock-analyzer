"""검색 자동완성 엔드포인트."""

from fastapi import APIRouter

from data.ticker_list import search_tickers

router = APIRouter()


@router.get("/search")
def search(q: str = "", limit: int = 8):
    """티커/종목명 검색. 자동완성용.

    Query Params:
        q: 검색어 (예: "NV", "apple")
        limit: 최대 결과 수 (기본 8)
    """
    results = search_tickers(q, limit=min(limit, 20))
    return {"results": results}
