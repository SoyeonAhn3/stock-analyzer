"""교차검증 Agent — 3개 Agent 결과 간 모순 탐지.

사용법:
    from agents.cross_validation import run
    result = run(agent_results)
"""

import json
import logging
from typing import Any

from agents.claude_client import call_claude

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """너는 투자 분석 교차검증 전문가야.
3명의 분석가(뉴스, 재무/기술, 거시경제)가 각자 분석 결과를 제출했어.
이들 사이의 모순, 충돌, 합의 사항을 찾아줘.

규칙:
- 각 분석가의 의견이 서로 다른 부분을 명확히 지적해.
- 모순이 투자 판단에 미치는 영향을 평가해.
- 3명 모두 동의하는 사항도 정리해.
- 분석가 의견이 1~2개만 있을 수 있어 (일부 실패). 있는 것만 검증해.

반드시 아래 JSON 형식으로만 답변해:
{
    "conflicts": [
        {"topic": "충돌 주제", "detail": "어떤 모순인지 설명", "severity": "high" | "medium" | "low"}
    ],
    "agreements": ["합의 사항 리스트"],
    "confidence_adjustment": "none" | "downgrade_one" | "downgrade_two",
    "notes": "종합 교차검증 소견 (2~3문장)"
}"""


def run(agent_results: dict[str, Any]) -> dict[str, Any]:
    """교차검증 Agent 실행 (동기 함수).

    Args:
        agent_results: {"news": {...}, "data": {...}, "macro": {...}}
                       일부 키가 없을 수 있음 (Agent 실패 시).

    Returns:
        교차검증 결과 dict. 실패 시 기본 결과 반환 (분석 중단 없음).
    """
    if not agent_results:
        return _default_result("Agent 결과 없음")

    # 프롬프트 구성
    user_message = _build_message(agent_results)

    # Claude 호출
    result = call_claude(SYSTEM_PROMPT, user_message)

    if result["parsed"]:
        return {
            "agent": "cross_validation",
            "status": "success",
            **result["data"],
        }

    if result.get("raw_output"):
        logger.warning("Cross-validation: JSON 파싱 실패, raw_output 반환")
        return {
            "agent": "cross_validation",
            "status": "partial",
            "conflicts": [],
            "agreements": [],
            "confidence_adjustment": "none",
            "notes": result["raw_output"][:500],
        }

    # 교차검증 실패해도 전체 파이프라인은 멈추지 않음
    logger.error("Cross-validation 실패: %s", result.get("error"))
    return _default_result(result.get("error", "unknown"))


def _build_message(agent_results: dict[str, Any]) -> str:
    """Claude에게 보낼 user_message를 조립한다."""
    parts = []

    for agent_name, label in [("news", "뉴스 분석"), ("data", "재무/기술 분석"), ("macro", "거시경제 분석")]:
        result = agent_results.get(agent_name)
        if result:
            # raw_output만 있는 경우 (partial)
            if result.get("status") == "partial":
                parts.append(f"\n[{label}] (부분 결과):\n{result.get('raw_output', result.get('summary', ''))[:800]}")
            else:
                # 정상 결과 — agent, status 키 제외하고 분석 내용만 전달
                content = {k: v for k, v in result.items() if k not in ("agent", "status")}
                parts.append(f"\n[{label}]:\n{json.dumps(content, ensure_ascii=False, indent=2)}")
        else:
            parts.append(f"\n[{label}]: 데이터 없음 (Agent 실패)")

    return "\n".join(parts)


def _default_result(reason: str) -> dict[str, Any]:
    """실패 시 기본 결과. 파이프라인 중단 방지."""
    return {
        "agent": "cross_validation",
        "status": "skipped",
        "conflicts": [],
        "agreements": [],
        "confidence_adjustment": "none",
        "notes": f"교차검증 생략: {reason}",
    }
