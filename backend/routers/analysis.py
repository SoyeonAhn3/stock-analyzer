"""AI 분석 엔드포인트 — 5-Agent 파이프라인 실행 + 캐시 + 무료체험 게이트."""

import asyncio
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException

from data.quote import get_quote
from data.fundamentals import get_fundamentals
from data.technicals import get_technicals
from data.analysis_cache import get_cached_analysis, save_analysis
from agents.orchestrator import run_analysis
from backend.auth import get_current_user
from services.trial_service import reserve_credit, commit_credit, release_credit, get_status

router = APIRouter()


@router.post("/analysis/{ticker}")
async def analyze(
    ticker: str,
    force: bool = False,
    user: dict = Depends(get_current_user),
    x_request_id: Optional[str] = Header(None),
):
    """AI Deep Analysis 실행 (1~2분 소요).

    Quick Look 데이터를 수집한 뒤 5-Agent 파이프라인에 전달한다.

    무료체험 게이트 (Phase 14):
        - Google 로그인 필수 (get_current_user). 검증된 sub가 지갑 키.
        - 캐시 히트는 게이트 이전 → 크레딧 차감 없음 (무료)
        - 예약(reserve) → 성공 시 확정(commit) / 실패 시 환불(release)
        - X-Request-Id = 멱등성 키 (재시도 시 중복 차감 방지). 없으면 서버가 생성
    """
    ticker = ticker.upper()
    sub = user["sub"]

    # 캐시 확인 (24시간 TTL) — force=True이면 캐시 무시. 캐시 히트는 무료.
    if not force:
        cached = get_cached_analysis(ticker, include_meta=True)
        if cached:
            return cached

    # ── 무료체험 게이트: 예약 ──
    ref_id = x_request_id or f"auto-{uuid4()}"
    reserved = reserve_credit(sub, ref_id)
    if not reserved["ok"]:
        raise HTTPException(
            status_code=429,
            detail={"error": "trial_limit_reached", **reserved},
        )

    try:
        # Quick Look 데이터 수집 (3개 독립 호출 병렬 실행)
        quote_data, fundamentals_data, technicals_data = await asyncio.gather(
            asyncio.to_thread(get_quote, ticker),
            asyncio.to_thread(get_fundamentals, ticker),
            asyncio.to_thread(get_technicals, ticker),
        )
        if quote_data is None:
            raise HTTPException(404, f"Cannot find ticker {ticker}")

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
    except Exception:
        # 데이터 수집/티커 오류/예외 → 환불 후 그대로 전파
        release_credit(sub, ref_id)
        raise

    # 하드 실패 (전 에이전트 실패 → analyst None): 차감하지 않고 환불
    if result.get("analyst") is None:
        release_credit(sub, ref_id)
        result["wallet"] = get_status(sub)
        return result

    # ── 성공: 캐시 저장 + 확정(차감) ──
    save_analysis(ticker, result)
    commit_credit(sub, ref_id)
    result["wallet"] = get_status(sub)

    return result


@router.get("/analysis/{ticker}/cache")
def get_cache(ticker: str):
    """캐시된 분석 결과 조회 (AI 호출 없음)."""
    ticker = ticker.upper()
    cached = get_cached_analysis(ticker, include_meta=True)
    if not cached:
        raise HTTPException(404, "No cached analysis")
    return cached
