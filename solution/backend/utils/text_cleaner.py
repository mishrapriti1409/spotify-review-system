"""
Text cleaning utilities used before indexing reviews.
"""
import re
import unicodedata
from typing import Optional


def clean_text(text: Optional[str]) -> str:
    """Full cleaning pipeline for a single review text."""
    if not text or not text.strip():
        return ""

    # Decode HTML entities
    text = _remove_html(text)
    # Remove URLs
    text = _remove_urls(text)
    # Remove emojis / non-ASCII that cause issues (keep accented chars)
    text = _normalize_unicode(text)
    # Collapse whitespace
    text = _normalize_whitespace(text)
    # Minimum length check
    if len(text.split()) < 3:
        return ""
    return text


def _remove_html(text: str) -> str:
    import html
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    return text


def _remove_urls(text: str) -> str:
    text = re.sub(r"http\S+|www\.\S+", "", text)
    return text


def _normalize_unicode(text: str) -> str:
    # Normalize to NFC form
    return unicodedata.normalize("NFC", text)


def _normalize_whitespace(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def is_spam(text: str) -> bool:
    """Heuristic spam detection."""
    if not text:
        return True
    lower = text.lower()
    spam_patterns = [
        r"^[\W\d]+$",          # only symbols/numbers
        r"(.)\1{5,}",           # repeated characters
        r"(buy now|click here|free money|promo code)",
    ]
    for pattern in spam_patterns:
        if re.search(pattern, lower):
            return True
    return False
