"""Search API routes — semantic, keyword, hybrid."""
from fastapi import APIRouter, HTTPException

from backend.api.models.requests import SearchRequest
from backend.rag.retriever import retrieve
from backend.utils.logger import get_logger

router = APIRouter(prefix="/search", tags=["Search"])
logger = get_logger(__name__)


@router.post("/")
async def search_reviews(req: SearchRequest):
    """Search reviews with the specified mode."""
    try:
        results = retrieve(
            query=req.query,
            top_k=req.top_k,
            search_mode=req.search_mode,
            filters=req.filters,
        )
        return {
            "query": req.query,
            "mode": req.search_mode,
            "total": len(results),
            "results": results,
        }
    except Exception as e:
        logger.error(f"[search route] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
