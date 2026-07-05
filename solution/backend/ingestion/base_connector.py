"""
Base class for all data source connectors.
"""
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from backend.utils.schema import Review
from backend.utils.config_loader import get_storage_path
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class BaseConnector(ABC):
    source_name: str = "base"

    def __init__(self, config: dict):
        self.config = config
        self.raw_dir = get_storage_path("raw_path") / self.source_name
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def fetch(self) -> List[Review]:
        """Fetch raw reviews from the source and return list of Review objects."""
        pass

    def save_raw(self, reviews: List[Review]) -> Path:
        """Persist raw reviews to JSON in data/raw/<source>/."""
        from datetime import datetime
        filename = f"{self.source_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        out_path = self.raw_dir / filename
        data = [r.to_dict() for r in reviews]
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"[{self.source_name}] Saved {len(reviews)} raw reviews → {out_path}")
        return out_path

    def run(self) -> List[Review]:
        """Fetch + save. Returns the reviews."""
        logger.info(f"[{self.source_name}] Starting ingestion...")
        reviews = self.fetch()
        if reviews:
            self.save_raw(reviews)
        logger.info(f"[{self.source_name}] Ingestion complete. {len(reviews)} reviews collected.")
        return reviews
