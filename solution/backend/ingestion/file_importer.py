"""
File-based importer — reads pre-downloaded JSON datasets from data/raw/.
Supports the Apify Reddit scraper schema and a generic flat schema.

Drop any JSON file into:
  data/raw/reddit/   — for Reddit Apify exports
  data/raw/custom/   — for any flat [{text, rating, date, ...}] files
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


class RedditFileConnector(BaseConnector):
    """Imports Apify Reddit scraper JSON exports from data/raw/reddit/."""
    source_name = "reddit"

    def fetch(self) -> List[Review]:
        raw_dir = get_storage_path("raw_path") / "reddit"
        json_files = list(raw_dir.glob("*.json"))
        if not json_files:
            logger.warning("[reddit_file] No JSON files found in data/raw/reddit/")
            return []

        reviews: List[Review] = []
        seen: set = set()

        for filepath in json_files:
            logger.info(f"[reddit_file] Reading {filepath.name}")
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if not isinstance(data, list):
                    data = [data]

                for item in data:
                    # Build text from title + body
                    title = item.get("title", "") or ""
                    body = item.get("body", "") or item.get("selftext", "") or ""
                    combined = f"{title}. {body}".strip(". ")
                    text = clean_text(combined)
                    if not text or is_spam(text):
                        continue

                    uid = item.get("id") or item.get("parsedId") or hash(text)
                    if uid in seen:
                        continue
                    seen.add(uid)

                    date = (
                        item.get("createdAt")
                        or item.get("created_at")
                        or item.get("timestamp")
                        or ""
                    )
                    if date:
                        date = date[:10]  # keep YYYY-MM-DD

                    community = (
                        item.get("communityName")
                        or item.get("subreddit")
                        or "r/spotify"
                    )
                    url = item.get("postUrl") or item.get("url") or ""
                    upvotes = item.get("upVotes") or item.get("score") or 0

                    reviews.append(Review(
                        source="reddit",
                        platform="Reddit",
                        review_text=text,
                        date=date,
                        url=url,
                        language="en",
                        metadata={
                            "subreddit": community,
                            "post_id": str(uid),
                            "upvotes": upvotes,
                            "type": item.get("dataType", "post"),
                            "flair": item.get("flair", ""),
                            "source_file": filepath.name,
                        },
                    ))

                    # Also index top-level comments if present
                    for comment in item.get("comments", []):
                        c_text = clean_text(
                            comment.get("body", "")
                            or comment.get("text", "")
                            or ""
                        )
                        if not c_text or is_spam(c_text):
                            continue
                        c_uid = comment.get("id") or hash(c_text)
                        if c_uid in seen:
                            continue
                        seen.add(c_uid)
                        reviews.append(Review(
                            source="reddit",
                            platform="Reddit",
                            review_text=c_text,
                            date=date,
                            url=url,
                            language="en",
                            metadata={
                                "subreddit": community,
                                "post_id": str(uid),
                                "type": "comment",
                                "upvotes": comment.get("upVotes") or comment.get("score") or 0,
                                "source_file": filepath.name,
                            },
                        ))

            except Exception as e:
                logger.error(f"[reddit_file] Error reading {filepath.name}: {e}")

        logger.info(f"[reddit_file] Loaded {len(reviews)} posts/comments from files.")
        return reviews


class CustomFileConnector(BaseConnector):
    """
    Generic importer for any flat JSON array in data/raw/custom/.
    Expected schema per item: {text, rating?, date?, url?, platform?}
    """
    source_name = "custom"

    def fetch(self) -> List[Review]:
        raw_dir = get_storage_path("raw_path") / "custom"
        raw_dir.mkdir(parents=True, exist_ok=True)
        json_files = list(raw_dir.glob("*.json"))
        if not json_files:
            logger.info("[custom_file] No files in data/raw/custom/ — skipping.")
            return []

        reviews: List[Review] = []
        seen: set = set()

        for filepath in json_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    data = [data]

                for item in data:
                    text = clean_text(
                        item.get("text") or item.get("review") or item.get("body") or ""
                    )
                    if not text or is_spam(text):
                        continue
                    uid = hash(text)
                    if uid in seen:
                        continue
                    seen.add(uid)

                    reviews.append(Review(
                        source="custom",
                        platform=item.get("platform", "Custom"),
                        review_text=text,
                        rating=float(item["rating"]) if item.get("rating") else None,
                        date=str(item.get("date", ""))[:10],
                        url=item.get("url", ""),
                        language=item.get("language", "en"),
                        metadata={"source_file": filepath.name},
                    ))
            except Exception as e:
                logger.error(f"[custom_file] Error reading {filepath.name}: {e}")

        logger.info(f"[custom_file] Loaded {len(reviews)} reviews from custom files.")
        return reviews
