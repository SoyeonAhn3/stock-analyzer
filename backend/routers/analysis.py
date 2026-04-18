"""AI 분석 엔드포인트 — 5-Agent 파이프라인 실행 + 캐시."""

from fastapi import APIRouter, HTTPException

from data.quote import get_quote
from data.fundamentals import get_fundamentals
from data.technicals import get_technicals
from data.analysis_cache import get_cached_analysis, save_analysis
from agents.orchestrator import run_analysis

router = APIRouter()


@router.post("/analysis/{ticker}")
async def analyze(ticker: str):
    """AI Deep Analysis 실행 (1~2분 소요).

    Quick Look 데이터를 수집한 뒤 5-Agent 파이프라인에 전달한다.
    """
    ticker = ticker.upper()

    # 캐시 확인 (24시간 TTL)
    cached = get_cached_analysis(ticker)
    if cached:
        return cached

    # Quick Look 데이터 수집
    quote_data = get_quote(ticker)
    if quote_data is None:
        raise HTTPException(404, f"Cannot find ticker {ticker}")

    fundamentals_data = get_fundamentals(ticker)
    technicals_data = get_technicals(ticker)

    # Agent들이 평탄(flat) 구조의 quick_look_data를 기대함 (key → value 직접 접근)
    quick_look_data = {"ticker": ticker}
    for source in (quote_data, fundamentals_data, technicals_data):
        if source:
            for k, v in source.items():
                if k == "ticker" or v is None:
                    continue
                quick_look_data[k] = v

    # AI 분석 실행 (async)
    result = await run_analysis(quick_look_data)

    # 결과 캐시 저장
    save_analysis(ticker, result)

    return result
