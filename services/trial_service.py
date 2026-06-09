"""무료체험 크레딧 지갑 서비스 — Phase 14.

기기별 크레딧 지갑(wallets) + 거래 원장(ledger) 기반.
핵심 공식: 사용 가능 크레딧 = balance - held

크레딧 흐름 (예약 → 확정/환불):
    reserve_credit()  분석 시작 시 1개 잠금(hold)
    commit_credit()   분석 성공 시 실제 차감 (balance-1, held-1)
    release_credit()  분석 실패 시 환불 (held-1, balance 불변)

지갑 변경과 원장 기록은 항상 한 트랜잭션으로 묶어 정합성을 보장한다.
ref_id(분석 요청당 1개)로 멱등성을 보장한다 — 같은 요청 재시도 시 중복 차감 없음.

사용법:
    from services.trial_service import reserve_credit, commit_credit, release_credit
    r = reserve_credit(device_id, ref_id)
    if r["ok"]:
        ...  # 분석 실행
        commit_credit(device_id, ref_id)   # 성공
    else:
        ...  # HTTP 429
"""

import logging
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

from data.database import get_connection
from services.email_sender import send_verification_email

logger = logging.getLogger(__name__)

INITIAL_CREDITS = 3          # 익명 기본 크레딧
EMAIL_BONUS = 3              # 이메일 인증 시 추가 크레딧
_CODE_EXPIRY_MINUTES = 10    # 인증코드 만료
_MAX_CODE_ATTEMPTS = 3       # 코드당 최대 오입력
_MAX_ACTIVE_CODES = 3        # 10분 내 발급 가능한 활성 코드 수


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _fmt(dt: datetime) -> str:
    """SQLite CURRENT_TIMESTAMP과 동일한 'YYYY-MM-DD HH:MM:SS' (UTC) 형식."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _status_dict(row: sqlite3.Row) -> dict:
    """wallets 행 → 상태 dict."""
    balance = row["balance"]
    held = row["held"]
    verified = bool(row["email_verified"])
    return {
        "balance": balance,
        "held": held,
        "available": balance - held,
        "email_verified": verified,
        "tier": "email" if verified else "anonymous",
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
        "SELECT balance, held, email_verified FROM wallets WHERE device_id = ?",
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
    """읽기 전용 상태 — balance/held/available/email_verified/tier."""
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


def request_verification(device_id: str, email: str) -> dict:
    """이메일 인증코드 발급 + 발송.

    Returns:
        {"ok": True, "expires_in": 600}
        {"ok": False, "reason": "email_taken" | "too_many_requests" | "send_failed"}
    """
    email = email.strip().lower()
    conn = get_connection()
    try:
        _ensure_wallet(conn, device_id)

        # 다른 기기가 이미 인증한 이메일이면 거부
        taken = conn.execute(
            "SELECT 1 FROM wallets WHERE email = ? AND email_verified = 1 AND device_id != ? LIMIT 1",
            (email, device_id),
        ).fetchone()
        if taken:
            conn.commit()
            return {"ok": False, "reason": "email_taken"}

        # 스팸 방지: 만료되지 않은 활성 코드 개수 제한
        now_str = _fmt(_now())
        active = conn.execute(
            "SELECT COUNT(*) FROM email_verification WHERE device_id = ? AND expires_at > ?",
            (device_id, now_str),
        ).fetchone()[0]
        if active >= _MAX_ACTIVE_CODES:
            conn.commit()
            return {"ok": False, "reason": "too_many_requests"}

        code = f"{secrets.randbelow(1_000_000):06d}"
        expires_at = _fmt(_now() + timedelta(minutes=_CODE_EXPIRY_MINUTES))
        conn.execute(
            "INSERT INTO email_verification (device_id, email, code, expires_at) VALUES (?, ?, ?, ?)",
            (device_id, email, code, expires_at),
        )
        conn.commit()
    finally:
        conn.close()

    # 발송은 트랜잭션 밖에서 (느린 I/O를 DB 락에서 분리)
    if not send_verification_email(email, code):
        return {"ok": False, "reason": "send_failed"}
    return {"ok": True, "expires_in": _CODE_EXPIRY_MINUTES * 60}


def verify_code(device_id: str, email: str, code: str) -> dict:
    """인증코드 검증. 성공 시 balance += 3 + email_verified=1.

    Returns:
        {"ok": True, ...status}
        {"ok": True, "already": True, ...status} 이미 인증된 기기
        {"ok": False, "reason": "no_code"|"expired"|"too_many_attempts"|"wrong_code"|"email_taken", ...}
    """
    email = email.strip().lower()
    conn = get_connection()
    try:
        _ensure_wallet(conn, device_id)

        wallet = _wallet_row(conn, device_id)
        if wallet["email_verified"]:
            conn.commit()
            return {"ok": True, "already": True, **_status_dict(wallet)}

        row = conn.execute(
            "SELECT id, code, attempts, expires_at FROM email_verification "
            "WHERE device_id = ? AND email = ? ORDER BY id DESC LIMIT 1",
            (device_id, email),
        ).fetchone()
        if row is None:
            conn.commit()
            return {"ok": False, "reason": "no_code"}

        if _fmt(_now()) > row["expires_at"]:
            conn.commit()
            return {"ok": False, "reason": "expired"}

        if row["attempts"] >= _MAX_CODE_ATTEMPTS:
            conn.commit()
            return {"ok": False, "reason": "too_many_attempts"}

        if row["code"] != code:
            conn.execute(
                "UPDATE email_verification SET attempts = attempts + 1 WHERE id = ?",
                (row["id"],),
            )
            conn.commit()
            return {
                "ok": False,
                "reason": "wrong_code",
                "attempts_left": _MAX_CODE_ATTEMPTS - (row["attempts"] + 1),
            }

        # 성공 — 이메일 등록 + 보너스 지급 (UNIQUE 충돌 시 email_taken)
        try:
            conn.execute(
                "UPDATE wallets SET email = ?, email_verified = 1, balance = balance + ?, "
                "updated_at = CURRENT_TIMESTAMP WHERE device_id = ?",
                (email, EMAIL_BONUS, device_id),
            )
        except sqlite3.IntegrityError:
            conn.rollback()
            return {"ok": False, "reason": "email_taken"}

        conn.execute(
            "INSERT INTO ledger (device_id, type, amount, ref_id) VALUES (?, 'grant', ?, 'email_verify')",
            (device_id, EMAIL_BONUS),
        )
        conn.commit()
        return {"ok": True, **_status_dict(_wallet_row(conn, device_id))}
    finally:
        conn.close()
