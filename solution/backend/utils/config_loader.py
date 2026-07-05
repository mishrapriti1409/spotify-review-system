"""
Configuration loader.
Priority: Environment variables > configs/config.json
This allows secrets to be injected via Railway/Render env vars
without hardcoding them in the JSON file.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict

# solution/ root is two levels up from this file (backend/utils/config_loader.py)
ROOT = Path(__file__).resolve().parent.parent.parent


def _resolve_path(relative: str) -> Path:
    return ROOT / relative


def load_config() -> Dict[str, Any]:
    config_path = ROOT / "configs" / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # Override with environment variables so cloud deployments don't
    # need the config file to contain secrets.
    groq_key = os.environ.get("GROQ_API_KEY", "")
    if groq_key:
        cfg["groq"]["api_key"] = groq_key

    reddit_id = os.environ.get("REDDIT_CLIENT_ID", "")
    if reddit_id:
        cfg["ingestion"]["sources"]["reddit"]["client_id"] = reddit_id

    reddit_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
    if reddit_secret:
        cfg["ingestion"]["sources"]["reddit"]["client_secret"] = reddit_secret

    twitter_token = os.environ.get("TWITTER_BEARER_TOKEN", "")
    if twitter_token:
        cfg["ingestion"]["sources"]["social"]["twitter_bearer_token"] = twitter_token

    youtube_key = os.environ.get("YOUTUBE_API_KEY", "")
    if youtube_key:
        cfg["ingestion"]["sources"]["social"]["youtube_api_key"] = youtube_key

    # Allow overriding CORS origins for Vercel frontend URL
    frontend_url = os.environ.get("FRONTEND_URL", "")
    if frontend_url:
        origins = cfg["server"]["cors_origins"]
        if frontend_url not in origins:
            origins.append(frontend_url)

    return cfg


def get_storage_path(key: str) -> Path:
    cfg = load_config()
    relative = cfg["storage"].get(key, f"data/{key}")
    # On Railway/Render, data may be mounted at /app/data
    base = os.environ.get("DATA_DIR", "")
    if base:
        folder = relative.split("/")[-1]
        p = Path(base) / folder
    else:
        p = _resolve_path(relative)
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_prompt(name: str) -> str:
    prompt_path = ROOT / "prompts" / name
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def load_fallback_responses() -> Dict[str, str]:
    path = ROOT / "prompts" / "fallback_responses.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# Singleton config loaded once
CONFIG = load_config()
