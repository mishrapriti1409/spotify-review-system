"""
Embedding generator using sentence-transformers.
Model is loaded once as a module-level singleton and reused for all calls.
"""
from typing import List
import json

from backend.utils.config_loader import CONFIG, get_storage_path
from backend.utils.schema import Review
from backend.utils.logger import get_logger

logger = get_logger(__name__)

_model = None


def get_model():
    """Return the singleton SentenceTransformer model, loading it on first call."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        model_name = CONFIG["embedding"]["model"]
        device = CONFIG["embedding"].get("device", "cpu")
        logger.info(f"[embedder] Loading model '{model_name}' on {device} — one-time load.")
        _model = SentenceTransformer(model_name, device=device)
        logger.info("[embedder] Model loaded and cached.")
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Batch-embed a list of texts. Model is loaded only once."""
    if not texts:
        return []
    model = get_model()
    batch_size = min(CONFIG["ingestion"].get("batch_size", 64), len(texts))
    logger.info(f"[embedder] Encoding {len(texts)} texts (batch_size={batch_size})...")
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,   # suppress noisy per-batch output
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    """Embed a single query string for retrieval."""
    model = get_model()
    vec = model.encode(
        query,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return vec.tolist()


def process_embeddings(reviews: List[Review]) -> List[Review]:
    """
    Add embeddings to all reviews that don't have one yet.
    Runs a single batch encode over all texts — efficient and fast.
    """
    to_embed = [r for r in reviews if r.embedding is None and r.review_text]
    if not to_embed:
        logger.info("[embedder] All reviews already have embeddings — skipping.")
        return reviews

    texts = [r.review_text for r in to_embed]
    logger.info(f"[embedder] Embedding {len(texts)} reviews in one batch...")
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
