"""
RAG Generator — builds the prompt from retrieved context and calls Groq LLM.
pip install groq
"""
from typing import List, Dict, Any

from groq import Groq

from backend.utils.config_loader import CONFIG, load_prompt, load_fallback_responses
from backend.utils.logger import get_logger

logger = get_logger(__name__)

_groq_client = None


def _get_groq():
    global _groq_client
    if _groq_client is None:
        api_key = CONFIG["groq"]["api_key"]
        if not api_key:
            raise ValueError("Groq API key not set. Add it to configs/config.json → groq.api_key")
        _groq_client = Groq(api_key=api_key)
    return _groq_client


def generate_response(
    question: str,
    context: str,
    conversation_history: List[Dict[str, str]] = None,
) -> str:
    """
    Generate a grounded answer using Groq LLM.
    Never calls LLM without context — if context is empty, returns fallback.
    """
    fallbacks = load_fallback_responses()

    if not context or not context.strip():
        return fallbacks["no_relevant_reviews"]

    system_prompt = load_prompt("rag_system_prompt.txt").replace("{context}", context)

    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history for follow-up context (last 4 turns)
    if conversation_history:
        for turn in conversation_history[-4:]:
            messages.append({"role": "user", "content": turn.get("user", "")})
            messages.append({"role": "assistant", "content": turn.get("assistant", "")})

    messages.append({"role": "user", "content": question})

    try:
        groq = _get_groq()
        model = CONFIG["groq"]["model"]
        response = groq.chat.completions.create(
            model=model,
            messages=messages,
            temperature=CONFIG["groq"]["temperature"],
            max_tokens=CONFIG["groq"]["max_tokens"],
        )
        answer = response.choices[0].message.content
        logger.info(f"[generator] Response generated. Model={model}, Tokens={response.usage.total_tokens}")
        return answer

    except Exception as e:
        logger.error(f"[generator] Groq API error: {e}")
        # Try fallback model
        for fallback_model in CONFIG["groq"].get("fallback_models", []):
            try:
                groq = _get_groq()
                response = groq.chat.completions.create(
                    model=fallback_model,
                    messages=messages,
                    temperature=CONFIG["groq"]["temperature"],
                    max_tokens=CONFIG["groq"]["max_tokens"],
                )
                return response.choices[0].message.content
            except Exception as fe:
                logger.error(f"[generator] Fallback model {fallback_model} failed: {fe}")

        return "I'm currently unable to generate a response. Please try again later."
