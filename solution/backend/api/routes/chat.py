"""Chat API routes."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, HTTPException

from backend.api.models.requests import ChatRequest, ChatResponse
from backend.rag.chat_engine import chat
from backend.storage.chat_storage import (
    create_conversation, list_conversations,
    load_conversation, delete_conversation,
)
from backend.utils.logger import get_logger

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = get_logger(__name__)

# Shared executor for blocking RAG calls (embedding + LLM)
_executor = ThreadPoolExecutor(max_workers=4)


@router.post("/", response_model=ChatResponse)
async def send_message(req: ChatRequest):
    """Send a message to the RAG chatbot."""
    conversation_id = req.conversation_id or create_conversation()
    try:
        # Run blocking RAG pipeline in thread pool — keeps event loop free
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _executor,
            lambda: chat(
                question=req.question,
                conversation_id=conversation_id,
                search_mode=req.search_mode,
                filters=req.filters,
            )
        )
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"[chat route] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations")
async def get_conversations():
    return {"conversations": list_conversations()}


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    conv = load_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.delete("/conversations/{conversation_id}")
async def remove_conversation(conversation_id: str):
    success = delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted", "conversation_id": conversation_id}


@router.post("/new")
async def new_conversation():
    conv_id = create_conversation()
    return {"conversation_id": conv_id}
