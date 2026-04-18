"""종합 판단 Agent — 모든 분석 결과를 종합하여 BUY/HOLD/SELL 판단.

사용법:
    from agents.analyst_agent import run
    result = run(agent_results, cross_validation)
"""

import json
import logging
from typing import Any

from agents.claude_client import call_claude

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """너는 시니어 주식 애널리스트야.
여러 분석가의 결과와 교차검증을 종합하여 최종 투자 의견을 제시해.

규칙:
- 주어진 데이터만 기반으로 판단해. 새로운 숫자를 만들지 마.
- 반드시 Bull case(긍정 시나리오)와 Bear case(부정 시나리오)를 함께 제시해.
- 긍정 신호가 우세하면 BUY, 부정 신호가 우세하면 SELL을 명확히 줘.
- HOLD는 긍정/부정이 정말 비슷하게 혼재할 때만 사용해.
- confidence 기준:
  - high: 3개 Agent 의견 방향 일치 + 기술/재무 뒷받침
  - medium: 2개 일치 또는 일부 혼재
  - low: 전반적으로 신호 혼재 또는 데이터 부족
- 분석 결과가 부분적일 수 있으니 (일부 Agent 실패) 가용 데이터 범위 내에서 판단해.
- disclaimer는 항상 포함하되, 판단 자체는 명확하게.

반드시 아래 JSON 형식으로만 답변해:
{
    "verdict": "BUY" | "HOLD" | "SELL",
    "confidence": "high" | "medium" | "low",
    "bull_case": "긍정 시나리오 설명 (2~3문장)",
    "bear_case": "부정 시나리오 설명 (2~3문장)",
    "key_factors": ["판단 근거 리스트 (3~5개)"],
    "risk_level": "high" | "medium" | "low",
    "time_horizon": "short_term" | "medium_term" | "long_term",
    "summary": "종합 분석 요약 (3~4문장)",
    "disclaimer": "본 분석은 AI가 생성한 참고 자료이며, 투자 자문이 아닙니다. 실제 투자 판단은 본인 책임입니다."
}"""

# 신뢰도 하향 매핑
_CONFIDENCE_DOWNGRADE = {
    "high": "medium",
    "medium": "low",
    "low": "low",
}


def run(
    agent_results: dict[str, Any],
    cross_validation: dict[str, Any],
    success_count: int = 3,
) -> dict[str, Any]:
    """Analyst Agent 실행 (동기 함수).

    Args:
        agent_results: {"news": {...}, "data": {...}, "macro": {...}}
        cross_validation: 교차검증 결과
        success_count: 성공한 Agent 수 (3/2/1)

    Returns:
        최종 판단 결과 dict.
    """
    # 프롬프트 구성
    user_message = _build_message(agent_results, cross_validation, success_count)

    # Claude 호출
    result = call_claude(SYSTEM_PROMPT, user_message)

    if result["parsed"]:
        final = {
            "agent": "analyst",
            "status": "success",
            **result["data"],
        }
    elif result.get("raw_output"):
        logger.warning("Analyst Agent: JSON 파싱 실패, raw_output 반환")
        final = {
            "agent": "analyst",
            "status": "partial",
            "verdict": "HOLD",
            "confidence": "low",
            "summary": result["raw_output"][:500],
            "disclaimer": "본 분석은 AI가 생성한 참고 자료이며, 투자 자문이 아닙니다.",
        }
    else:
        logger.error("Analyst Agent 실패: %s", result.get("error"))
        final = {
            "agent": "analyst",
            "status": "failed",
            "verdict": "HOLD",
            "confidence": "low",
            "summary": f"분석 실패: {result.get('error', 'unknown')}",
            "disclaimer": "본 분석은 AI가 생성한 참고 자료이며, 투자 자문이 아닙니다.",
        }

    # Graceful Degradation: 성공 Agent 수에 따라 신뢰도 조정
    final["confidence"] = _adjust_confidence(final.get("confidence", "low"), success_count)

    return final


def _adjust_confidence(confidence: str, success_count: int) -> str:
    """성공한 Agent 수에 따라 신뢰도를 하향 조정한다."""
    if success_count >= 3:
        return confidence  # 유지
    elif success_count == 2:
        return _CONFIDENCE_DOWNGRADE.get(confidence, "low")  # 1단계 하향
    else:
        return "low"  # 1개만 성공 시 무조건 low


def _build_message(
    agent_results: dict[str, Any],
    cross_validation: dict[str, Any],
    success_count: int,
) -> str:
    """Claude에게 보낼 user_message를 조립한다."""
    parts = []

    # 각 Agent 분석 결과
    for agent_name, label in [("news", "뉴스 분석"), ("data", "재무/기술 분석"), ("macro", "거시경제 분석")]:
        result = agent_results.get(agent_name)
        if result:
            content = {k: v for k, v in result.items() if k not in ("agent", "status")}
            parts.append(f"\n[{label}]:\n{json.dumps(content, ensure_ascii=False, indent=2)}")
        else:
            parts.append(f"\n[{label}]: 데이터 없음 (Agent 실패)")

    # 교차검증 결과
    cv_content = {k: v for k, v in cross_validation.items() if k not in ("agent", "status")}
    parts.append(f"\n[교차검증]:\n{json.dumps(cv_content, ensure_ascii=False, indent=2)}")

    # 데이터 완성도 안내
    if success_count < 3:
        parts.append(f"\n⚠️ 참고: {3 - success_count}개 Agent가 실패하여 불완전한 데이터 기반 분석입니다.")

    return "\n".join(parts)
