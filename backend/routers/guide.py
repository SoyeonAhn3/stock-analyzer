"""가이드 콘텐츠 엔드포인트."""

from fastapi import APIRouter, HTTPException

from data.guide_content import get_categories, get_topics, get_topic_detail

router = APIRouter()


@router.get("/guide/categories")
def categories():
    """가이드 카테고리 목록."""
    return {"categories": get_categories()}


@router.get("/guide/{category}")
def topics(category: str):
    """카테고리별 주제 목록."""
    result = get_topics(category)
    if not result:
        raise HTTPException(404, f"Category '{category}' not found")
    return {"category": category, "topics": result}


@router.get("/guide/{category}/{index}")
def topic_detail(category: str, index: int):
    """주제 상세 내용."""
    result = get_topic_detail(category, index)
    if result is None:
        raise HTTPException(404, f"Topic not found: {category}[{index}]")
    return result
