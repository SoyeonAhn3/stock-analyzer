"""AI 분석 결과 캐시 — 당일 동일 종목 재분석 시 즉시 반환.

사용법:
    from data.analysis_cache import get_cached_analysis, save_analysis
    cached = get_cached_analysis("NVDA")
    if cached:
        return cached
    # ... 새로 분석 ...
    save_analysis("NVDA", result_dict)
"""

import json
import logging
from datetime import datetime, timedelta

from data.database import get_connection

logger = logging.getLogger(__name__)

CACHE_TTL_HOURS = 24


def get_cached_analysis(ticker: str) -> dict | None:
    """캐시된 분석 결과 조회. 만료되었으면 None."""
    ticker = ticker.upper()
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT result, expires_at FROM analysis_cache WHERE ticker = ?",
            (ticker,),
        ).fetchone()
        if not row:
            return None

        expires_at = datetime.fromisoformat(row["expires_at"])
        if datetime.now() > expires_at:
            conn.execute("DELETE FROM analysis_cache WHERE ticker = ?", (ticker,))
            conn.commit()
            logger.info("Cache expired for %s", ticker)
            return None

        logger.info("Cache hit for %s", ticker)
        return json.loads(row["result"])
    finally:
        conn.close()


def save_analysis(ticker: str, result: dict) -> None:
    """분석 결과를 캐시에 저장."""
    ticker = ticker.upper()
    now = datetime.now()
    expires_at = now + timedelta(hours=CACHE_TTL_HOURS)

    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO analysis_cache (ticker, result, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (ticker, json.dumps(result, ensure_ascii=False), now.isoformat(), expires_at.isoformat()),
        )
        conn.commit()
        logger.info("Cached analysis for %s (expires %s)", ticker, expires_at.isoformat())
    finally:
        conn.close()


def clear_expired() -> int:
    """만료된 캐시 항목 정리. 삭제 건수 반환."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM analysis_cache WHERE expires_at < ?",
            (datetime.now().isoformat(),),
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()
