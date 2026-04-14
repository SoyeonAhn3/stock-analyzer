"""가격 알림 모듈 — 목표가 설정 + 트리거 체크 (SQLite 기반).

사용법:
    from data.alerts import create_alert, get_active_alerts, check_triggered
    create_alert("NVDA", 150.0, "above")
    triggered = check_triggered()
"""

import logging
from datetime import datetime
from typing import Any

from data.database import get_connection
from data.quote import get_quote

logger = logging.getLogger(__name__)


def create_alert(ticker: str, target_price: float, direction: str) -> dict[str, Any]:
    """알림 생성.

    Args:
        ticker: 종목 티커
        target_price: 목표가
        direction: "above" (이상 돌파) | "below" (이하 하락)

    Returns:
        생성된 알림 dict
    """
    ticker = ticker.upper()
    if direction not in ("above", "below"):
        raise ValueError(f"direction은 'above' 또는 'below'만 가능: {direction}")

    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO price_alerts (ticker, target_price, direction) VALUES (?, ?, ?)",
            (ticker, target_price, direction),
        )
        conn.commit()
        alert_id = cursor.lastrowid
        logger.info("Alert created: %s %s $%.2f (id=%d)", ticker, direction, target_price, alert_id)
        return {
            "id": alert_id,
            "ticker": ticker,
            "target_price": target_price,
            "direction": direction,
            "active": True,
        }
    finally:
        conn.close()


def get_active_alerts() -> list[dict[str, Any]]:
    """활성 알림 목록."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, ticker, target_price, direction, created_at FROM price_alerts WHERE active = 1 ORDER BY created_at DESC"
        ).fetchall()
        return [
            {
                "id": row["id"],
                "ticker": row["ticker"],
                "target_price": row["target_price"],
                "direction": row["direction"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]
    finally:
        conn.close()


def delete_alert(alert_id: int) -> None:
    """알림 삭제.

    Raises:
        KeyError: 존재하지 않는 알림
    """
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM price_alerts WHERE id = ?", (alert_id,))
        if cursor.rowcount == 0:
            raise KeyError(f"알림 ID {alert_id}이(가) 존재하지 않습니다.")
        conn.commit()
    finally:
        conn.close()


def check_triggered() -> list[dict[str, Any]]:
    """활성 알림의 트리거 여부 체크. 트리거된 알림은 비활성화.

    Returns:
        트리거된 알림 리스트
    """
    active = get_active_alerts()
    if not active:
        return []

    triggered = []
    conn = get_connection()
    try:
        for alert in active:
            quote = get_quote(alert["ticker"])
            if not quote or not quote.get("price"):
                continue

            current_price = quote["price"]
            hit = False

            if alert["direction"] == "above" and current_price >= alert["target_price"]:
                hit = True
            elif alert["direction"] == "below" and current_price <= alert["target_price"]:
                hit = True

            if hit:
                now = datetime.now().isoformat()
                conn.execute(
                    "UPDATE price_alerts SET active = 0, triggered_at = ? WHERE id = ?",
                    (now, alert["id"]),
                )
                triggered.append({
                    **alert,
                    "current_price": current_price,
                    "triggered_at": now,
                })
                logger.info(
                    "Alert triggered: %s %s $%.2f (current $%.2f)",
                    alert["ticker"], alert["direction"], alert["target_price"], current_price,
                )

        conn.commit()
    finally:
        conn.close()

    return triggered
