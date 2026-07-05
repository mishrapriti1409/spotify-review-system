"""
Ingestion pipeline orchestrator.

Source map
──────────
appstore   → iTunes RSS API (no key needed)
playstore  → google-play-scraper (no key needed)
reddit     → local JSON files in data/raw/reddit/ (drop Apify exports there)
community  → Spotify Community web scraper (optional)
social     → Twitter/X + YouTube (optional, keys needed)
custom     → any flat JSON files in data/raw/custom/
"""
import json
from typing import List, Optional

from backend.ingestion.appstore import AppStoreConnector
from backend.ingestion.playstore import PlayStoreConnector
from backend.ingestion.reddit import RedditConnector
from backend.ingestion.community import CommunityConnector
from backend.ingestion.social import SocialConnector
from backend.ingestion.file_importer import CustomFileConnector
from backend.utils.config_loader import CONFIG, get_storage_path
from backend.utils.schema import Review
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def run_ingestion(sources: Optional[List[str]] = None) -> List[Review]:
    """
    Run ingestion for all or a subset of sources.

    Args:
        sources: e.g. ["appstore","playstore","reddit"]. None = all enabled.

    Returns:
        Deduplicated list of Review objects ready for embedding.
    """
    ingestion_cfg = CONFIG.get("ingestion", {})
    source_cfgs   = ingestion_cfg.get("sources", {})

    all_reviews: List[Review] = []

    connector_map = [
        ("appstore",  AppStoreConnector),
        ("playstore", PlayStoreConnector),
        ("reddit",    RedditConnector),    # always reads local files
        ("community", CommunityConnector),
        ("social",    SocialConnector),
    ]

    for name, ConnectorClass in connector_map:
        if not _should_run(name, sources, source_cfgs):
            continue
        all_reviews.extend(_safe_run(ConnectorClass, ingestion_cfg, name))

    # Custom file imports (always attempted)
    if sources is None or "custom" in sources:
        all_reviews.extend(_safe_run(CustomFileConnector, ingestion_cfg, "custom"))

    # Global deduplication by text fingerprint
    if ingestion_cfg.get("deduplicate", True):
        seen: set = set()
        deduped: List[Review] = []
        for r in all_reviews:
            key = hash(r.review_text.lower().strip())
            if key not in seen:
                seen.add(key)
                deduped.append(r)
        logger.info(
            f"[pipeline] Deduplication: {len(all_reviews)} → {len(deduped)} reviews"
        )
        all_reviews = deduped

    _save_processed(all_reviews)
    return all_reviews


# ── helpers ────────────────────────────────────────────────────────────────────

def _should_run(
    name: str,
    sources: Optional[List[str]],
    source_cfgs: dict,
) -> bool:
    if sources and name not in sources:
        return False
    # If no explicit source list, respect the "enabled" flag in config
    if not sources and not source_cfgs.get(name, {}).get("enabled", True):
        return False
    return True


def _safe_run(ConnectorClass, ingestion_cfg: dict, name: str) -> List[Review]:
    try:
        connector = ConnectorClass(ingestion_cfg)
        return connector.run()
    except Exception as e:
        logger.error(f"[pipeline] Connector '{name}' failed: {e}", exc_info=True)
        return []


def _save_processed(reviews: List[Review]) -> None:
    processed_dir = get_storage_path("processed_path")
    from datetime import datetime
    filename  = f"merged_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    out_path  = processed_dir / filename
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in reviews], f, indent=2, ensure_ascii=False)
    logger.info(f"[pipeline] Saved {len(reviews)} reviews → {out_path}")


def load_existing_reviews() -> List[Review]:
    """Load the most recently processed reviews from disk."""
    processed_dir = get_storage_path("processed_path")
    files = sorted(processed_dir.glob("merged_*.json"), reverse=True)
    if not files:
        return []
    with open(files[0], "r", encoding="utf-8") as f:
        data = json.load(f)
    reviews = [Review.from_dict(d) for d in data]
    logger.info(f"[pipeline] Loaded {len(reviews)} reviews from {files[0].name}")
    return reviews
