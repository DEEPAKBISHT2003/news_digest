from typing import List, Any
from backend.database.models import PaginatedResponse

def paginate(items: List[Any], total_count: int, page: int, limit: int) -> PaginatedResponse:
    return PaginatedResponse(
        total=total_count,
        page=page,
        limit=limit,
        items=items
    )
