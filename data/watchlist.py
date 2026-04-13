"""Watchlist 모듈 — 관심 종목 CRUD + 등락률 조회.

사용법:
    from data.watchlist import load_watchlist, add_to_watchlist, get_watchlist_quotes
    wl = load_watchlist()
    add_to_watchlist("NVDA")
    quotes = get_watchlist_quotes(wl)
"""

import json
import logging
import os
from typing import Any, Optional

from data.quote import get_quote

logger = logging.getLogger(__name__)

WATCHLIST_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "watchlist.json")

HIGHLIGHT_THRESHOLD = 5.0  # ±5% 이상이면 highlight


def load_watchlist() -> list[str]:
    """watchlist.json 로드. 파일 없으면 빈 리스트."""
    try:
        with open(WATCHLIST_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def add_to_watchlist(ticker: str) -> None:
    """종목 추가. 대문자 변환, 중복 무시.

    Raises:
        ValueError: 빈 문자열
    """
    ticker = ticker.strip().upper()
    if not ticker:
        raise ValueError("티커가 비어있습니다.")

    wl = load_watchlist()
    if ticker in wl:
        logger.info("이미 Watchlist에 존재: %s", ticker)
        return
    wl.append(ticker)
    _save(wl)
    logger.info("Watchlist 추가: %s", ticker)


def remove_from_watchlist(ticker: str) -> None:
    """종목 제거.

    Raises:
        KeyError: 존재하지 않는 티커
    """
    ticker = ticker.strip().upper()
    wl = load_watchlist()
    if ticker not in wl:
        raise KeyError(f"'{ticker}'이(가) Watchlist에 없습니다.")
    wl.remove(ticker)
    _save(wl)
    logger.info("Watchlist 제거: %s", ticker)


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
    """Watchlist를 JSON 파일로 저장."""
    _save(watchlist)


def _save(data: list) -> None:
    """watchlist.json에 저장."""
    os.makedirs(os.path.dirname(WATCHLIST_PATH), exist_ok=True)
    with open(WATCHLIST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
