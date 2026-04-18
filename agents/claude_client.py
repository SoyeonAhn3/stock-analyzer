"""Claude API 기본 호출 + JSON 파싱 공통 모듈.

사용법:
    from agents.claude_client import call_claude
    result = call_claude(system_prompt, user_message)
    # {"parsed": True, "data": {...}} 또는
    # {"parsed": False, "raw_output": "...", "error": "..."}
"""

import json
import logging
from typing import Any

from anthropic import Anthropic

from config.api_config import ANTHROPIC_API_KEY
from utils.usage_tracker import usage_tracker

logger = logging.getLogger(__name__)

# Claude 모델 설정
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 2048
CLAUDE_TIMEOUT = 60  # seconds


def call_claude(system_prompt: str, user_message: str) -> dict[str, Any]:
    """Claude API를 호출하고 JSON 파싱을 시도한다.

    Args:
        system_prompt: AI 역할 설정 (예: "너는 주식 뉴스 분석 전문가야")
        user_message: 분석할 데이터 및 지시사항

    Returns:
        성공: {"parsed": True, "data": {분석 결과 dict}}
        파싱 실패: {"parsed": False, "raw_output": "AI 원본 응답", "error": "파싱 에러 메시지"}
        호출 실패: {"parsed": False, "raw_output": "", "error": "에러 메시지"}
    """
    # 일일 한도 체크
    if usage_tracker.is_exhausted:
        return {
            "parsed": False,
            "raw_output": "",
            "error": "일일 AI 사용 한도(100회)에 도달했습니다.",
        }

    if not ANTHROPIC_API_KEY:
        return {
            "parsed": False,
            "raw_output": "",
            "error": "ANTHROPIC_API_KEY가 설정되지 않았습니다.",
        }

    try:
        client = Anthropic(api_key=ANTHROPIC_API_KEY, timeout=CLAUDE_TIMEOUT)
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": "{"},
            ],
            stop_sequences=["```"],
        )

        # 사용량 카운트
        usage_tracker.increment()

        raw_text = "{" + response.content[0].text
        logger.info("Claude 응답 수신 (tokens: input=%s, output=%s)",
                     response.usage.input_tokens, response.usage.output_tokens)

        # JSON 파싱 시도
        return _parse_json_response(raw_text)

    except Exception as e:
        logger.error("Claude API 호출 실패: %s", e)
        return {
            "parsed": False,
            "raw_output": "",
            "error": str(e),
        }


def _parse_json_response(raw_text: str) -> dict[str, Any]:
    """AI 응답에서 JSON을 추출하여 파싱한다."""
    # 1차: 전체 텍스트가 JSON인 경우
    try:
        data = json.loads(raw_text)
        return {"parsed": True, "data": data}
    except json.JSONDecodeError:
        pass

    # 2차: ```json ... ``` 블록 추출
    if "```json" in raw_text:
        try:
            start = raw_text.index("```json") + 7
            end = raw_text.index("```", start)
            data = json.loads(raw_text[start:end].strip())
            return {"parsed": True, "data": data}
        except (ValueError, json.JSONDecodeError):
            pass

    # 3차: { } 블록 추출 (가장 바깥 중괄호)
    first_brace = raw_text.find("{")
    last_brace = raw_text.rfind("}")
    if first_brace != -1 and last_brace > first_brace:
        try:
            data = json.loads(raw_text[first_brace:last_brace + 1])
            return {"parsed": True, "data": data}
        except json.JSONDecodeError:
            pass

    # 파싱 실패 — raw_output 보존
    logger.warning("JSON 파싱 실패. raw_output 보존.")
    return {
        "parsed": False,
        "raw_output": raw_text,
        "error": "JSON 파싱 실패",
    }
