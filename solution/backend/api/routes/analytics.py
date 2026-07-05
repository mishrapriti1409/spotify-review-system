"""Analytics API routes."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.analytics.generator import load_latest_analytics, generate_analytics
from backend.ingestion.pipeline import load_existing_reviews
from backend.utils.logger import get_logger

router = APIRouter(prefix="/analytics", tags=["Analytics"])
logger = get_logger(__name__)


@router.get("/")
async def get_analytics():
    """Return the latest pre-computed analytics."""
    data = load_latest_analytics()
    if not data:
        raise HTTPException(
            status_code=404,
            detail="No analytics available. Please run ingestion first."
        )
    return data


@router.post("/refresh")
async def refresh_analytics():
    """Recompute analytics from currently processed reviews."""
    reviews = load_existing_reviews()
    if not reviews:
        raise HTTPException(status_code=404, detail="No processed reviews found.")
    analytics = generate_analytics(reviews)
    return analytics


@router.get("/sentiment")
async def get_sentiment(platform: Optional[str] = Query(None)):
    """Sentiment breakdown, optionally filtered by platform."""
    data = load_latest_analytics()
    if not data:
        raise HTTPException(status_code=404, detail="No analytics available.")
    return {"sentiment_distribution": data.get("sentiment_distribution", {})}


@router.get("/topics")
async def get_topics():
    """Topic distribution."""
    data = load_latest_analytics()
    if not data:
        raise HTTPException(status_code=404, detail="No analytics available.")
    return {"topic_distribution": data.get("topic_distribution", {})}


@router.get("/timeline")
async def get_timeline():
    """Review count over time."""
    data = load_latest_analytics()
    if not data:
        raise HTTPException(status_code=404, detail="No analytics available.")
    return {"timeline_trends": data.get("timeline_trends", [])}


@router.get("/keywords")
async def get_keywords():
    """Top keywords for word cloud."""
    data = load_latest_analytics()
    if not data:
        raise HTTPException(status_code=404, detail="No analytics available.")
    return {"keywords": data.get("top_keywords", [])}
