"""
RAG Retriever — embeds the query, searches ChromaDB, returns top-k relevant reviews.
"""
from typing import List, Dict, Any, Optional

from backend.processing.embedder import embed_query
from backend.storage.vector_store import similarity_search, keyword_search, get_collection_stats
from backend.utils.config_loader import CONFIG
from backend.utils.logger import get_logger

logger = get_logger(__name__)

MIN_SCORE = CONFIG["rag"].get("min_relevance_score", 0.3)
TOP_K = CONFIG["rag"].get("top_k", 10)


def retrieve(
    query: str,
    top_k: int = TOP_K,
    search_mode: str = "semantic",
    filters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant reviews for a query.

    Args:
        query: Natural language question.
        top_k: Number of results to return.
        search_mode: "semantic" | "keyword" | "hybrid"
        filters: Optional ChromaDB metadata filters.

    Returns:
        List of retrieved document dicts with text, metadata, score.
    """
    stats = get_collection_stats()
    if stats["total_documents"] == 0:
        logger.warning("[retriever] Vector store is empty.")
        return []

    if search_mode == "keyword":
        results = keyword_search(query, top_k=top_k)
    elif search_mode == "hybrid":
        results = _hybrid_search(query, top_k=top_k, filters=filters)
    else:  # semantic (default)
        query_vec = embed_query(query)
        results = similarity_search(query_vec, top_k=top_k, where=filters)

    # Filter by minimum relevance score
    results = [r for r in results if r["score"] >= MIN_SCORE]

    logger.info(f"[retriever] Query='{query[:60]}...' → {len(results)} docs retrieved (mode={search_mode})")
    return results


def _hybrid_search(
    query: str,
    top_k: int,
    filters: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Combine semantic and keyword results, deduplicate by id, re-rank by score."""
    semantic_results = similarity_search(embed_query(query), top_k=top_k, where=filters)
    keyword_results = keyword_search(query, top_k=top_k)

    # Merge by id, keep highest score
    merged: Dict[str, Dict] = {}
    for r in semantic_results + keyword_results:
        rid = r["id"]
        if rid not in merged or r["score"] > merged[rid]["score"]:
            merged[rid] = r

    results = sorted(merged.values(), key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def build_context(docs: List[Dict[str, Any]], max_length: int = 4000) -> str:
    """
    Build the context string from retrieved documents to inject into the LLM prompt.
    """
    context_parts = []
    total_chars = 0

    for i, doc in enumerate(docs, 1):
        meta = doc.get("metadata", {})
        platform = meta.get("platform", meta.get("source", "Unknown"))
        rating_val = meta.get("rating", 0)
        rating = f" | Rating: {rating_val}/5" if rating_val else ""
        date = f" | Date: {meta.get('date', '')[:10]}" if meta.get("date") else ""
        sentiment = f" | Sentiment: {meta.get('sentiment', '')}" if meta.get("sentiment") else ""

        snippet = (
            f"[Review {i}] Source: {platform}{rating}{date}{sentiment}\n"
            f"{doc['text']}\n"
        )

        if total_chars + len(snippet) > max_length:
            break

        context_parts.append(snippet)
        total_chars += len(snippet)

    return "\n---\n".join(context_parts)


def assess_confidence(docs: List[Dict[str, Any]]) -> str:
    """Assess retrieval confidence based on number of docs and their scores."""
    if not docs:
        return "Low"
    avg_score = sum(d["score"] for d in docs) / len(docs)
    if len(docs) >= 5 and avg_score >= 0.6:
        return "High"
    elif len(docs) >= 2 and avg_score >= 0.4:
        return "Medium"
    return "Low"
