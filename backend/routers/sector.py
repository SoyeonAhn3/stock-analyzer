"""섹터 스크리닝 + 테마 관리 엔드포인트."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.sector_analyzer import run_sector_screening
from data.theme_manager import load_themes, create_theme, delete_theme, get_theme_names

router = APIRouter()


class ThemeCreateRequest(BaseModel):
    name: str
    tickers: list[str]
    preset: str


@router.post("/sector/{name}")
async def sector_screening(name: str):
    """섹터 또는 테마 AI 스크리닝 실행 (2~3분 소요)."""
    result = await run_sector_screening(name)
    if result.get("status") == "failed":
        raise HTTPException(500, result.get("error", "Screening failed"))
    return result


@router.get("/themes")
def themes():
    """테마 목록 조회."""
    return {
        "themes": load_themes(),
        "names": get_theme_names(),
    }


@router.post("/themes")
def theme_create(req: ThemeCreateRequest):
    """새 테마 생성."""
    try:
        create_theme(req.name, req.tickers, req.preset)
        return {"status": "created", "name": req.name}
    except ValueError as e:
        raise HTTPException(422, str(e))


@router.delete("/themes/{name}")
def theme_delete(name: str):
    """테마 삭제."""
    try:
        delete_theme(name)
        return {"status": "deleted", "name": name}
    except KeyError:
        raise HTTPException(404, f"Theme '{name}' not found")
