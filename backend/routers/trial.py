"""무료체험 크레딧 API — Phase 14.

지갑 상태 조회 + 이메일 인증 코드 요청/검증.
모든 요청은 X-Device-Id 헤더로 기기(지갑)를 식별한다.

예약/확정/환불(reserve/commit/release)은 사용자가 직접 호출하지 않고
분석 엔드포인트(analysis.py) 내부에서 처리하므로 여기 노출하지 않는다.

비즈니스 결과(코드 틀림, 한도 등)는 HTTP 200 + {"ok": false, "reason": ...}로
반환한다 — 프론트가 ok/reason으로 분기. 헤더 누락 등 요청 자체 오류만 4xx.
"""

from typing import Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from services.trial_service import get_status, request_verification, verify_code

router = APIRouter()


def _require_device(x_device_id: Optional[str]) -> str:
    """X-Device-Id 헤더 필수 검증."""
    if not x_device_id:
        raise HTTPException(400, "X-Device-Id header required")
    return x_device_id


class RequestCodeBody(BaseModel):
    email: str


class VerifyBody(BaseModel):
    email: str
    code: str


@router.get("/trial/status")
def trial_status(x_device_id: Optional[str] = Header(None)):
    """현재 기기의 지갑 상태 (balance / held / available / email_verified / tier)."""
    device_id = _require_device(x_device_id)
    return get_status(device_id)


@router.post("/trial/request-code")
def trial_request_code(body: RequestCodeBody, x_device_id: Optional[str] = Header(None)):
    """이메일로 6자리 인증 코드 발송."""
    device_id = _require_device(x_device_id)
    if not body.email.strip():
        raise HTTPException(400, "email required")
    return request_verification(device_id, body.email)


@router.post("/trial/verify")
def trial_verify(body: VerifyBody, x_device_id: Optional[str] = Header(None)):
    """6자리 인증 코드 검증 — 성공 시 크레딧 +3."""
    device_id = _require_device(x_device_id)
    return verify_code(device_id, body.email, body.code)
