"""
Review analyzer — generates sentiment, topics, keywords, and pain points.
Uses lightweight local models (no API calls) so it works offline.
pip install vaderSentiment keybert scikit-learn
"""
import re
from typing import List, Dict, Any

from backend.utils.schema import Review
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Topic keywords for Spotify-specific categorization
TOPIC_KEYWORDS: Dict[str, List[str]] = {
    "music_discovery": ["discover", "new music", "discovery", "find music", "explore", "recommendation"],
    "playlists": ["playlist", "queue", "shuffle", "liked songs", "saved"],
    "recommendations": ["recommend", "suggested", "for you", "daily mix", "discover weekly", "radar"],
    "ui_ux": ["ui", "interface", "design", "layout", "button", "navigation", "app"],
    "audio_quality": ["quality", "sound", "audio", "bitrate", "volume", "normalize"],
    "premium": ["premium", "subscription", "free", "ads", "advertisement", "price", "cost"],
    "offline": ["offline", "download", "cache", "storage"],
    "social": ["friend", "share", "collaborate", "social", "follow", "artist"],
    "bugs": ["bug", "crash", "error", "freeze", "glitch", "broken", "fix"],
    "performance": ["slow", "lag", "battery", "load", "fast", "quick"],
    "podcast": ["podcast", "episode", "show", "talk"],
    "repeat_listening": ["repeat", "same song", "again", "loop", "habit", "keep playing"],
}

PAIN_POINT_PATTERNS = [
    r"(can\'t|cannot|doesn\'t|don\'t|won\'t|fails? to)\s+\w+",
    r"(wish|want|need|missing|lack(ing)?|should have|would be nice)",
    r"(annoying|frustrating|disappointed|hate|dislike|terrible|awful|horrible)",
    r"(used to|before.*?update|since.*?update|after.*?update)",
]

DISCOVERY_ISSUES = [
    "same songs", "same artists", "nothing new", "repetitive", "stuck in bubble",
    "doesn't discover", "no variety", "echo chamber", "filter bubble"
]

RECOMMENDATION_ISSUES = [
    "bad recommendations", "irrelevant", "doesn't know my taste", "wrong genre",
    "off track", "random songs", "unrelated", "missed the mark"
]


def _get_vader():
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        return SentimentIntensityAnalyzer()
    except ImportError:
        logger.warning("[analyzer] vaderSentiment not installed. Using basic sentiment.")
        return None


def analyze_sentiment(text: str) -> tuple:
    """Returns (sentiment_label, sentiment_score)."""
    vader = _get_vader()
    if vader:
        scores = vader.polarity_scores(text)
        compound = scores["compound"]
        if compound >= 0.05:
            return "positive", compound
        elif compound <= -0.05:
            return "negative", compound
        else:
            return "neutral", compound
    # Fallback: keyword-based
    lower = text.lower()
    pos_words = ["great", "love", "amazing", "good", "excellent", "perfect", "best"]
    neg_words = ["bad", "terrible", "awful", "hate", "worst", "broken", "useless"]
    pos_count = sum(1 for w in pos_words if w in lower)
    neg_count = sum(1 for w in neg_words if w in lower)
    if pos_count > neg_count:
        return "positive", 0.5
    elif neg_count > pos_count:
        return "negative", -0.5
    return "neutral", 0.0


def extract_topics(text: str) -> List[str]:
    """Map review text to predefined Spotify topic categories."""
    lower = text.lower()
    found = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            found.append(topic)
    return found or ["general"]


def extract_keywords(text: str) -> List[str]:
    """Extract keywords using simple regex — fast, no model needed."""
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    stopwords = {
        "that", "this", "with", "have", "from", "they", "will", "been", "more",
        "when", "your", "just", "like", "very", "also", "some", "what", "there",
        "their", "which", "about", "would", "into", "than", "then", "them",
    }
    # Frequency count and return top 5
    freq: Dict[str, int] = {}
    for w in words:
        if w not in stopwords:
            freq[w] = freq.get(w, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda x: -x[1])[:5]]


def extract_pain_points(text: str) -> List[str]:
    lower = text.lower()
    pains = []
    for pattern in PAIN_POINT_PATTERNS:
        matches = re.findall(pattern, lower)
        pains.extend([" ".join(m) if isinstance(m, tuple) else m for m in matches])
    return list(set(pains[:5]))


def extract_discovery_issues(text: str) -> List[str]:
    lower = text.lower()
    return [issue for issue in DISCOVERY_ISSUES if issue in lower]


def extract_recommendation_issues(text: str) -> List[str]:
    lower = text.lower()
    return [issue for issue in RECOMMENDATION_ISSUES if issue in lower]


def analyze_reviews(reviews: List[Review]) -> List[Review]:
    """Run full analysis pipeline on all reviews."""
    logger.info(f"[analyzer] Analyzing {len(reviews)} reviews...")
    for review in reviews:
        if not review.review_text:
            continue
        text = review.review_text
        sentiment, score = analyze_sentiment(text)
        review.sentiment = sentiment
        review.sentiment_score = score
        review.topics = extract_topics(text)
        review.keywords = extract_keywords(text)
        review.pain_points = extract_pain_points(text)
        review.music_discovery_issues = extract_discovery_issues(text)
        review.recommendation_issues = extract_recommendation_issues(text)
    logger.info("[analyzer] Analysis complete.")
    return reviews
