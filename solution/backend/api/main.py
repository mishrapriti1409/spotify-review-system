"""
FastAPI application entry point.
Run with: uvicorn backend.api.main:app --reload --port 8000
"""
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routes import chat, ingest, analytics, search
from backend.utils.config_loader import CONFIG
from backend.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Spotify Review Discovery Engine",
    description="RAG-based Customer Intelligence Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=CONFIG["server"]["cors_origins"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round(time.time() - start, 4)
    response.headers["X-Process-Time"] = str(duration)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration}s)")
    return response


# Register routers
app.include_router(chat.router)
app.include_router(ingest.router)
app.include_router(analytics.router)
app.include_router(search.router)


@app.on_event("startup")
async def startup_event():
    """Pre-load the embedding model so the first user query is fast."""
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=1)

    def _warmup():
        from backend.processing.embedder import get_model
        logger.info("[startup] Pre-loading embedding model...")
        get_model()
        logger.info("[startup] Embedding model ready.")

    # Run in background thread — doesn't block server startup
    loop.run_in_executor(executor, _warmup)


@app.get("/")
async def root():
    return {
        "name": "Spotify Review Discovery Engine",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    from backend.storage.vector_store import get_collection_stats
    stats = get_collection_stats()
    return {
        "status": "healthy",
        "vector_store": stats,
    }
