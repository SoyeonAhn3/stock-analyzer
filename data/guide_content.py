"""Beginner's Guide 콘텐츠 모듈 — JSON 파일 기반.

콘텐츠는 config/guide/*.json에 저장.
이 모듈은 JSON을 읽어서 반환하는 로더 역할만 한다.

사용법:
    from data.guide_content import get_categories, get_topics, get_topic_detail
    cats = get_categories()           # ["chart_basics", ...]
    topics = get_topics("chart_basics")  # [{title, level, ...}, ...]
    detail = get_topic_detail("chart_basics", 0)

콘텐츠 추가/수정:
    config/guide/ 폴더의 JSON 파일을 편집하면 됨.
    Python 코드 수정 불필요.
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# JSON 파일 디렉토리
_GUIDE_DIR = Path(__file__).resolve().parent.parent / "config" / "guide"

# 메모리 캐시 (서버 시작 시 1회 로드)
_cache: dict[str, dict[str, Any]] | None = None


def _load_all() -> dict[str, dict[str, Any]]:
    """config/guide/*.json 전체 로드. 서버 시작 후 1회만 실행."""
    global _cache
    if _cache is not None:
        return _cache

    _cache = {}
    if not _GUIDE_DIR.exists():
        logger.warning("Guide directory not found: %s", _GUIDE_DIR)
        return _cache

    for json_file in sorted(_GUIDE_DIR.glob("*.json")):
        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)
            _cache[json_file.stem] = data
        except Exception as e:
            logger.warning("Failed to load %s: %s", json_file.name, e)

    logger.info("Loaded %d guide categories from %s", len(_cache), _GUIDE_DIR)
    return _cache


def reload() -> None:
    """캐시 초기화 — JSON 수정 후 서버 재시작 없이 반영할 때 사용."""
    global _cache
    _cache = None
    _load_all()


def get_categories() -> list[str]:
    """카테고리 키 목록 반환."""
    return list(_load_all().keys())


def get_category_info(category: str) -> Optional[dict[str, Any]]:
    """카테고리 전체 정보 반환."""
    return _load_all().get(category)


def get_topics(category: str) -> list[dict[str, Any]]:
    """특정 카테고리의 주제 리스트 반환. 없으면 빈 리스트."""
    cat = _load_all().get(category)
    if cat is None:
        return []
    return cat.get("topics", [])


def get_topic_detail(category: str, index: int) -> Optional[dict[str, Any]]:
    """특정 주제의 상세 정보 반환.

    Args:
        category: 카테고리 키
        index: 주제 인덱스 (0부터)

    Returns:
        {title, level, what, how, when, example} 또는 None
    """
    topics = get_topics(category)
    if 0 <= index < len(topics):
        return topics[index]
    return None
