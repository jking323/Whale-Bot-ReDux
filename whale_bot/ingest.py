"""Bring hydrophone recordings into data/audio/.

Data sources (mix and match — the rest of the pipeline treats them the same):

* **local**   — copy/point audio files you already have (your own buoy
                recordings, downloaded datasets) into data/audio/.
* **url**     — download recordings from any direct HTTP(S) link, e.g.
                Orcasound archive clips, NOAA/Watkins exports, or a Kaggle
                file URL.
* **manifest**— a text file of URLs (one per line) to fetch in bulk.

Tags/annotations are handled separately (see annotations.py) — drop them in
data/annotations/. This keeps recordings and labels decoupled, exactly as the
sources provide them.
"""

import shutil
from pathlib import Path
from urllib.parse import urlparse

import requests

from .config import AUDIO_DIR

AUDIO_EXTENSIONS = {".wav", ".flac", ".mp3", ".ogg", ".m4a", ".aif", ".aiff"}
USER_AGENT = "whale-bot-redux hydrophone fetcher"


def _ensure_audio_dir():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def import_local(source, move=False):
    """Copy (or move) local audio files/dirs into data/audio/."""
    _ensure_audio_dir()
    source = Path(source).expanduser()
    if source.is_dir():
        files = [p for p in source.rglob("*") if p.suffix.lower() in AUDIO_EXTENSIONS]
    elif source.is_file():
        files = [source]
    else:
        raise SystemExit(f"No such file or directory: {source}")

    if not files:
        raise SystemExit(f"No audio files ({sorted(AUDIO_EXTENSIONS)}) under {source}")

    for path in files:
        dest = AUDIO_DIR / path.name
        if dest.exists():
            print(f"skip (exists) {dest.name}")
            continue
        (shutil.move if move else shutil.copy2)(str(path), str(dest))
        print(f"imported {dest.name}")
    print(f"\n{len(files)} file(s) processed -> {AUDIO_DIR}")


def _download_one(session, url, timeout=60):
    _ensure_audio_dir()
    name = Path(urlparse(url).path).name or "download"
    if Path(name).suffix.lower() not in AUDIO_EXTENSIONS:
        print(f"skip (not audio) {url}")
        return False
    dest = AUDIO_DIR / name
    if dest.exists():
        print(f"skip (exists) {dest.name}")
        return False
    try:
        with session.get(url, timeout=timeout, stream=True) as r:
            r.raise_for_status()
            with dest.open("wb") as f:
                for chunk in r.iter_content(chunk_size=1 << 16):
                    f.write(chunk)
        print(f"downloaded {dest.name}")
        return True
    except requests.RequestException as exc:
        print(f"FAILED {url}: {exc}")
        if dest.exists():
            dest.unlink()
        return False


def download_urls(urls, timeout=60):
    """Download a list of direct audio URLs into data/audio/."""
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    got = sum(_download_one(session, u.strip(), timeout) for u in urls if u.strip())
    print(f"\n{got} file(s) downloaded -> {AUDIO_DIR}")
    return got


def download_manifest(manifest_path, timeout=60):
    """Download every URL listed (one per line) in a manifest text file."""
    manifest_path = Path(manifest_path).expanduser()
    if not manifest_path.exists():
        raise SystemExit(f"No manifest file at {manifest_path}")
    lines = [
        line for line in manifest_path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    return download_urls(lines, timeout=timeout)
