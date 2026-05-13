from fastapi import APIRouter, Query
from backend.services.article_service import ArticleService
from backend.database.models import PaginatedResponse
from backend.utils.pagination import paginate

router = APIRouter(prefix="/blogs", tags=["Blogs"])

@router.get("/", response_model=PaginatedResponse)
async def get_blogs(
    domain: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50)
):
    items, total = await ArticleService.get_articles(
        content_type='blog',
        domain=domain,
        page=page,
        limit=limit
    )
    return paginate(items, total, page, limit)
