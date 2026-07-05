"""
Chat engine — orchestrates the full RAG pipeline for each user question.
"""
from typing import List, Dict, Any, Optional

from backend.rag.retriever import retrieve, build_context, assess_confidence
from backend.rag.generator import generate_response
from backend.storage.chat_storage import save_message, load_conversation
from backend.storage.vector_store import get_collection_stats
from backend.utils.config_loader import load_fallback_responses
from backend.utils.logger import get_logger

logger = get_logger(__name__)
FALLBACKS = load_fallback_responses()


def chat(
    question: str,
    conversation_id: str,
    search_mode: str = "semantic",
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Full RAG pipeline for a single user turn.

    Returns:
        {
            "answer": str,
            "sources": list,
            "confidence": str,
            "retrieved_count": int,
            "retrieved_docs": list (snippets),
            "conversation_id": str,
        }
    """
    # 1. Check knowledge base is populated
    stats = get_collection_stats()
    if stats["total_documents"] == 0:
        return _fallback_response(FALLBACKS["empty_knowledge_base"], conversation_id, question)

    # 2. Retrieve relevant documents
    docs = retrieve(question, search_mode=search_mode, filters=filters)

    if not docs:
        return _fallback_response(FALLBACKS["no_relevant_reviews"], conversation_id, question)

    # 3. Assess confidence
    confidence = assess_confidence(docs)
    if confidence == "Low" and len(docs) < 2:
        return _fallback_response(FALLBACKS["low_retrieval_confidence"], conversation_id, question)

    # 4. Build context
    context = build_context(docs, max_length=CONFIG_MAX_CONTEXT)

    # 5. Load conversation history for follow-up support
    conv = load_conversation(conversation_id)
    history = []
    if conv:
        for msg in conv.get("messages", [])[-4:]:
            history.append({
                "user": msg.get("user_question", ""),
                "assistant": msg.get("response", ""),
            })

    # 6. Generate grounded response
    answer = generate_response(question, context, conversation_history=history)

    # 7. Extract sources
    sources = list(set(
        d["metadata"].get("platform", d["metadata"].get("source", "Unknown"))
        for d in docs
    ))

    # 8. Persist to chat history
    save_message(
        conversation_id=conversation_id,
        user_question=question,
        response=answer,
        retrieved_docs=[{"text": d["text"][:200], "score": d["score"], "metadata": d["metadata"]} for d in docs[:5]],
        sources=sources,
        confidence=confidence,
    )

    logger.info(f"[chat_engine] Q='{question[:60]}' | Docs={len(docs)} | Confidence={confidence}")

    return {
        "answer": answer,
        "sources": sources,
        "confidence": confidence,
        "retrieved_count": len(docs),
        "retrieved_docs": [
            {
                "text": d["text"][:300],
                "score": d["score"],
                "platform": d["metadata"].get("platform", ""),
                "rating": d["metadata"].get("rating", ""),
                "date": d["metadata"].get("date", "")[:10],
                "sentiment": d["metadata"].get("sentiment", ""),
            }
            for d in docs[:6]
        ],
        "conversation_id": conversation_id,
    }


def _fallback_response(message: str, conversation_id: str, question: str) -> Dict[str, Any]:
    save_message(
        conversation_id=conversation_id,
        user_question=question,
        response=message,
        retrieved_docs=[],
        sources=[],
        confidence="Low",
    )
    return {
        "answer": message,
        "sources": [],
        "confidence": "Low",
        "retrieved_count": 0,
        "retrieved_docs": [],
        "conversation_id": conversation_id,
    }


# Load at module level to avoid repeated config reads
from backend.utils.config_loader import CONFIG
CONFIG_MAX_CONTEXT = CONFIG["rag"].get("max_context_length", 4000)
