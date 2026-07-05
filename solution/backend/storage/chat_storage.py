"""
Local chat history storage — persists conversations as JSON files.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from backend.utils.config_loader import get_storage_path
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def _history_dir() -> Path:
    return get_storage_path("chat_history_path")


def create_conversation() -> str:
    """Create a new conversation and return its ID."""
    conv_id = str(uuid.uuid4())
    conv_file = _history_dir() / f"{conv_id}.json"
    data = {
        "conversation_id": conv_id,
        "created_at": datetime.utcnow().isoformat(),
        "messages": [],
    }
    with open(conv_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return conv_id


def save_message(
    conversation_id: str,
    user_question: str,
    response: str,
    retrieved_docs: List[Dict[str, Any]],
    sources: List[str],
    confidence: str,
) -> None:
    """Append a message turn to an existing conversation."""
    conv_file = _history_dir() / f"{conversation_id}.json"

    if not conv_file.exists():
        # Auto-create if missing
        data = {
            "conversation_id": conversation_id,
            "created_at": datetime.utcnow().isoformat(),
            "messages": [],
        }
    else:
        with open(conv_file, "r", encoding="utf-8") as f:
            data = json.load(f)

    message = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "user_question": user_question,
        "response": response,
        "retrieved_docs": retrieved_docs[:5],  # store first 5 snippets only
        "sources": sources,
        "confidence": confidence,
    }
    data["messages"].append(message)
    data["updated_at"] = datetime.utcnow().isoformat()

    with open(conv_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_conversation(conversation_id: str) -> Optional[Dict[str, Any]]:
    """Load a conversation by ID."""
    conv_file = _history_dir() / f"{conversation_id}.json"
    if not conv_file.exists():
        return None
    with open(conv_file, "r", encoding="utf-8") as f:
        return json.load(f)


def list_conversations() -> List[Dict[str, Any]]:
    """Return metadata for all conversations, newest first."""
    history_dir = _history_dir()
    convs = []
    for f in sorted(history_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            messages = data.get("messages", [])
            first_q = messages[0]["user_question"] if messages else "New conversation"
            convs.append({
                "id": data["conversation_id"],
                "created_at": data.get("created_at", ""),
                "updated_at": data.get("updated_at", data.get("created_at", "")),
                "message_count": len(messages),
                "preview": first_q[:80],
            })
        except Exception:
            pass
    return convs


def delete_conversation(conversation_id: str) -> bool:
    conv_file = _history_dir() / f"{conversation_id}.json"
    if conv_file.exists():
        conv_file.unlink()
        return True
    return False
