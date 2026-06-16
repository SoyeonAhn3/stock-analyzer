"""무료체험 크레딧 지갑 서비스 — Phase 14.

계정별 크레딧 지갑(wallets) + 거래 원장(ledger) 기반.
핵심 공식: 사용 가능 크레딧 = balance - held

신원 키:
    지갑의 키(device_id 컬럼)에는 **검증된 Google 계정 ID(sub)**가 들어간다.
    sub는 구글이 서명한 위조 불가 값이므로 안전한 지갑 키가 된다.
    (2026-06-15 피벗: 이메일 6자리 코드 인증 → Google OAuth 로그인.
     지갑/원장/hold 코어는 그대로 재사용하고 신원 키 값만 교체했다.
     컬럼명 device_id는 마이그레이션 없이 유지한다.)

크레딧 흐름 (예약 → 확정/환불):
    reserve_credit()  분석 시작 시 1개 잠금(hold)
    commit_credit()   분석 성공 시 실제 차감 (balance-1, held-1)
    release_credit()  분석 실패 시 환불 (held-1, balance 불변)

지갑 변경과 원장 기록은 항상 한 트랜잭션으로 묶어 정합성을 보장한다.
ref_id(분석 요청당 1개)로 멱등성을 보장한다 — 같은 요청 재시도 시 중복 차감 없음.

사용법:
    from services.trial_service import reserve_credit, commit_credit, release_credit
    r = reserve_credit(sub, ref_id)
    if r["ok"]:
        ...  # 분석 실행
        commit_credit(sub, ref_id)   # 성공
    else:
        ...  # HTTP 429
"""

import logging
import sqlite3

from data.database import get_connection

logger = logging.getLogger(__name__)

INITIAL_CREDITS = 3          # 로그인 계정 기본 크레딧


def _status_dict(row: sqlite3.Row) -> dict:
    """wallets 행 → 상태 dict."""
    balance = row["balance"]
    held = row["held"]
    return {
        "balance": balance,
        "held": held,
        "available": balance - held,
    }


def _ensure_wallet(conn: sqlite3.Connection, device_id: str) -> bool:
    """지갑이 없으면 생성. 새로 만든 경우 grant 원장 기록. (커밋은 호출자 책임)

    Returns:
        새로 생성했으면 True.
    """
    cur = conn.execute("INSERT OR IGNORE INTO wallets (device_id) VALUES (?)", (device_id,))
    created = cur.rowcount == 1
    if created:
        conn.execute(
            "INSERT INTO ledger (device_id, type, amount, ref_id) VALUES (?, 'grant', ?, 'signup')",
            (device_id, INITIAL_CREDITS),
        )
    return created


def _wallet_row(conn: sqlite3.Connection, device_id: str) -> sqlite3.Row:
    return conn.execute(
        "SELECT balance, held FROM wallets WHERE device_id = ?",
        (device_id,),
    ).fetchone()


def _has_ledger(conn: sqlite3.Connection, device_id: str, ref_id: str, type_: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM ledger WHERE device_id = ? AND ref_id = ? AND type = ? LIMIT 1",
        (device_id, ref_id, type_),
    ).fetchone() is not None


def get_or_create_user(device_id: str) -> dict:
    """지갑 조회/생성 후 상태 반환."""
    conn = get_connection()
    try:
        _ensure_wallet(conn, device_id)
        conn.commit()
        return _status_dict(_wallet_row(conn, device_id))
    finally:
        conn.close()


def get_status(device_id: str) -> dict:
    """읽기 전용 상태 — balance/held/available."""
    return get_or_create_user(device_id)


def reserve_credit(device_id: str, ref_id: str) -> dict:
    """분석 시작 시 크레딧 1개 예약(hold). 예약+원장이 한 트랜잭션.

    Returns:
        {"ok": True, ...status} 예약 성공
        {"ok": True, "already": True, ...status} 같은 ref_id로 이미 예약됨(멱등)
        {"ok": False, "reason": "no_credit", ...status} 가용 크레딧 없음 → 429
    """
    conn = get_connection()
    try:
        _ensure_wallet(conn, device_id)

        # 멱등성: 같은 요청이 이미 예약됐으면 다시 잡지 않음
        if _has_ledger(conn, device_id, ref_id, "hold"):
            conn.commit()
            return {"ok": True, "already": True, **_status_dict(_wallet_row(conn, device_id))}

        cur = conn.execute(
            "UPDATE wallets SET held = held + 1, updated_at = CURRENT_TIMESTAMP "
            "WHERE device_id = ? AND (balance - held) >= 1",
            (device_id,),
        )
        if cur.rowcount == 1:
            conn.execute(
                "INSERT INTO ledger (device_id, type, amount, ref_id) VALUES (?, 'hold', 1, ?)",
                (device_id, ref_id),
            )
            conn.commit()
            return {"ok": True, **_status_dict(_wallet_row(conn, device_id))}

        conn.rollback()
        return {"ok": False, "reason": "no_credit", **_status_dict(_wallet_row(conn, device_id))}
    finally:
        conn.close()


def commit_credit(device_id: str, ref_id: str) -> dict:
    """분석 성공 시 예약을 실제 차감으로 확정 (balance-1, held-1)."""
    conn = get_connection()
    try:
        if _has_ledger(conn, device_id, ref_id, "commit"):
            return {"ok": True, "already": True, **_status_dict(_wallet_row(conn, device_id))}

        cur = conn.execute(
            "UPDATE wallets SET balance = balance - 1, held = held - 1, updated_at = CURRENT_TIMESTAMP "
            "WHERE device_id = ? AND held >= 1",
            (device_id,),
        )
        if cur.rowcount == 1:
            conn.execute(
                "INSERT INTO ledger (device_id, type, amount, ref_id) VALUES (?, 'commit', -1, ?)",
                (device_id, ref_id),
            )
            conn.commit()
            return {"ok": True, **_status_dict(_wallet_row(conn, device_id))}

        conn.rollback()
        return {"ok": False, "reason": "no_hold", **_status_dict(_wallet_row(conn, device_id))}
    finally:
        conn.close()


def release_credit(device_id: str, ref_id: str) -> dict:
    """분석 실패 시 예약 환불 (held-1, balance 불변)."""
    conn = get_connection()
    try:
        if _has_ledger(conn, device_id, ref_id, "release"):
            return {"ok": True, "already": True, **_status_dict(_wallet_row(conn, device_id))}

        cur = conn.execute(
            "UPDATE wallets SET held = held - 1, updated_at = CURRENT_TIMESTAMP "
            "WHERE device_id = ? AND held >= 1",
            (device_id,),
        )
        if cur.rowcount == 1:
            conn.execute(
                "INSERT INTO ledger (device_id, type, amount, ref_id) VALUES (?, 'release', -1, ?)",
                (device_id, ref_id),
            )
            conn.commit()
            return {"ok": True, **_status_dict(_wallet_row(conn, device_id))}

        conn.rollback()
        return {"ok": False, "reason": "no_hold", **_status_dict(_wallet_row(conn, device_id))}
    finally:
        conn.close()
