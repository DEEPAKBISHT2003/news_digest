from fastapi import APIRouter, Query, HTTPException
from backend.services.article_service import ArticleService
from backend.database.models import PaginatedResponse, ShortResponse
from backend.utils.pagination import paginate

router = APIRouter(prefix="/shorts", tags=["Shorts"])

@router.get("/", response_model=PaginatedResponse)
async def get_shorts(
    domain: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    items, total = await ArticleService.get_articles(
        content_type='short',
        domain=domain,
        page=page,
        limit=limit
    )
    return paginate(items, total, page, limit)
