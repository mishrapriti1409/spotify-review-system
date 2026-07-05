"""
ChromaDB vector store — persistent local mode.
Compatible with chromadb >=0.5 and >=1.0.
Stores documents in solution/data/vector_store/.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb

from backend.utils.config_loader import CONFIG, get_storage_path
from backend.utils.schema import Review
from backend.utils.logger import get_logger

logger = get_logger(__name__)

_client: Optional[chromadb.PersistentClient] = None
_collection = None


def _get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        vs_path = str(get_storage_path("vector_store"))
        logger.info(f"[vector_store] Initializing ChromaDB at {vs_path}")
        # chromadb >=1.0 removed the Settings import — PersistentClient(path=...) is the only API
        _client = chromadb.PersistentClient(path=vs_path)
    return _client


def get_collection():
    global _collection
    if _collection is None:
        client = _get_client()
        collection_name = CONFIG["vector_store"]["collection_name"]
        metric = CONFIG["vector_store"].get("distance_metric", "cosine")
        _collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": metric},
        )
        logger.info(
            f"[vector_store] Collection '{collection_name}' ready. "
            f"Count: {_collection.count()}"
        )
    return _collection


def upsert_reviews(reviews: List[Review]) -> int:
    """
    Upsert reviews with embeddings into ChromaDB.
    Returns number of documents upserted.
    """
    collection = get_collection()
    to_add = [r for r in reviews if r.embedding is not None and r.review_text]

    if not to_add:
        logger.warning("[vector_store] No reviews with embeddings to upsert.")
        return 0

    ids = [r.doc_id for r in to_add]
    embeddings = [r.embedding for r in to_add]
    documents = [r.review_text for r in to_add]
    metadatas = [_build_metadata(r) for r in to_add]

    batch_size = 500
    total = 0
    for i in range(0, len(to_add), batch_size):
        collection.upsert(
            ids=ids[i:i + batch_size],
            embeddings=embeddings[i:i + batch_size],
            documents=documents[i:i + batch_size],
            metadatas=metadatas[i:i + batch_size],
        )
        total += len(ids[i:i + batch_size])

    logger.info(f"[vector_store] Upserted {total} documents.")
    return total


def _build_metadata(r: Review) -> Dict[str, Any]:
    """Build ChromaDB-safe metadata dict — only str/int/float/bool values allowed."""
    return {
        "source": r.source or "",
        "platform": r.platform or "",
        "rating": float(r.rating) if r.rating is not None else 0.0,
        "date": r.date or "",
        "language": r.language or "en",
        "country": r.country or "",
        "sentiment": r.sentiment or "neutral",
        "sentiment_score": float(r.sentiment_score) if r.sentiment_score is not None else 0.0,
        "topics": json.dumps(r.topics),
        "keywords": json.dumps(r.keywords),
        "url": r.url or "",
    }


def similarity_search(
    query_embedding: List[float],
    top_k: int = 10,
    where: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve top-k most similar documents to the query embedding.
    Returns list of dicts: {id, text, metadata, score}.
    """
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return []

    kwargs: Dict[str, Any] = {
        "query_embeddings": [query_embedding],
        "n_results": min(top_k, count),
        "include": ["documents", "metadatas", "distances"],
    }
    if where:
        kwargs["where"] = where

    results = collection.query(**kwargs)

    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    output = []
    for doc_id, doc, meta, dist in zip(ids, docs, metas, distances):
        # cosine distance → similarity score
        score = 1.0 - float(dist)
        output.append({
            "id": doc_id,
            "text": doc,
            "metadata": meta,
            "score": round(score, 4),
        })

    return output


def keyword_search(keyword: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """Keyword search using ChromaDB's built-in text query."""
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return []

    results = collection.query(
        query_texts=[keyword],
        n_results=min(top_k, count),
        include=["documents", "metadatas", "distances"],
    )

    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    return [
        {
            "id": doc_id,
            "text": doc,
            "metadata": meta,
            "score": round(1.0 - float(dist), 4),
        }
        for doc_id, doc, meta, dist in zip(ids, docs, metas, distances)
    ]


def get_collection_stats() -> Dict[str, Any]:
    collection = get_collection()
    return {
        "total_documents": collection.count(),
        "collection_name": CONFIG["vector_store"]["collection_name"],
        "path": str(get_storage_path("vector_store")),
    }


def reset_collection():
    """Delete and recreate the collection (used when re-ingesting from scratch)."""
    global _collection
    client = _get_client()
    collection_name = CONFIG["vector_store"]["collection_name"]
    try:
        client.delete_collection(collection_name)
        logger.warning(f"[vector_store] Collection '{collection_name}' deleted.")
    except Exception:
        pass
    _collection = None
    get_collection()  # recreate
