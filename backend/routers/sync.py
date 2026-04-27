"""포트폴리오 크로스 디바이스 동기화 API."""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.sync_service import (
    create_sync,
    connect_sync,
    push_data,
    pull_data,
    disconnect_sync,
    cleanup_expired,
    ensure_table,
)

logger = logging.getLogger(__name__)

router = APIRouter()

ensure_table()


class CreateRequest(BaseModel):
    pin: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")


class ConnectRequest(BaseModel):
    code: str = Field(min_length=14, max_length=14)
    pin: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")


class PushRequest(BaseModel):
    code: str = Field(min_length=14, max_length=14)
    pin: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")
    data: str


class PullRequest(BaseModel):
    code: str = Field(min_length=14, max_length=14)
    pin: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")


class DisconnectRequest(BaseModel):
    code: str = Field(min_length=14, max_length=14)
    pin: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")


@router.post("/sync/create")
def sync_create(req: CreateRequest):
    """새 동기화 코드 생성."""
    try:
        result = create_sync(req.pin)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/sync/connect")
def sync_connect(req: ConnectRequest):
    """기존 코드로 연결 (코드+PIN 검증)."""
    result = connect_sync(req.code, req.pin)
    if not result.get("success"):
        error = result.get("error")
        if error == "invalid_code":
            raise HTTPException(404, "동기화 코드를 찾을 수 없습니다.")
        if error == "locked":
            raise HTTPException(429, f"{result.get('retry_after', 30)}초 후 다시 시도하세요.")
        if error == "wrong_pin":
            left = result.get("attempts_left", 0)
            raise HTTPException(401, f"PIN이 올바르지 않습니다. (남은 시도: {left}회)")
    return {"success": True}


@router.post("/sync/push")
def sync_push(req: PushRequest):
    """LocalStorage 데이터 → 서버 업로드."""
    result = push_data(req.code, req.pin, req.data)
    if not result.get("success"):
        error = result.get("error")
        if error == "locked":
            raise HTTPException(429, f"{result.get('retry_after', 30)}초 후 다시 시도하세요.")
        if error == "wrong_pin":
            raise HTTPException(401, "PIN이 올바르지 않습니다.")
        raise HTTPException(404, "동기화 코드를 찾을 수 없습니다.")
    return {"success": True, "updated_at": result["updated_at"]}


@router.post("/sync/pull")
def sync_pull(req: PullRequest):
    """서버 → LocalStorage 데이터 다운로드."""
    result = pull_data(req.code, req.pin)
    if not result.get("success"):
        error = result.get("error")
        if error == "locked":
            raise HTTPException(429, f"{result.get('retry_after', 30)}초 후 다시 시도하세요.")
        if error == "wrong_pin":
            raise HTTPException(401, "PIN이 올바르지 않습니다.")
        raise HTTPException(404, "동기화 코드를 찾을 수 없습니다.")
    return {"success": True, "data": result["data"], "updated_at": result["updated_at"]}


@router.delete("/sync/disconnect")
def sync_disconnect(req: DisconnectRequest):
    """동기화 해제 + 서버 데이터 삭제."""
    result = disconnect_sync(req.code, req.pin)
    if not result.get("success"):
        raise HTTPException(401, "인증에 실패했습니다.")
    return {"success": True}


@router.post("/sync/cleanup")
def sync_cleanup():
    """90일 미접속 데이터 정리 (관리용)."""
    deleted = cleanup_expired()
    return {"deleted": deleted}
