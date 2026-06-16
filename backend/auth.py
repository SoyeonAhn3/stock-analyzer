"""Google ID 토큰 검증 — Phase 14 무료체험 로그인.

프론트엔드(@react-oauth/google)가 발급받은 Google ID 토큰을
`Authorization: Bearer <token>` 헤더로 받아 서버에서 검증한다.
검증에 성공하면 구글이 서명한 `sub`(계정 고유 ID)를 신원 키로 사용한다 —
위조가 불가능하므로 무료체험 지갑의 안전한 키가 된다.

사용법 (FastAPI 의존성):
    from fastapi import Depends
    from backend.auth import get_current_user

    @router.post("/something")
    def handler(user: dict = Depends(get_current_user)):
        sub = user["sub"]
"""

import logging
import os
from typing import Optional

from fastapi import Header, HTTPException
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

logger = logging.getLogger(__name__)

# 구글 공개키 조회용 transport
_transport = google_requests.Request()


def _client_id() -> str:
    """백엔드 audience 검증용 클라이언트 ID — 프론트의 VITE_GOOGLE_CLIENT_ID와 동일 값.

    호출 시점에 env를 읽는다(모듈 로드 시점이 아니라) — load_dotenv 실행 순서나
    라우터 import 순서와 무관하게 항상 최신 값을 보장하기 위함.
    미설정 시 audience 검증을 건너뛴다(개발용). 운영에서는 반드시 설정할 것.
    """
    return os.getenv("GOOGLE_CLIENT_ID", "")


def verify_google_token(token: str) -> dict:
    """Google ID 토큰을 검증하고 사용자 정보를 반환.

    Raises:
        ValueError: 토큰이 위조/만료/잘못된 audience인 경우 (google-auth가 발생)
    """
    info = id_token.verify_oauth2_token(token, _transport, _client_id() or None)
    return {
        "sub": info["sub"],
        "email": info.get("email"),
        "name": info.get("name"),
        "picture": info.get("picture"),
    }


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """`Authorization: Bearer <token>` 헤더에서 사용자를 검증·추출하는 의존성.

    Returns:
        {"sub", "email", "name", "picture"}

    Raises:
        HTTPException 401: 헤더 누락 / 형식 오류 / 토큰 검증 실패
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Login required")

    token = authorization[7:].strip()
    if not token:
        raise HTTPException(401, "Login required")

    try:
        return verify_google_token(token)
    except ValueError as exc:
        logger.warning("Google token verification failed: %s", exc)
        raise HTTPException(401, "Invalid or expired login")
