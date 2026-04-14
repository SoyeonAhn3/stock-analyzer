"""SQLite 데이터베이스 관리 — 연결, 테이블 초기화, JSON 마이그레이션.

사용법:
    from data.database import get_connection, init_db
    init_db()  # 앱 시작 시 1회
    conn = get_connection()
"""

import json
import logging
import os
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "app.db"

# 기존 JSON 파일 경로 (마이그레이션용)
_CONFIG_DIR = Path(__file__).parent.parent / "config"
_WATCHLIST_JSON = _CONFIG_DIR / "watchlist.json"
_THEMES_JSON = _CONFIG_DIR / "themes.json"

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS watchlist (
    ticker TEXT PRIMARY KEY,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS themes (
    name TEXT PRIMARY KEY,
    tickers TEXT NOT NULL,
    preset TEXT NOT NULL,
    is_default INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analysis_cache (
    ticker TEXT PRIMARY KEY,
    result TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS price_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    target_price REAL NOT NULL,
    direction TEXT NOT NULL CHECK(direction IN ('above', 'below')),
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    triggered_at TIMESTAMP
);
"""

DEFAULT_THEMES = {
    "AI_semiconductor": {
        "tickers": ["NVDA", "AMD", "AVGO", "TSM", "MRVL", "INTC", "QCOM"],
        "preset": "large_stable",
    },
    "defense": {
        "tickers": ["LMT", "RTX", "NOC", "GD", "BA", "LHX", "HII"],
        "preset": "large_stable",
    },
    "clean_energy": {
        "tickers": ["ENPH", "SEDG", "FSLR", "NEE", "PLUG", "RUN"],
        "preset": "mid_growth",
    },
    "cybersecurity": {
        "tickers": ["CRWD", "PANW", "FTNT", "ZS", "OKTA"],
        "preset": "mid_growth",
    },
    "space": {
        "tickers": ["RKLB", "ASTS", "LUNR", "BA", "LMT"],
        "preset": "early_growth",
    },
}


def get_connection() -> sqlite3.Connection:
    """SQLite 연결 반환. WAL 모드 활성화."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    """테이블 생성 + 기존 JSON 데이터 마이그레이션."""
    conn = get_connection()
    try:
        conn.executescript(CREATE_TABLES_SQL)
        _migrate_watchlist(conn)
        _migrate_themes(conn)
        conn.commit()
        logger.info("Database initialized: %s", DB_PATH)
    finally:
        conn.close()


def _migrate_watchlist(conn: sqlite3.Connection) -> None:
    """config/watchlist.json → watchlist 테이블 마이그레이션."""
    count = conn.execute("SELECT COUNT(*) FROM watchlist").fetchone()[0]
    if count > 0:
        return  # 이미 데이터 있으면 스킵

    if not _WATCHLIST_JSON.exists():
        return

    try:
        with open(_WATCHLIST_JSON, "r", encoding="utf-8") as f:
            tickers = json.load(f)
        if isinstance(tickers, list) and tickers:
            conn.executemany(
                "INSERT OR IGNORE INTO watchlist (ticker) VALUES (?)",
                [(t,) for t in tickers],
            )
            logger.info("Migrated %d watchlist tickers from JSON", len(tickers))
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Watchlist migration failed: %s", e)


def _migrate_themes(conn: sqlite3.Connection) -> None:
    """config/themes.json → themes 테이블 마이그레이션."""
    count = conn.execute("SELECT COUNT(*) FROM themes").fetchone()[0]
    if count > 0:
        return  # 이미 데이터 있으면 스킵

    themes = {}

    # JSON 파일에서 읽기 시도
    if _THEMES_JSON.exists():
        try:
            with open(_THEMES_JSON, "r", encoding="utf-8") as f:
                themes = json.load(f)
            logger.info("Migrating %d themes from JSON", len(themes))
        except (json.JSONDecodeError, OSError):
            pass

    # JSON이 없거나 비어있으면 기본 테마 사용
    if not themes:
        themes = DEFAULT_THEMES

    for name, data in themes.items():
        is_default = 1 if name in DEFAULT_THEMES else 0
        conn.execute(
            "INSERT OR IGNORE INTO themes (name, tickers, preset, is_default) VALUES (?, ?, ?, ?)",
            (name, json.dumps(data["tickers"]), data["preset"], is_default),
        )
