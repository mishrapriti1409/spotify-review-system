"""
Reddit connector — reads pre-downloaded JSON files from data/raw/reddit/.

No API credentials needed. Drop any Apify Reddit scraper export into that
folder and it will be picked up automatically on the next ingestion run.

Supported schemas
─────────────────
Apify reddit-scraper (flat list of posts + comments):
  { dataType, title, body, communityName, upVotes, postUrl, createdAt, id, ... }

Comments appear as separate top-level entries with dataType == "comment".
"""
import json
from pathlib import Path
from typing import List

from backend.ingestion.base_connector import BaseConnector
from backend.utils.schema import Review
from backend.utils.text_cleaner import clean_text, is_spam
from backend.utils.config_loader import get_storage_path
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class RedditConnector(BaseConnector):
    source_name = "reddit"

    def fetch(self) -> List[Review]:
        raw_dir = get_storage_path("raw_path") / "reddit"
        raw_dir.mkdir(parents=True, exist_ok=True)

        json_files = sorted(raw_dir.glob("*.json"))
        if not json_files:
            logger.warning(
                "[reddit] No JSON files found in data/raw/reddit/. "
                "Add Apify Reddit scraper exports there to include Reddit data."
            )
            return []

        reviews: List[Review] = []
        seen: set = set()

        for filepath in json_files:
            logger.info(f"[reddit] Reading {filepath.name}")
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if not isinstance(data, list):
                    data = [data]

                for item in data:
                    data_type = item.get("dataType", "post")

                    # ── Build review text ──────────────────────────────────────
                    if data_type == "post":
                        title = item.get("title", "") or ""
                        body  = item.get("body", "") or ""
                        raw   = f"{title}. {body}".strip(". ")
                    else:
                        # comment — body only
                        raw = item.get("body", "") or ""

                    text = clean_text(raw)
                    if not text or is_spam(text):
                        continue

                    # ── Deduplication ──────────────────────────────────────────
                    uid = (
                        item.get("id")
                        or item.get("parsedId")
                        or str(hash(text))
                    )
                    if uid in seen:
                        continue
                    seen.add(uid)

                    # ── Metadata ───────────────────────────────────────────────
                    date_raw = (
                        item.get("createdAt")
                        or item.get("created_at")
                        or item.get("timestamp")
                        or ""
                    )
                    date = date_raw[:10] if date_raw else ""   # keep YYYY-MM-DD

                    community = (
                        item.get("communityName")
                        or item.get("subreddit")
                        or "r/spotify"
                    )
                    url     = item.get("postUrl") or item.get("url") or ""
                    upvotes = item.get("upVotes") or item.get("score") or 0

                    reviews.append(Review(
                        source="reddit",
                        platform="Reddit",
                        review_text=text,
                        date=date,
                        url=url,
                        language="en",
                        metadata={
                            "subreddit":   community,
                            "post_id":     str(uid),
                            "upvotes":     upvotes,
                            "type":        data_type,
                            "flair":       item.get("flair", ""),
                            "source_file": filepath.name,
                        },
                    ))

            except Exception as e:
                logger.error(f"[reddit] Error reading {filepath.name}: {e}", exc_info=True)

        logger.info(f"[reddit] Loaded {len(reviews)} posts/comments from {len(json_files)} file(s).")
        return reviews
