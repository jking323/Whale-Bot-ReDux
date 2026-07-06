"""Central configuration for Whale Bot.

Paths are anchored to the repository root so every command works no matter
which directory you run it from. Reddit credentials come from environment
variables (or a local .env file) — never commit them to the repo.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv is optional; plain env vars still work
    pass

REPO_ROOT = Path(__file__).resolve().parent.parent

# Scraped post metadata
DATA_DIR = REPO_ROOT / "data"
POSTS_CSV = DATA_DIR / "posts.csv"

# Image datasets
DATASETS_DIR = REPO_ROOT / "datasets"
RAW_IMAGE_DIR = DATASETS_DIR / "raw"      # unlabeled downloads land here
TRAIN_DIR = DATASETS_DIR / "train"        # train/<class_name>/*.jpg
VAL_DIR = DATASETS_DIR / "val"            # val/<class_name>/*.jpg

# Model checkpoints
MODEL_DIR = REPO_ROOT / "models"
DEFAULT_CHECKPOINT = MODEL_DIR / "whale_classifier.pt"


def reddit_client():
    """Build an authenticated (read-only) PRAW client from the environment.

    Required environment variables:
        REDDIT_CLIENT_ID
        REDDIT_CLIENT_SECRET
    Optional:
        REDDIT_USER_AGENT
    """
    import praw

    missing = [
        key
        for key in ("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET")
        if not os.getenv(key)
    ]
    if missing:
        raise SystemExit(
            "Missing Reddit credentials: "
            + ", ".join(missing)
            + "\nCopy .env.example to .env and fill in your values, or export"
            " them as environment variables. Create an app at"
            " https://www.reddit.com/prefs/apps (script type)."
        )

    return praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent=os.getenv("REDDIT_USER_AGENT", "whale-bot-redux (by u/unknown)"),
    )
