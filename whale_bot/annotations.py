"""Load tag/annotation files that live *separately* from the audio.

Each annotation marks a labeled time span inside a recording. Three common
formats are supported, auto-detected by extension and header:

1. CSV (recommended) — columns: audio_file, start, end, label
   Times are seconds. `audio_file` is a filename inside data/audio/.

       audio_file,start,end,label
       rec_2024-01-05.wav,12.4,15.1,orca
       rec_2024-01-05.wav,88.0,91.2,humpback

2. Audacity label track (.txt, tab-separated, no header):
       12.400000\t15.100000\torca

3. Raven selection table (.txt, tab-separated, with header containing
   "Begin Time (s)" / "End Time (s)" and an annotation/label column).

Every loader yields uniform Annotation records so the rest of the pipeline
doesn't care which format the tags came in.
"""

import csv
from dataclasses import dataclass
from pathlib import Path

from .config import ANNOTATIONS_DIR


@dataclass
class Annotation:
    audio_file: str  # filename within data/audio/
    start: float     # seconds
    end: float       # seconds
    label: str

    @property
    def duration(self):
        return self.end - self.start


def _load_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = {c.lower().strip(): c for c in (reader.fieldnames or [])}
        required = ("audio_file", "start", "end", "label")
        missing = [c for c in required if c not in cols]
        if missing:
            raise ValueError(
                f"{path.name}: CSV missing columns {missing}. "
                f"Expected header: {','.join(required)}"
            )
        for row in reader:
            yield Annotation(
                audio_file=row[cols["audio_file"]].strip(),
                start=float(row[cols["start"]]),
                end=float(row[cols["end"]]),
                label=row[cols["label"]].strip(),
            )


def _load_raven(path, audio_file):
    """Raven selection table: tab-separated with a header row."""
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        cols = {c.lower().strip(): c for c in (reader.fieldnames or [])}
        begin = cols.get("begin time (s)")
        end = cols.get("end time (s)")
        # Label column varies: "Annotation", "Species", "Tags", "Call"...
        label_col = next(
            (cols[k] for k in ("annotation", "species", "tags", "call", "label")
             if k in cols),
            None,
        )
        if not (begin and end):
            raise ValueError(
                f"{path.name}: not a Raven table (no Begin/End Time columns)"
            )
        for row in reader:
            yield Annotation(
                audio_file=audio_file,
                start=float(row[begin]),
                end=float(row[end]),
                label=(row[label_col].strip() if label_col and row[label_col]
                       else "unknown"),
            )


def _load_audacity(path, audio_file):
    """Audacity label track: `start<TAB>end<TAB>label`, no header."""
    with path.open(encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 3:
                continue
            yield Annotation(
                audio_file=audio_file,
                start=float(parts[0]),
                end=float(parts[1]),
                label=parts[2].strip() or "unknown",
            )


def _sniff_and_load(path):
    """Detect the format of a single annotation file and yield Annotations.

    For Audacity/Raven files (which don't name their audio), the audio file is
    assumed to share the annotation's stem, e.g. rec_01.txt -> rec_01.wav.
    """
    audio_file_guess = path.stem + ".wav"
    if path.suffix.lower() == ".csv":
        yield from _load_csv(path)
        return

    # Peek at the first line to distinguish Raven (has header) from Audacity
    with path.open(encoding="utf-8") as f:
        first = f.readline().lower()
    if "begin time" in first:
        yield from _load_raven(path, audio_file_guess)
    else:
        yield from _load_audacity(path, audio_file_guess)


def load_annotations(annotations_dir=ANNOTATIONS_DIR):
    """Load every annotation file in a directory into one flat list."""
    annotations_dir = Path(annotations_dir)
    if not annotations_dir.exists():
        raise SystemExit(
            f"No annotations directory at {annotations_dir}. Put your tag files "
            "there (CSV / Audacity / Raven) — see whale_bot/annotations.py."
        )

    files = sorted(
        p for p in annotations_dir.iterdir()
        if p.suffix.lower() in (".csv", ".txt")
    )
    if not files:
        raise SystemExit(f"No .csv/.txt annotation files found in {annotations_dir}")

    records = []
    for path in files:
        records.extend(_sniff_and_load(path))
    return records
