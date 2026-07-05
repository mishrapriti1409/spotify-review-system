"""
Embedding generator using ChromaDB's built-in ONNX embedding function.
Uses the same all-MiniLM-L6-v2 model but via onnxruntime (~80 MB RAM)
instead of PyTorch + sentence-transformers (~500 MB RAM).
This keeps the deployed backend well within a 512 MB memory limit.
"""
from typing import List
import json

from backend.utils.config_loader import CONFIG, get_storage_path
from backend.utils.schema import Review
from backend.utils.logger import get_logger

logger = get_logger(__name__)

_ef = None  # ChromaDB ONNX embedding function singleton


def get_embedding_function():
    """
    Return the singleton ChromaDB ONNX embedding function.
    Loaded lazily on first call — avoids any memory hit at import time.
    """
    global _ef
    if _ef is None:
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
        logger.info("[embedder] Loading ONNX embedding function (all-MiniLM-L6-v2)...")
        _ef = ONNXMiniLM_L6_V2()
        logger.info("[embedder] ONNX embedding function ready.")
    return _ef

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Batch-embed a list of texts using the ONNX function."""
    if not texts:
        return []
      ef = get_embedding_function()
    logger.info(f"[embedder] Encoding {len(texts)} texts via ONNX...")
    # ONNXMiniLM_L6_V2 is callable and returns EmbeddingResult (list of lists)
    embeddings = ef(texts)
    return [list(e) for e in embeddings]


def embed_query(query: str) -> List[float]:
    """Embed a single query string for retrieval."""
   results = embed_texts([query])
    return results[0] if results else []


def process_embeddings(reviews: List[Review]) -> List[Review]:
    """
    Add embeddings to all reviews that don't have one yet.
    Runs a single batch encode — efficient and memory-safe.
    """
    to_embed = [r for r in reviews if r.embedding is None and r.review_text]
    if not to_embed:
        logger.info("[embedder] All reviews already have embeddings — skipping.")
        return reviews

    texts = [r.review_text for r in to_embed]
    logger.info(f"[embedder] Embedding {len(texts)} reviews...")
    vectors = embed_texts(texts)

    for review, vector in zip(to_embed, vectors):
        review.embedding = vector

    # Persist embedding vectors to disk
    emb_dir = get_storage_path("embeddings_path")
    from datetime import datetime
    out_path = emb_dir / f"embeddings_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    emb_data = [{"doc_id": r.doc_id, "embedding": r.embedding} for r in to_embed]
    with open(out_path, "w") as f:
        json.dump(emb_data, f)
    logger.info(f"[embedder] Embeddings saved → {out_path}")

    return reviews
