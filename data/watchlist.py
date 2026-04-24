"""Watchlist 모듈 — 관심 종목 CRUD + 등락률 조회 (SQLite 기반).

사용법:
    from data.watchlist import load_watchlist, add_to_watchlist, get_watchlist_quotes
    wl = load_watchlist()
    add_to_watchlist("NVDA")
    quotes = get_watchlist_quotes(wl)
"""

import logging
from typing import Any

from data.database import get_connection
from data.quote import get_quote

logger = logging.getLogger(__name__)

HIGHLIGHT_THRESHOLD = 5.0  # ±5% 이상이면 highlight


def load_watchlist() -> list[str]:
    """watchlist 테이블에서 티커 목록 로드."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT ticker FROM watchlist ORDER BY added_at"
        ).fetchall()
        return [row["ticker"] for row in rows]
    finally:
        conn.close()


def add_to_watchlist(ticker: str) -> None:
    """종목 추가. 대문자 변환, 중복 무시.

    Raises:
        ValueError: 빈 문자열
    """
    ticker = ticker.strip().upper()
    if not ticker:
        raise ValueError("티커가 비어있습니다.")

    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO watchlist (ticker) VALUES (?)", (ticker,)
        )
        conn.commit()
        logger.info("Watchlist 추가: %s", ticker)
    finally:
        conn.close()


def remove_from_watchlist(ticker: str) -> None:
    """종목 제거.

    Raises:
        KeyError: 존재하지 않는 티커
    """
    ticker = ticker.strip().upper()
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM watchlist WHERE ticker = ?", (ticker,)
        )
        if cursor.rowcount == 0:
            raise KeyError(f"'{ticker}'이(가) Watchlist에 없습니다.")
        conn.commit()
        logger.info("Watchlist 제거: %s", ticker)
    finally:
        conn.close()


def get_watchlist_quotes(watchlist: list[str]) -> list[dict[str, Any]]:
    """각 종목의 현재가 + 등락률 조회.

    Returns:
        [
            {
                "ticker": "NVDA",
                "price": 120.5,
                "change": 2.2,
                "change_percent": 1.86,
                "highlight": False,
                "source": "finnhub"
            },
            ...
        ]
    """
    results = []
    for ticker in watchlist:
        q = get_quote(ticker)
        if q is None:
            results.append({
                "ticker": ticker,
                "price": None,
                "change": None,
                "change_percent": None,
                "highlight": False,
                "source": None,
            })
            continue

        change_pct = q.get("change_percent", 0) or 0
        results.append({
            "ticker": ticker,
            "price": q.get("price"),
            "change": q.get("change"),
            "change_percent": change_pct,
            "highlight": abs(change_pct) >= HIGHLIGHT_THRESHOLD,
            "source": q.get("source"),
        })

    return results


def save_watchlist_to_file(watchlist: list[str]) -> None:
    """하위 호환용 — SQLite에 일괄 저장 (트랜잭션 보장)."""
    conn = get_connection()
    try:
        with conn:
            conn.execute("DELETE FROM watchlist")
            conn.executemany(
                "INSERT INTO watchlist (ticker) VALUES (?)",
                [(t,) for t in watchlist],
            )
    finally:
        conn.close()
