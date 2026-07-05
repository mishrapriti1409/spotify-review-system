"""
Google Play Store connector.
Uses google-play-scraper library.
pip install google-play-scraper
"""
from typing import List
from datetime import datetime

from backend.ingestion.base_connector import BaseConnector
from backend.utils.schema import Review
from backend.utils.text_cleaner import clean_text, is_spam
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class PlayStoreConnector(BaseConnector):
    source_name = "playstore"

    def fetch(self) -> List[Review]:
        try:
            from google_play_scraper import reviews, Sort
        except ImportError:
            logger.error("google-play-scraper not installed. Run: pip install google-play-scraper")
            return []

        cfg = self.config.get("sources", {}).get("playstore", {})
        app_id = cfg.get("app_id", "com.spotify.music")
        lang = cfg.get("lang", "en")
        country = cfg.get("country", "us")
        max_reviews = cfg.get("max_reviews", 500)

        result_list: List[Review] = []
        seen = set()

        try:
            result, _ = reviews(
                app_id,
                lang=lang,
                country=country,
                sort=Sort.NEWEST,
                count=max_reviews,
            )

            for r in result:
                text = clean_text(r.get("content", ""))
                if not text or is_spam(text):
                    continue
                uid = f"playstore_{r.get('reviewId', hash(text))}"
                if uid in seen:
                    continue
                seen.add(uid)

                date_val = r.get("at")
                date_str = date_val.isoformat() if hasattr(date_val, "isoformat") else str(date_val or "")

                result_list.append(Review(
                    source="playstore",
                    platform="Google Play Store",
                    review_text=text,
                    rating=float(r.get("score", 0)),
                    date=date_str,
                    country=country.upper(),
                    language=lang,
                    metadata={
                        "review_id": r.get("reviewId", ""),
                        "app_version": r.get("appVersion", ""),
                        "device": r.get("device", ""),
                        "thumbs_up": r.get("thumbsUpCount", 0),
                        "reply_content": r.get("replyContent", ""),
                    }
                ))
        except Exception as e:
            logger.error(f"[playstore] Error: {e}")

        logger.info(f"[playstore] Fetched {len(result_list)} reviews")
        return result_list
