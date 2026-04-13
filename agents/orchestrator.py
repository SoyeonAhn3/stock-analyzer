"""Agent 오케스트레이터 — 병렬 실행 + 상태 관리 + Graceful Degradation.

사용법:
    from agents.orchestrator import run_analysis
    result = await run_analysis(quick_look_data)
"""

import asyncio
import logging
from typing import Any, Optional

from agents import news_agent, data_agent, macro_agent
from agents import cross_validation, analyst_agent

logger = logging.getLogger(__name__)

# Agent 타임아웃 (초)
AGENT_TIMEOUT = 30
AGENT_RETRY_DELAY = 15


async def run_analysis(
    quick_look_data: dict,
    agent_overrides: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """AI Deep Analysis 전체 파이프라인 실행.

    Args:
        quick_look_data: Phase 2에서 수집한 데이터
        agent_overrides: 테스트용. Agent 결과를 직접 주입 가능.
                         예: {"news": {...결과 dict...}}

    Returns:
        analysis_state = {
            "ticker": "NVDA",
            "quick_look_data": {...},
            "agent_results": {"news": {...}, "data": {...}, "macro": {...}},
            "agent_status": {"news": "success", "data": "failed", ...},
            "cross_validation": {...},
            "analyst": {...},
            "errors": [],
        }
    """
    ticker = quick_look_data.get("ticker", "UNKNOWN")
    agent_overrides = agent_overrides or {}
    errors = []

    logger.info("=== Deep Analysis 시작: %s ===", ticker)

    # ─── 1단계: 3개 Agent 병렬 실행 ───
    agent_results, agent_status, agent_errors = await _run_parallel_agents(
        ticker, quick_look_data, agent_overrides
    )
    errors.extend(agent_errors)

    success_count = list(agent_status.values()).count("success")
    logger.info("Agent 결과: %d/3 성공 %s", success_count, agent_status)

    # ─── 2단계: Graceful Degradation 판정 ───
    if success_count == 0:
        logger.error("모든 Agent 실패. 분석 중단.")
        return {
            "ticker": ticker,
            "quick_look_data": quick_look_data,
            "agent_results": {},
            "agent_status": agent_status,
            "cross_validation": None,
            "analyst": None,
            "errors": errors,
        }

    # ─── 3단계: 교차검증 ───
    logger.info("교차검증 시작")
    cv_result = cross_validation.run(agent_results)

    # ─── 4단계: 최종 판단 ───
    logger.info("최종 판단 시작")
    analyst_result = analyst_agent.run(agent_results, cv_result, success_count)

    logger.info("=== Deep Analysis 완료: %s → %s (%s) ===",
                ticker, analyst_result.get("verdict"), analyst_result.get("confidence"))

    return {
        "ticker": ticker,
        "quick_look_data": quick_look_data,
        "agent_results": agent_results,
        "agent_status": agent_status,
        "cross_validation": cv_result,
        "analyst": analyst_result,
        "errors": errors,
    }


async def _run_parallel_agents(
    ticker: str,
    quick_look_data: dict,
    agent_overrides: dict,
) -> tuple[dict, dict, list]:
    """3개 Agent를 병렬로 실행하고 결과를 수집한다."""
    agent_results = {}
    agent_status = {}
    errors = []

    agents = {
        "news": news_agent,
        "data": data_agent,
        "macro": macro_agent,
    }

    # override된 Agent는 실제 호출 생략
    for name, mock_result in agent_overrides.items():
        if name in agents:
            agent_results[name] = mock_result
            agent_status[name] = "success"
            del agents[name]
            logger.info("Agent '%s' override 적용", name)

    if not agents:
        return agent_results, agent_status, errors

    # 병렬 실행
    tasks = {
        name: _run_agent_with_retry(name, module, ticker, quick_look_data)
        for name, module in agents.items()
    }

    results = await asyncio.gather(*tasks.values(), return_exceptions=True)

    for name, result in zip(tasks.keys(), results):
        if isinstance(result, Exception):
            agent_status[name] = "failed"
            errors.append(f"{name}: {result}")
            logger.error("Agent '%s' 실패: %s", name, result)
        else:
            agent_results[name] = result
            agent_status[name] = "success"

    return agent_results, agent_status, errors


async def _run_agent_with_retry(
    name: str,
    module: Any,
    ticker: str,
    quick_look_data: dict,
) -> dict[str, Any]:
    """개별 Agent를 타임아웃 + 1회 재시도로 실행한다."""
    for attempt in range(2):  # 최초 시도 + 1회 재시도
        try:
            result = await asyncio.wait_for(
                module.run(ticker, quick_look_data),
                timeout=AGENT_TIMEOUT,
            )
            return result
        except asyncio.TimeoutError:
            logger.warning("Agent '%s' 타임아웃 (시도 %d/2)", name, attempt + 1)
            if attempt == 0:
                await asyncio.sleep(AGENT_RETRY_DELAY)
        except Exception as e:
            logger.warning("Agent '%s' 에러 (시도 %d/2): %s", name, attempt + 1, e)
            if attempt == 0:
                await asyncio.sleep(AGENT_RETRY_DELAY)

    raise RuntimeError(f"Agent '{name}' 2회 시도 모두 실패")
