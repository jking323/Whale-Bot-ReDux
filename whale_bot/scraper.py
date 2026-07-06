"""Scrape submissions from a subreddit into data/posts.csv.

Replaces the old xlsx logging: CSV is append-friendly, diffable, and easy to
load with pandas later. Posts already in the log are skipped, so the scraper
can be run repeatedly (e.g. on a schedule) to grow the dataset over time.
"""

import csv
from datetime import datetime, timezone

from .config import DATA_DIR, POSTS_CSV, reddit_client

FIELDS = ("id", "title", "url", "subreddit", "created_utc", "scraped_at")

LISTINGS = ("hot", "new", "top")


def load_seen_ids():
    """Return the set of post IDs already recorded in the log."""
    if not POSTS_CSV.exists():
        return set()
    with POSTS_CSV.open(newline="", encoding="utf-8") as f:
        return {row["id"] for row in csv.DictReader(f)}


def scrape(subreddit="whales", limit=50, listing="hot"):
    """Fetch up to `limit` posts and append any new ones to the log.

    Returns the number of new posts recorded.
    """
    if listing not in LISTINGS:
        raise ValueError(f"listing must be one of {LISTINGS}, got {listing!r}")

    reddit = reddit_client()
    seen = load_seen_ids()
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    submissions = getattr(reddit.subreddit(subreddit), listing)(limit=limit)

    new_rows = []
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for submission in submissions:
        if submission.id in seen:
            continue
        new_rows.append(
            {
                "id": submission.id,
                "title": submission.title,
                "url": submission.url,
                "subreddit": str(submission.subreddit),
                "created_utc": int(submission.created_utc),
                "scraped_at": now,
            }
        )

    write_header = not POSTS_CSV.exists()
    with POSTS_CSV.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerows(new_rows)

    print(f"r/{subreddit} ({listing}): {len(new_rows)} new posts logged "
          f"({len(seen)} already known) -> {POSTS_CSV}")
    return len(new_rows)
