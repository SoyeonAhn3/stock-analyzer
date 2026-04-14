"""가격 알림 엔드포인트 — 알림 CRUD + 트리거 체크."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from data.alerts import create_alert, get_active_alerts, delete_alert, check_triggered

router = APIRouter()


class AlertCreateRequest(BaseModel):
    ticker: str
    target_price: float
    direction: str  # "above" | "below"


@router.post("/alerts")
def create(req: AlertCreateRequest):
    """알림 생성."""
    try:
        result = create_alert(req.ticker, req.target_price, req.direction)
        return result
    except ValueError as e:
        raise HTTPException(422, str(e))


@router.get("/alerts")
def list_alerts():
    """활성 알림 목록."""
    return {"alerts": get_active_alerts()}


@router.delete("/alerts/{alert_id}")
def remove(alert_id: int):
    """알림 삭제."""
    try:
        delete_alert(alert_id)
        return {"status": "deleted", "id": alert_id}
    except KeyError as e:
        raise HTTPException(404, str(e))


@router.get("/alerts/triggered")
def triggered():
    """트리거된 알림 조회. 현재가를 체크하여 조건 충족된 알림 반환."""
    results = check_triggered()
    return {"triggered": results}
