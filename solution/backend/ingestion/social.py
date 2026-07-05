"""
Social media connector — Twitter/X and YouTube Comments.
pip install tweepy google-api-python-client
"""
import time
from typing import List

from backend.ingestion.base_connector import BaseConnector
from backend.utils.schema import Review
from backend.utils.text_cleaner import clean_text, is_spam
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class SocialConnector(BaseConnector):
    source_name = "social"

    def fetch(self) -> List[Review]:
        cfg = self.config.get("sources", {}).get("social", {})
        if not cfg.get("enabled", False):
            logger.info("[social] Source disabled in config.")
            return []

        reviews: List[Review] = []
        reviews.extend(self._fetch_twitter(cfg))
        reviews.extend(self._fetch_youtube(cfg))
        return reviews

    def _fetch_twitter(self, cfg: dict) -> List[Review]:
        bearer_token = cfg.get("twitter_bearer_token", "")
        if not bearer_token:
            logger.warning("[social/twitter] No bearer token configured.")
            return []

        try:
            import tweepy
        except ImportError:
            logger.error("tweepy not installed. Run: pip install tweepy")
            return []

        reviews: List[Review] = []
        try:
            client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
            queries = [
                "Spotify music discovery -is:retweet lang:en",
                "Spotify recommendations -is:retweet lang:en",
                "Spotify playlist -is:retweet lang:en",
            ]
            max_items = cfg.get("max_items", 100) // len(queries)

            for query in queries:
                resp = client.search_recent_tweets(
                    query=query,
                    max_results=min(max_items, 100),
                    tweet_fields=["created_at", "public_metrics", "lang"],
                )
                if not resp.data:
                    continue
                for tweet in resp.data:
                    text = clean_text(tweet.text)
                    if not text or is_spam(text):
                        continue
                    reviews.append(Review(
                        source="social",
                        platform="Twitter/X",
                        review_text=text,
                        date=tweet.created_at.isoformat() if tweet.created_at else None,
                        url=f"https://twitter.com/i/web/status/{tweet.id}",
                        language="en",
                        metadata={
                            "tweet_id": str(tweet.id),
                            "likes": tweet.public_metrics.get("like_count", 0) if tweet.public_metrics else 0,
                            "retweets": tweet.public_metrics.get("retweet_count", 0) if tweet.public_metrics else 0,
                            "query": query,
                        }
                    ))
                time.sleep(0.5)
        except Exception as e:
            logger.error(f"[social/twitter] Error: {e}")

        return reviews

    def _fetch_youtube(self, cfg: dict) -> List[Review]:
        api_key = cfg.get("youtube_api_key", "")
        if not api_key:
            logger.warning("[social/youtube] No API key configured.")
            return []

        try:
            from googleapiclient.discovery import build
        except ImportError:
            logger.error("google-api-python-client not installed. Run: pip install google-api-python-client")
            return []

        reviews: List[Review] = []
        try:
            youtube = build("youtube", "v3", developerKey=api_key)
            # Search for Spotify-related videos
            search_resp = youtube.search().list(
                q="Spotify music discovery review 2024",
                part="id",
                type="video",
                maxResults=10,
            ).execute()

            for item in search_resp.get("items", []):
                video_id = item["id"]["videoId"]
                try:
                    comments_resp = youtube.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        maxResults=50,
                        textFormat="plainText",
                    ).execute()

                    for c in comments_resp.get("items", []):
                        snippet = c["snippet"]["topLevelComment"]["snippet"]
                        text = clean_text(snippet.get("textDisplay", ""))
                        if not text or is_spam(text):
                            continue
                        reviews.append(Review(
                            source="social",
                            platform="YouTube",
                            review_text=text,
                            date=snippet.get("publishedAt", ""),
                            url=f"https://youtube.com/watch?v={video_id}",
                            language="en",
                            metadata={
                                "video_id": video_id,
                                "likes": snippet.get("likeCount", 0),
                            }
                        ))
                except Exception as e:
                    logger.warning(f"[social/youtube] Comment fetch error for video {video_id}: {e}")

        except Exception as e:
            logger.error(f"[social/youtube] Error: {e}")

        return reviews
