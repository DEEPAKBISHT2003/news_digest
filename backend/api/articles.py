from fastapi import APIRouter, HTTPException
from backend.services.article_service import ArticleService
from backend.database.models import ArticleDetailResponse

router = APIRouter(prefix="/article", tags=["Articles"])

@router.get("/{article_id}", response_model=ArticleDetailResponse)
async def get_article(article_id: int):
    article = await ArticleService.get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
