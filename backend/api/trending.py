from fastapi import APIRouter, Query
from backend.services.article_service import ArticleService
from backend.database.models import TrendingResponse
from typing import List

router = APIRouter(prefix="/trending", tags=["Trending"])

@router.get("/", response_model=List[TrendingResponse])
async def get_trending(limit: int = Query(10, ge=1, le=50)):
    return await ArticleService.get_trending(limit)
