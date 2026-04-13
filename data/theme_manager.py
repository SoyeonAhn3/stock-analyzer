"""커스텀 테마 관리 모듈 - themes.json CRUD.

사용법:
    from data.theme_manager import load_themes, create_theme, delete_theme
    themes = load_themes()
    create_theme("my_picks", ["AAPL", "MSFT", "GOOGL", "AMZN", "META"], "large_stable")
"""

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

THEMES_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "themes.json")

VALID_PRESETS = ("large_stable", "mid_growth", "early_growth", "dividend")

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


def load_themes() -> dict[str, Any]:
    """themes.json 로드. 파일 없으면 기본 테마로 자동 생성."""
    try:
        with open(THEMES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.info("themes.json not found or invalid, creating defaults")
        _save(DEFAULT_THEMES)
        return DEFAULT_THEMES.copy()


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

    themes = load_themes()
    themes[name] = {
        "tickers": [t.upper() for t in tickers],
        "preset": preset,
    }
    _save(themes)
    logger.info("Theme created: %s (%d tickers, preset=%s)", name, len(tickers), preset)


def delete_theme(name: str) -> None:
    """테마 삭제.

    Raises:
        KeyError: 존재하지 않는 테마
    """
    themes = load_themes()
    if name not in themes:
        raise KeyError(f"테마 '{name}'이(가) 존재하지 않습니다.")
    del themes[name]
    _save(themes)
    logger.info("Theme deleted: %s", name)


def get_theme_names() -> list[str]:
    """등록된 테마 이름 목록."""
    return list(load_themes().keys())


def _save(data: dict) -> None:
    """themes.json에 저장."""
    os.makedirs(os.path.dirname(THEMES_PATH), exist_ok=True)
    with open(THEMES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
