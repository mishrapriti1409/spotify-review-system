"""Pydantic request/response models for the API."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    conversation_id: Optional[str] = None
    search_mode: str = Field(default="semantic", pattern="^(semantic|keyword|hybrid)$")
    filters: Optional[Dict[str, Any]] = None


class IngestRequest(BaseModel):
    sources: Optional[List[str]] = None  # None = all enabled sources
    reset: bool = False  # If True, wipe vector store before re-indexing


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=10, ge=1, le=50)
    search_mode: str = Field(default="semantic", pattern="^(semantic|keyword|hybrid)$")
    filters: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: str
    retrieved_count: int
    retrieved_docs: List[Dict[str, Any]]
    conversation_id: str


class IngestResponse(BaseModel):
    status: str
    total_ingested: int
    total_indexed: int
    sources_processed: List[str]
    duration_seconds: float
    message: str


class AnalyticsResponse(BaseModel):
    data: Dict[str, Any]
    generated_at: str
    total_reviews: int
