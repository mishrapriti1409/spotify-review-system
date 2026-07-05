"""
Unified Review Schema — every review from every source maps to this structure.
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime


@dataclass
class Review:
    doc_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: str = ""           # e.g. "appstore", "playstore", "reddit"
    platform: str = ""         # human-readable: "Apple App Store"
    review_text: str = ""
    rating: Optional[float] = None
    date: Optional[str] = None
    url: Optional[str] = None
    language: str = "en"
    country: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # AI-generated fields (populated during processing)
    sentiment: Optional[str] = None        # "positive" | "negative" | "neutral"
    sentiment_score: Optional[float] = None
    topics: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    pain_points: List[str] = field(default_factory=list)
    listening_intent: Optional[str] = None
    recommendation_issues: List[str] = field(default_factory=list)
    music_discovery_issues: List[str] = field(default_factory=list)
    user_goals: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None

    ingested_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("embedding", None)  # don't serialize large vectors to JSON
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Review":
        d.pop("embedding", None)
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
