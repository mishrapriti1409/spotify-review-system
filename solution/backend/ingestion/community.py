"""
Spotify Community connector.
Scrapes community.spotify.com using requests + BeautifulSoup.
pip install requests beautifulsoup4
"""
import time
from typing import List

import requests
from bs4 import BeautifulSoup

from backend.ingestion.base_connector import BaseConnector
from backend.utils.schema import Review
from backend.utils.text_cleaner import clean_text, is_spam
from backend.utils.logger import get_logger

logger = get_logger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


class CommunityConnector(BaseConnector):
    source_name = "community"

    def fetch(self) -> List[Review]:
        cfg = self.config.get("sources", {}).get("community", {})
        if not cfg.get("enabled", False):
            logger.info("[community] Source disabled in config.")
            return []

        base_url = cfg.get("base_url", "https://community.spotify.com")
        max_pages = cfg.get("max_pages", 5)
        reviews: List[Review] = []
        seen = set()

        # Scrape the "Music" and "App" boards
        boards = [
            f"{base_url}/t5/Music/bd-p/music",
            f"{base_url}/t5/Android/bd-p/Android",
            f"{base_url}/t5/iOS/bd-p/iOS",
        ]

        for board_url in boards:
            for page in range(1, max_pages + 1):
                try:
                    url = f"{board_url}?page={page}"
                    resp = requests.get(url, headers=HEADERS, timeout=15)
                    if resp.status_code != 200:
                        break
                    soup = BeautifulSoup(resp.text, "html.parser")

                    # Find discussion threads
                    threads = soup.select("a.page-link.lia-link-navigation.lia-custom-event")
                    if not threads:
                        threads = soup.select("a[href*='/t5/']")

                    for thread in threads:
                        thread_url = thread.get("href", "")
                        if not thread_url.startswith("http"):
                            thread_url = base_url + thread_url
                        if thread_url in seen:
                            continue
                        seen.add(thread_url)

                        # Fetch thread content
                        try:
                            t_resp = requests.get(thread_url, headers=HEADERS, timeout=15)
                            t_soup = BeautifulSoup(t_resp.text, "html.parser")
                            posts = t_soup.select(".lia-message-body-content")
                            for i, p in enumerate(posts):
                                text = clean_text(p.get_text(separator=" "))
                                if not text or is_spam(text):
                                    continue
                                reviews.append(Review(
                                    source="community",
                                    platform="Spotify Community",
                                    review_text=text,
                                    url=thread_url,
                                    language="en",
                                    metadata={
                                        "type": "question" if i == 0 else "reply",
                                        "board": board_url,
                                    }
                                ))
                        except Exception as inner_e:
                            logger.warning(f"[community] Thread fetch error: {inner_e}")

                    time.sleep(1)  # polite delay
                except Exception as e:
                    logger.error(f"[community] Page fetch error: {e}")
                    break

        logger.info(f"[community] Fetched {len(reviews)} posts")
        return reviews
