"""
Analytics generator — computes all dashboard metrics from processed reviews.
Saves results to data/analytics/ as JSON.
"""
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from backend.utils.schema import Review
from backend.utils.config_loader import get_storage_path
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def generate_analytics(reviews: List[Review]) -> Dict[str, Any]:
    """Compute and save all analytics from the given reviews list."""
    if not reviews:
        logger.warning("[analytics] No reviews to analyze.")
        return {}

    analytics = {
        "generated_at": datetime.utcnow().isoformat(),
        "total_reviews": len(reviews),
        "reviews_by_source": _reviews_by_source(reviews),
        "sentiment_distribution": _sentiment_distribution(reviews),
        "rating_distribution": _rating_distribution(reviews),
        "topic_distribution": _topic_distribution(reviews),
        "pain_point_frequency": _pain_point_frequency(reviews),
        "discovery_challenges": _discovery_challenges(reviews),
        "recommendation_complaints": _recommendation_complaints(reviews),
        "feature_requests": _feature_requests(reviews),
        "listening_behaviors": _listening_behaviors(reviews),
        "timeline_trends": _timeline_trends(reviews),
        "top_keywords": _top_keywords(reviews),
        "language_distribution": _language_distribution(reviews),
        "country_distribution": _country_distribution(reviews),
        "avg_rating_by_platform": _avg_rating_by_platform(reviews),
    }

    # Save to disk
    analytics_dir = get_storage_path("analytics_path")
    out_file = analytics_dir / f"analytics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(analytics, f, indent=2, ensure_ascii=False)

    # Also write latest.json for fast frontend access
    latest_file = analytics_dir / "latest.json"
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(analytics, f, indent=2, ensure_ascii=False)

    logger.info(f"[analytics] Saved analytics for {len(reviews)} reviews → {out_file}")
    return analytics


def load_latest_analytics() -> Dict[str, Any]:
    """Load the most recent analytics from disk."""
    analytics_dir = get_storage_path("analytics_path")
    latest = analytics_dir / "latest.json"
    if latest.exists():
        with open(latest, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _reviews_by_source(reviews: List[Review]) -> Dict[str, int]:
    counter = Counter(r.platform for r in reviews)
    return dict(counter.most_common())


def _sentiment_distribution(reviews: List[Review]) -> Dict[str, int]:
    counter = Counter(r.sentiment or "unknown" for r in reviews)
    return {"positive": counter.get("positive", 0), "neutral": counter.get("neutral", 0), "negative": counter.get("negative", 0)}


def _rating_distribution(reviews: List[Review]) -> Dict[str, int]:
    rated = [r for r in reviews if r.rating is not None]
    counter = Counter(int(r.rating) for r in rated)
    return {str(k): v for k, v in sorted(counter.items())}


def _topic_distribution(reviews: List[Review]) -> Dict[str, int]:
    topic_list = []
    for r in reviews:
        topic_list.extend(r.topics)
    counter = Counter(topic_list)
    return dict(counter.most_common(20))


def _pain_point_frequency(reviews: List[Review]) -> Dict[str, int]:
    all_pains = []
    for r in reviews:
        all_pains.extend(r.pain_points)
    counter = Counter(all_pains)
    return dict(counter.most_common(15))


def _discovery_challenges(reviews: List[Review]) -> Dict[str, int]:
    challenges = []
    for r in reviews:
        challenges.extend(r.music_discovery_issues)
    return dict(Counter(challenges).most_common(10))


def _recommendation_complaints(reviews: List[Review]) -> Dict[str, int]:
    complaints = []
    for r in reviews:
        complaints.extend(r.recommendation_issues)
    return dict(Counter(complaints).most_common(10))


def _feature_requests(reviews: List[Review]) -> List[str]:
    """Simple heuristic to identify feature requests."""
    import re
    requests_list = []
    pattern = re.compile(
        r"(wish|want|need|please add|would love|should have|feature request|suggest|add option)",
        re.IGNORECASE,
    )
    for r in reviews:
        if pattern.search(r.review_text):
            # Extract the sentence containing the request
            for sentence in r.review_text.split("."):
                if pattern.search(sentence) and len(sentence.split()) > 4:
                    requests_list.append(sentence.strip()[:120])
    # Deduplicate and return top 20
    seen = set()
    unique = []
    for req in requests_list:
        key = req.lower()[:50]
        if key not in seen:
            seen.add(key)
            unique.append(req)
    return unique[:20]


def _listening_behaviors(reviews: List[Review]) -> Dict[str, int]:
    behaviors = {
        "repeat_listening": 0,
        "playlist_usage": 0,
        "shuffle_mode": 0,
        "offline_listening": 0,
        "podcast_listening": 0,
        "discovery_active": 0,
    }
    for r in reviews:
        text = r.review_text.lower()
        if any(w in text for w in ["repeat", "same song", "loop", "again and again"]):
            behaviors["repeat_listening"] += 1
        if "playlist" in text:
            behaviors["playlist_usage"] += 1
        if "shuffle" in text:
            behaviors["shuffle_mode"] += 1
        if "offline" in text or "download" in text:
            behaviors["offline_listening"] += 1
        if "podcast" in text:
            behaviors["podcast_listening"] += 1
        if any(w in text for w in ["discover", "new music", "explore", "find music"]):
            behaviors["discovery_active"] += 1
    return behaviors


def _timeline_trends(reviews: List[Review]) -> List[Dict[str, Any]]:
    """Group reviews by month for timeline chart."""
    monthly: Dict[str, Dict[str, Any]] = {}
    for r in reviews:
        if not r.date:
            continue
        try:
            month = r.date[:7]  # "YYYY-MM"
            if month not in monthly:
                monthly[month] = {"month": month, "count": 0, "positive": 0, "negative": 0, "neutral": 0}
            monthly[month]["count"] += 1
            sentiment = r.sentiment or "neutral"
            monthly[month][sentiment] = monthly[month].get(sentiment, 0) + 1
        except Exception:
            pass
    return sorted(monthly.values(), key=lambda x: x["month"])


def _top_keywords(reviews: List[Review]) -> List[Dict[str, Any]]:
    all_kw = []
    for r in reviews:
        all_kw.extend(r.keywords)
    counter = Counter(all_kw)
    return [{"text": kw, "value": count} for kw, count in counter.most_common(50)]


def _language_distribution(reviews: List[Review]) -> Dict[str, int]:
    return dict(Counter(r.language or "unknown" for r in reviews).most_common(10))


def _country_distribution(reviews: List[Review]) -> Dict[str, int]:
    return dict(Counter(r.country or "unknown" for r in reviews if r.country).most_common(15))


def _avg_rating_by_platform(reviews: List[Review]) -> Dict[str, float]:
    platform_ratings: Dict[str, List[float]] = {}
    for r in reviews:
        if r.rating is not None and r.platform:
            platform_ratings.setdefault(r.platform, []).append(r.rating)
    return {
        platform: round(sum(ratings) / len(ratings), 2)
        for platform, ratings in platform_ratings.items()
    }
