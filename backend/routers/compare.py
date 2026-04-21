"""종목 비교 엔드포인트."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from data.compare import detect_comparison_type, get_comparison_data
from agents.compare_agent import run_compare_analysis

router = APIRouter()


class CompareRequest(BaseModel):
    tickers: list[str]


@router.post("/compare")
def compare(req: CompareRequest):
    """비교 유형 감지 + 비교 데이터 조회."""
    if len(req.tickers) < 2 or len(req.tickers) > 3:
        raise HTTPException(422, "2~3 tickers required")

    tickers = [t.upper() for t in req.tickers]
    comparison_type = detect_comparison_type(tickers)
    comparison_data = get_comparison_data(tickers)

    return {
        "comparison_type": comparison_type,
        "data": comparison_data,
    }


@router.post("/compare/analyze")
def compare_analyze(req: CompareRequest):
    """AI 비교 분석 실행."""
    if len(req.tickers) < 2 or len(req.tickers) > 3:
        raise HTTPException(422, "2~3 tickers required")

    tickers = [t.upper() for t in req.tickers]
    comparison_type = detect_comparison_type(tickers)
    comparison_data = get_comparison_data(tickers)

    result = run_compare_analysis(
        tickers=tickers,
        comparison_type=comparison_type,
        ticker_data=comparison_data.get("data", {}),
        sector_pe=comparison_data.get("sector_pe"),
        macro=comparison_data.get("macro"),
    )
    return result
