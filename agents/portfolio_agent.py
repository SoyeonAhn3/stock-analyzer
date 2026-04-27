"""포트폴리오 AI 리포트 에이전트.

Step 2(portfolio_calculator)의 정량 분석 결과를 받아
자연어 해석 + 리밸런싱 제안을 JSON으로 반환한다.

사용법:
    from agents.portfolio_agent import generate_report
    report = generate_report(analysis_data)
"""

import json
import logging
from typing import Any

from agents.claude_client import call_claude

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """너는 CFA 자격을 보유한 포트폴리오 분석 전문가야.
사용자의 포트폴리오 정량 분석 결과를 받아 자연어 리포트를 작성해.

## 핵심 규칙

1. 주어진 숫자를 재계산하지 마. 해석만 해.
2. 모든 제안에는 반드시 근거 숫자를 인용해.
3. 리밸런싱 제안은 구체적으로 해 (어떤 종목/ETF를, 왜, 얼마나).
4. 한국어로 작성해.

## 판단 기준표

| 지표 | 기준 | 판단 |
|---|---|---|
| HHI > 0.25 | 집중 위험 | "포트폴리오가 소수 종목에 집중되어 있습니다" |
| 단일 섹터 > 40% | 섹터 쏠림 | "섹터 분산이 필요합니다" |
| 상관계수 > 0.75 + 같은 섹터 | 동일 베팅 | "실질 분산 효과가 없습니다" |
| Beta > 1.5 | 고위험 | "시장 대비 변동이 큽니다" |
| MDD < -20% | 심리적 부담 | "하락장에서 큰 손실이 발생할 수 있습니다" |
| Sharpe < 0.5 | 비효율 | "위험 대비 수익이 부족합니다" |
| 유동성 flag = danger | 즉시 경고 | "매도 시 슬리피지가 발생할 수 있습니다" |
| PER > 30 비중 > 50% | 금리 민감 | "금리 인상기에 취약합니다" |
| missing_sectors > 7 | 섹터 공백 | "방어 섹터 편입을 고려하세요" |

## 리밸런싱 제안 규칙

- 축소 제안: 현재 비중 → 목표 비중을 명시해.
- 신규 편입 제안: 구체적 ETF 또는 종목명 + 목표 비중을 제시해.
- 전후 비교표에는 반드시 tech_pct, defensive_pct, hhi, estimated_sharpe를 포함해.
- 종목이 1개인 경우에도 분산 투자를 위한 구체적 편입 제안을 해.

## 출력 JSON 스키마 (반드시 이 구조를 따라)

{
  "summary": "포트폴리오 전체 한 줄 요약 (50자 이내)",
  "concentration": {
    "level": "HIGH 또는 MEDIUM 또는 LOW",
    "detail": "집중도 상세 설명 (HHI, 섹터 비중 인용)"
  },
  "risk_assessment": {
    "score": "risk_rating 숫자 (예: 6.4)",
    "detail": "위험 평가 상세 설명"
  },
  "strengths": ["강점1 (근거 숫자 포함)", "강점2"],
  "risks": ["리스크1 (근거 숫자 포함)", "리스크2"],
  "rebalancing": [
    {
      "action": "구체적 행동 (예: NVDA 비중 32% → 20% 축소)",
      "reason": "근거 (숫자 인용)"
    }
  ],
  "rebalancing_comparison": {
    "before": {"tech_pct": 0, "defensive_pct": 0, "hhi": 0, "estimated_sharpe": 0},
    "after": {"tech_pct": 0, "defensive_pct": 0, "hhi": 0, "estimated_sharpe": 0}
  },
  "macro_warning": "거시 경제 관련 경고 (없으면 null)",
  "style_summary": "스타일 요약 한 줄",
  "disclaimer": "본 분석은 AI가 생성한 참고 자료이며, 투자 자문이 아닙니다."
}"""

_REQUIRED_FIELDS = {
    "summary", "strengths", "risks", "rebalancing", "disclaimer",
}

_MAX_TOKENS = 4096


def generate_report(analysis: dict[str, Any]) -> dict[str, Any] | None:
    """Step 2 분석 결과를 AI 리포트로 변환한다.

    Args:
        analysis: run_analysis()의 반환값 (concentration, risk, performance 등)

    Returns:
        성공: AI 리포트 dict
        실패: None
    """
    user_message = _build_user_message(analysis)

    result = call_claude(SYSTEM_PROMPT, user_message, max_tokens=_MAX_TOKENS)

    if result.get("parsed") and result.get("data"):
        report = result["data"]
        report = _ensure_required_fields(report)
        return report

    logger.warning("1차 AI 리포트 생성 실패, 재시도: %s", result.get("error"))
    retry = call_claude(SYSTEM_PROMPT, user_message, max_tokens=_MAX_TOKENS)

    if retry.get("parsed") and retry.get("data"):
        report = retry["data"]
        report = _ensure_required_fields(report)
        return report

    logger.error("AI 리포트 생성 최종 실패: %s", retry.get("error"))
    return None


def _build_user_message(analysis: dict[str, Any]) -> str:
    """분석 데이터를 AI에게 전달할 메시지로 조립한다."""
    sections = []

    sections.append("아래는 사용자 포트폴리오의 정량 분석 결과입니다. 이 숫자를 기반으로 리포트를 작성해주세요.\n")

    key_order = [
        ("concentration", "집중도 분석"),
        ("fundamentals", "가중평균 펀더멘털"),
        ("performance", "성과 분석"),
        ("risk", "위험 분석"),
        ("style", "스타일 분류"),
        ("macro", "거시 노출도"),
        ("scores", "4대 점수 (0~100)"),
    ]

    for key, label in key_order:
        data = analysis.get(key)
        if data is None:
            continue

        display = _simplify_for_prompt(key, data)
        sections.append(f"### {label}\n```json\n{json.dumps(display, ensure_ascii=False, default=str, indent=2)}\n```")

    return "\n\n".join(sections)


def _simplify_for_prompt(key: str, data: Any) -> Any:
    """토큰 절약을 위해 상관관계 행렬 등 큰 데이터를 축약한다."""
    if key != "risk" or not isinstance(data, dict):
        return data

    simplified = dict(data)

    if "correlation" in simplified and isinstance(simplified["correlation"], dict):
        tickers = list(simplified["correlation"].keys())
        if len(tickers) > 8:
            simplified["correlation"] = f"({len(tickers)}x{len(tickers)} 행렬, high_corr_pairs 참조)"
        elif len(tickers) == 0:
            simplified["correlation"] = "단일 종목 (상관관계 없음)"

    return simplified


def _ensure_required_fields(report: dict[str, Any]) -> dict[str, Any]:
    """필수 필드가 누락된 경우 기본값을 채운다."""
    defaults = {
        "summary": "분석 결과를 확인해주세요.",
        "strengths": [],
        "risks": [],
        "rebalancing": [],
        "disclaimer": "본 분석은 AI가 생성한 참고 자료이며, 투자 자문이 아닙니다.",
    }

    for field, default in defaults.items():
        if field not in report or report[field] is None:
            report[field] = default

    return report
