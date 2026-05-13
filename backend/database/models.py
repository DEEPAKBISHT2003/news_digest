from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class ArticleBase(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    source: Optional[str] = None
    url: str
    published_at: Optional[datetime] = None
    dominant_category: Optional[str] = None
    image_url: Optional[str] = None
    reading_time: Optional[int] = None
    slug: Optional[str] = None

class ShortResponse(ArticleBase):
    importance_score: int
    trend_score: int

class BlogResponse(ArticleBase):
    content: str

class ArticleDetailResponse(ArticleBase):
    content: str
    structured_data: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    domain_percentages: Dict[str, float] = {}
    importance_score: int
    trend_score: int
    fact_score: int
    confidence_score: float

class TrendingResponse(ArticleBase):
    importance_score: int
    trend_score: int

class DomainMixResponse(BaseModel):
    primary_domain: str
    domain_percentages: Dict[str, float]

class PaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: List[Any]
