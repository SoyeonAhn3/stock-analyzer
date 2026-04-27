"""포트폴리오 크로스 디바이스 동기화 서비스.

동기화 코드(12자리) + PIN(4자리, bcrypt 해시) 기반 무로그인 인증.
SQLite에 저장하며, 90일 미접속 시 자동 삭제.
"""

import logging
import secrets
import string
import time
from datetime import datetime, timedelta, timezone

import bcrypt

from data.database import get_connection

logger = logging.getLogger(__name__)

_CODE_CHARS = string.ascii_uppercase + string.digits
_CODE_LENGTH = 12
_PIN_LENGTH = 4
_MAX_ATTEMPTS = 3
_LOCKOUT_SECONDS = 30
_EXPIRY_DAYS = 90


def _generate_code() -> str:
    raw = "".join(secrets.choice(_CODE_CHARS) for _ in range(_CODE_LENGTH))
    return f"{raw[:4]}-{raw[4:8]}-{raw[8:12]}"


def _hash_pin(pin: str) -> str:
    return bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()


def _verify_pin(pin: str, hashed: str) -> bool:
    return bcrypt.checkpw(pin.encode(), hashed.encode())


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_table() -> None:
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS portfolio_sync (
                code TEXT PRIMARY KEY,
                pin_hash TEXT NOT NULL,
                data TEXT NOT NULL DEFAULT '[]',
                fail_count INTEGER DEFAULT 0,
                locked_until TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_accessed TEXT NOT NULL
            );
        """)
        conn.commit()
    finally:
        conn.close()


def cleanup_expired() -> int:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=_EXPIRY_DAYS)).isoformat()
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM portfolio_sync WHERE last_accessed < ?", (cutoff,)
        )
        conn.commit()
        deleted = cursor.rowcount
        if deleted:
            logger.info("Cleaned up %d expired sync entries", deleted)
        return deleted
    finally:
        conn.close()


def create_sync(pin: str) -> dict:
    if len(pin) != _PIN_LENGTH or not pin.isdigit():
        raise ValueError("PIN must be exactly 4 digits")

    code = _generate_code()
    pin_hash = _hash_pin(pin)
    now = _now_iso()

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO portfolio_sync (code, pin_hash, data, created_at, updated_at, last_accessed) "
            "VALUES (?, ?, '[]', ?, ?, ?)",
            (code, pin_hash, now, now, now),
        )
        conn.commit()
        return {"code": code}
    finally:
        conn.close()


def connect_sync(code: str, pin: str) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT pin_hash, fail_count, locked_until FROM portfolio_sync WHERE code = ?",
            (code,),
        ).fetchone()

        if not row:
            return {"success": False, "error": "invalid_code"}

        if row["locked_until"]:
            lock_time = datetime.fromisoformat(row["locked_until"])
            if datetime.now(timezone.utc) < lock_time:
                remaining = int((lock_time - datetime.now(timezone.utc)).total_seconds())
                return {"success": False, "error": "locked", "retry_after": max(remaining, 1)}

        if not _verify_pin(pin, row["pin_hash"]):
            fail = row["fail_count"] + 1
            locked_until = None
            if fail >= _MAX_ATTEMPTS:
                locked_until = (datetime.now(timezone.utc) + timedelta(seconds=_LOCKOUT_SECONDS)).isoformat()
                fail = 0
            conn.execute(
                "UPDATE portfolio_sync SET fail_count = ?, locked_until = ? WHERE code = ?",
                (fail, locked_until, code),
            )
            conn.commit()
            return {"success": False, "error": "wrong_pin", "attempts_left": _MAX_ATTEMPTS - fail if fail < _MAX_ATTEMPTS else 0}

        conn.execute(
            "UPDATE portfolio_sync SET fail_count = 0, locked_until = NULL, last_accessed = ? WHERE code = ?",
            (_now_iso(), code),
        )
        conn.commit()
        return {"success": True}
    finally:
        conn.close()


def push_data(code: str, pin: str, data: str) -> dict:
    auth = connect_sync(code, pin)
    if not auth.get("success"):
        return auth

    now = _now_iso()
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE portfolio_sync SET data = ?, updated_at = ?, last_accessed = ? WHERE code = ?",
            (data, now, now, code),
        )
        conn.commit()
        return {"success": True, "updated_at": now}
    finally:
        conn.close()


def pull_data(code: str, pin: str) -> dict:
    auth = connect_sync(code, pin)
    if not auth.get("success"):
        return auth

    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT data, updated_at FROM portfolio_sync WHERE code = ?", (code,)
        ).fetchone()
        conn.execute(
            "UPDATE portfolio_sync SET last_accessed = ? WHERE code = ?",
            (_now_iso(), code),
        )
        conn.commit()
        return {
            "success": True,
            "data": row["data"],
            "updated_at": row["updated_at"],
        }
    finally:
        conn.close()


def disconnect_sync(code: str, pin: str) -> dict:
    auth = connect_sync(code, pin)
    if not auth.get("success"):
        return auth

    conn = get_connection()
    try:
        conn.execute("DELETE FROM portfolio_sync WHERE code = ?", (code,))
        conn.commit()
        return {"success": True}
    finally:
        conn.close()
