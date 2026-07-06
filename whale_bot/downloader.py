"""Download images from logged posts into datasets/raw/.

Only direct image links are fetched (i.redd.it, i.imgur.com, or any URL
ending in a known image extension). Files are named <post_id>.<ext> so the
image can always be traced back to its row in data/posts.csv, and existing
files are skipped so re-runs are cheap.
"""

import csv
from urllib.parse import urlparse

import requests

from .config import POSTS_CSV, RAW_IMAGE_DIR

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
IMAGE_HOSTS = {"i.redd.it", "i.imgur.com"}
USER_AGENT = "whale-bot-redux image fetcher"


def image_extension(url):
    """Return the image extension for a direct image URL, else None."""
    parsed = urlparse(url)
    path = parsed.path.lower()
    for ext in IMAGE_EXTENSIONS:
        if path.endswith(ext):
            return ext
    # Some i.redd.it links omit the extension; default to .jpg for known hosts
    if parsed.hostname in IMAGE_HOSTS:
        return ".jpg"
    return None


def download_images(timeout=15):
    """Download every logged image that isn't already on disk.

    Returns (downloaded, skipped, failed) counts.
    """
    if not POSTS_CSV.exists():
        raise SystemExit(f"No post log at {POSTS_CSV} — run `scrape` first.")

    RAW_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    downloaded = skipped = failed = 0
    with POSTS_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ext = image_extension(row["url"])
            if ext is None:
                continue  # not a direct image link (gallery, video, article…)

            dest = RAW_IMAGE_DIR / f"{row['id']}{ext}"
            if dest.exists():
                skipped += 1
                continue

            try:
                response = session.get(row["url"], timeout=timeout)
                response.raise_for_status()
                dest.write_bytes(response.content)
                downloaded += 1
                print(f"downloaded {dest.name}  ({row['title'][:60]})")
            except requests.RequestException as exc:
                failed += 1
                print(f"FAILED {row['url']}: {exc}")

    print(f"\n{downloaded} downloaded, {skipped} already present, "
          f"{failed} failed -> {RAW_IMAGE_DIR}")
    return downloaded, skipped, failed
