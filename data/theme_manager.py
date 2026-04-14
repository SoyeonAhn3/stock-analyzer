"""커스텀 테마 관리 모듈 — SQLite 기반 CRUD.

사용법:
    from data.theme_manager import load_themes, create_theme, delete_theme
    themes = load_themes()
    create_theme("my_picks", ["AAPL", "MSFT", "GOOGL", "AMZN", "META"], "large_stable")
"""

import json
import logging
from typing import Any

from data.database import get_connection

logger = logging.getLogger(__name__)

VALID_PRESETS = ("large_stable", "mid_growth", "early_growth", "dividend")


def load_themes() -> dict[str, Any]:
    """themes 테이블에서 전체 테마 로드. dict[name → {tickers, preset}] 형태."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT name, tickers, preset FROM themes ORDER BY created_at"
        ).fetchall()
        return {
            row["name"]: {
                "tickers": json.loads(row["tickers"]),
                "preset": row["preset"],
            }
            for row in rows
        }
    finally:
        conn.close()


def create_theme(name: str, tickers: list[str], preset: str) -> None:
    """새 테마 생성.

    Args:
        name: 테마 이름
        tickers: 종목 리스트 (최소 5개)
        preset: 프리셋 ("large_stable", "mid_growth", "early_growth", "dividend")

    Raises:
        ValueError: 티커 5개 미만 또는 유효하지 않은 프리셋
    """
    if len(tickers) < 5:
        raise ValueError(f"티커는 최소 5개 필요합니다 (현재 {len(tickers)}개)")
    if preset not in VALID_PRESETS:
        raise ValueError(f"유효하지 않은 프리셋: {preset}. 허용: {VALID_PRESETS}")

    upper_tickers = [t.upper() for t in tickers]
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO themes (name, tickers, preset) VALUES (?, ?, ?)",
            (name, json.dumps(upper_tickers), preset),
        )
        conn.commit()
        logger.info("Theme created: %s (%d tickers, preset=%s)", name, len(tickers), preset)
    finally:
        conn.close()


def delete_theme(name: str) -> None:
    """테마 삭제.

    Raises:
        KeyError: 존재하지 않는 테마
    """
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM themes WHERE name = ?", (name,))
        if cursor.rowcount == 0:
            raise KeyError(f"테마 '{name}'이(가) 존재하지 않습니다.")
        conn.commit()
        logger.info("Theme deleted: %s", name)
    finally:
        conn.close()


def get_theme_names() -> list[str]:
    """등록된 테마 이름 목록."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT name FROM themes ORDER BY created_at"
        ).fetchall()
        return [row["name"] for row in rows]
    finally:
        conn.close()
