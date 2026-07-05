"""
Apple App Store connector.
Uses the public iTunes RSS API directly — no third-party library required.
Endpoint: https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/sortBy=mostRecent/json
"""
import time
from typing import List

import requests

from backend.ingestion.base_connector import BaseConnector
from backend.utils.schema import Review
from backend.utils.text_cleaner import clean_text, is_spam
from backend.utils.logger import get_logger

logger = get_logger(__name__)

RSS_URL = "https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/sortBy=mostRecent/json"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; SpotifyResearchBot/1.0)"}


class AppStoreConnector(BaseConnector):
    source_name = "appstore"

    def fetch(self) -> List[Review]:
        cfg = self.config.get("sources", {}).get("appstore", {})
        app_id = cfg.get("app_id", "324684580")
        countries = cfg.get("countries", ["us", "gb", "in", "au", "ca"])
        max_per_country = max(1, cfg.get("max_reviews", 200) // len(countries))
        # iTunes RSS returns up to 500 reviews in pages of 50
        max_pages = min(10, (max_per_country + 49) // 50)

        reviews: List[Review] = []
        seen: set = set()

        for country in countries:
            for page in range(1, max_pages + 1):
                url = (
                    f"https://itunes.apple.com/{country}/rss/customerreviews/"
                    f"page={page}/id={app_id}/sortBy=mostRecent/json"
                )
                try:
                    resp = requests.get(url, headers=HEADERS, timeout=15)
                    if resp.status_code != 200:
                        break
                    data = resp.json()
                    entries = data.get("feed", {}).get("entry", [])
                    if not entries:
                        break

                    # First entry is app metadata, skip it
                    if isinstance(entries[0].get("im:name"), dict):
                        entries = entries[1:]

                    for entry in entries:
                        text = clean_text(entry.get("content", {}).get("label", ""))
                        if not text or is_spam(text):
                            continue
                        uid = f"appstore_{country}_{hash(text)}"
                        if uid in seen:
                            continue
                        seen.add(uid)

                        rating_str = (
                            entry.get("im:rating", {}).get("label", "0")
                            if isinstance(entry.get("im:rating"), dict)
                            else "0"
                        )
                        date_str = entry.get("updated", {}).get("label", "")

                        reviews.append(Review(
                            source="appstore",
                            platform="Apple App Store",
                            review_text=text,
                            rating=float(rating_str) if rating_str.isdigit() else 0.0,
                            date=date_str[:10] if date_str else "",
                            country=country.upper(),
                            language="en",
                            metadata={
                                "title": entry.get("title", {}).get("label", ""),
                                "version": entry.get("im:version", {}).get("label", ""),
                                "country": country,
                                "page": page,
                            }
                        ))

                    if len(reviews) >= max_per_country * len(countries):
                        break
                    time.sleep(0.3)

                except Exception as e:
                    logger.error(f"[appstore] Error fetching {country} page {page}: {e}")
                    break

        logger.info(f"[appstore] Fetched {len(reviews)} reviews from {countries}")
        return reviews
