from fastapi import APIRouter, HTTPException
from backend.services.article_service import ArticleService
from backend.database.models import DomainMixResponse

router = APIRouter(prefix="/domain-mix", tags=["Domains"])

@router.get("/{article_id}", response_model=DomainMixResponse)
async def get_domain_mix(article_id: int):
    mix = await ArticleService.get_domain_mix(article_id)
    if not mix:
        raise HTTPException(status_code=404, detail="Article not found")
    return mix
