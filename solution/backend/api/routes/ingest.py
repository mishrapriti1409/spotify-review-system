"""Ingestion API routes — including the Retrieve Latest Reviews endpoint."""
import threading
import time
import datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException

from backend.api.models.requests import IngestRequest, IngestResponse
from backend.ingestion.pipeline import run_ingestion
from backend.processing.analyzer import analyze_reviews
from backend.processing.embedder import process_embeddings
from backend.storage.vector_store import upsert_reviews, reset_collection, get_collection_stats
from backend.analytics.generator import generate_analytics
from backend.utils.logger import get_logger

router = APIRouter(prefix="/ingest", tags=["Ingestion"])
logger = get_logger(__name__)

_ingestion_status = {
    "running": False,
    "progress": "",
    "total_ingested": 0,
    "total_indexed": 0,
    "error": None,
    "completed_at": None,
}


@router.post("/", response_model=IngestResponse)
async def trigger_ingestion(req: IngestRequest):
    """
    Start ingestion in a background thread and return immediately.
    Frontend polls /ingest/status to track progress.
    """
    if _ingestion_status["running"]:
        raise HTTPException(status_code=409, detail="Ingestion already in progress.")

    # Fire-and-forget background thread — does NOT block the response
    t = threading.Thread(
        target=_run_full_pipeline_sync,
        args=(req.sources, req.reset),
        daemon=True,
    )
    t.start()

    return IngestResponse(
        status="started",
        total_ingested=0,
        total_indexed=0,
        sources_processed=req.sources or ["all"],
        duration_seconds=0.0,
        message="Ingestion started. Poll /ingest/status for progress.",
    )


@router.get("/status")
async def get_ingestion_status():
    """Poll this every ~2 seconds to track ingestion progress."""
    return _ingestion_status


@router.get("/stats")
async def get_stats():
    """Return current vector store document count."""
    return get_collection_stats()


def _run_full_pipeline_sync(sources: Optional[List[str]], reset: bool):
    """
    Blocking pipeline that runs entirely in a background thread.
    Updates _ingestion_status so the frontend can poll progress.
    """
    global _ingestion_status
    _ingestion_status["running"] = True
    _ingestion_status["error"] = None
    _ingestion_status["total_ingested"] = 0
    _ingestion_status["total_indexed"] = 0
    _ingestion_status["completed_at"] = None
    _ingestion_status["progress"] = "Starting ingestion..."
    start = time.time()

    try:
        # Step 1: Fetch reviews from sources
        _ingestion_status["progress"] = "Fetching reviews from sources..."
        reviews = run_ingestion(sources=sources)
        _ingestion_status["total_ingested"] = len(reviews)
        logger.info(f"[ingest] Fetched {len(reviews)} reviews.")

        if not reviews:
            _ingestion_status["progress"] = "No reviews collected from configured sources."
            return

        # Step 2: Analyze (sentiment, topics, keywords)
        _ingestion_status["progress"] = f"Analyzing {len(reviews)} reviews..."
        reviews = analyze_reviews(reviews)
        logger.info("[ingest] Analysis complete.")

        # Step 3: Generate embeddings (loads model once, batch encodes all)
        _ingestion_status["progress"] = f"Generating embeddings for {len(reviews)} reviews (this takes ~1–2 minutes)..."
        reviews = process_embeddings(reviews)
        logger.info("[ingest] Embeddings complete.")

        # Step 4: Index into ChromaDB
        _ingestion_status["progress"] = "Indexing into vector store..."
        if reset:
            reset_collection()
        total_indexed = upsert_reviews(reviews)
        _ingestion_status["total_indexed"] = total_indexed
        logger.info(f"[ingest] Indexed {total_indexed} documents.")

        # Step 5: Compute analytics
        _ingestion_status["progress"] = "Computing analytics..."
        generate_analytics(reviews)

        duration = round(time.time() - start, 2)
        _ingestion_status["progress"] = (
            f"Complete — {total_indexed} reviews indexed in {duration}s."
        )
        _ingestion_status["completed_at"] = datetime.datetime.utcnow().isoformat()
        logger.info(f"[ingest] Pipeline finished in {duration}s.")

    except Exception as e:
        logger.error(f"[ingest] Pipeline error: {e}", exc_info=True)
        _ingestion_status["error"] = str(e)
        _ingestion_status["progress"] = f"Failed: {str(e)}"
    finally:
        _ingestion_status["running"] = False
