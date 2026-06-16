"""무료체험 크레딧 API — Phase 14.

지갑(크레딧) 상태 조회만 노출한다.
신원은 Google 로그인(Authorization: Bearer <ID 토큰>)으로 식별하며,
검증된 sub가 지갑 키가 된다 — backend/auth.py 참조.

예약/확정/환불(reserve/commit/release)은 사용자가 직접 호출하지 않고
분석 엔드포인트(analysis.py) 내부에서 처리하므로 여기 노출하지 않는다.
"""

from fastapi import APIRouter, Depends

from backend.auth import get_current_user
from services.trial_service import get_status

router = APIRouter()


@router.get("/trial/status")
def trial_status(user: dict = Depends(get_current_user)):
    """로그인 계정의 지갑 상태 (balance / held / available)."""
    return get_status(user["sub"])
