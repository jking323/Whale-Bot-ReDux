"""Turn tagged audio into mel-spectrogram images for training.

For each annotation (a labeled time span in a recording), the audio is sliced,
resampled, and converted to a log-mel spectrogram saved as a PNG under
datasets/spectrograms/<split>/<label>/. Spans longer than CLIP_SECONDS are cut
into consecutive windows; shorter ones are padded, so every image has the same
dimensions and the classifier sees a fixed input.

Spectrogram parameters live in config.py and MUST match between processing and
prediction — spectrogram.audio_to_images() is the single source of truth used
by both paths.
"""

import hashlib

import numpy as np

from .config import (
    AUDIO_DIR,
    CLIP_SECONDS,
    FMAX,
    FMIN,
    HOP_LENGTH,
    N_FFT,
    N_MELS,
    SAMPLE_RATE,
    TRAIN_DIR,
    VAL_DIR,
)

CLIP_SAMPLES = int(CLIP_SECONDS * SAMPLE_RATE)


def _mel_to_uint8(mel_db):
    """Scale a log-mel array to a 0-255 image, low freq at the bottom."""
    # Normalize to [0, 1] using a fixed dB floor so brightness is comparable
    # across clips (per-clip min/max would erase loudness information).
    clipped = np.clip(mel_db, -80.0, 0.0)
    normed = (clipped + 80.0) / 80.0
    img = (normed * 255.0).astype(np.uint8)
    return np.flipud(img)  # so low frequencies render at the image bottom


def _waveform_to_mel_db(y):
    import librosa

    mel = librosa.feature.melspectrogram(
        y=y,
        sr=SAMPLE_RATE,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        n_mels=N_MELS,
        fmin=FMIN,
        fmax=FMAX,
        power=2.0,
    )
    return librosa.power_to_db(mel, ref=np.max)


def waveform_to_images(y):
    """Split a waveform into fixed windows and return a list of PIL images."""
    from PIL import Image

    images = []
    if len(y) == 0:
        return images

    # Chop into consecutive CLIP_SAMPLES windows; pad the final short one.
    n_windows = max(1, int(np.ceil(len(y) / CLIP_SAMPLES)))
    for w in range(n_windows):
        chunk = y[w * CLIP_SAMPLES : (w + 1) * CLIP_SAMPLES]
        if len(chunk) < CLIP_SAMPLES:
            chunk = np.pad(chunk, (0, CLIP_SAMPLES - len(chunk)))
        mel_db = _waveform_to_mel_db(chunk)
        images.append(Image.fromarray(_mel_to_uint8(mel_db)).convert("RGB"))
    return images


def audio_to_images(path, start=None, end=None):
    """Load (a span of) an audio file and return spectrogram window images."""
    import librosa

    offset = start or 0.0
    duration = (end - offset) if end is not None else None
    y, _ = librosa.load(
        path, sr=SAMPLE_RATE, mono=True, offset=offset, duration=duration
    )
    return waveform_to_images(y)


def _short_hash(*parts):
    return hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()[:8]


def process(val_fraction=0.2, audio_dir=AUDIO_DIR):
    """Build the spectrogram image dataset from audio + annotations.

    Each annotation is deterministically assigned to train or val based on a
    hash of (audio_file, start), so re-running is stable and the same segment
    never lands in both splits. Returns a per-label count summary.
    """
    from collections import Counter

    from .annotations import load_annotations

    annotations = load_annotations()
    if not audio_dir.exists():
        raise SystemExit(f"No audio directory at {audio_dir} — run `ingest` first.")

    counts = Counter()
    missing_audio = set()

    for ann in annotations:
        audio_path = audio_dir / ann.audio_file
        if not audio_path.exists():
            missing_audio.add(ann.audio_file)
            continue

        # Deterministic split: hash bucket -> val if below the fraction cutoff
        bucket = int(_short_hash(ann.audio_file, ann.start), 16) % 1000
        split_dir = VAL_DIR if bucket < val_fraction * 1000 else TRAIN_DIR
        out_dir = split_dir / ann.label
        out_dir.mkdir(parents=True, exist_ok=True)

        try:
            images = audio_to_images(audio_path, ann.start, ann.end)
        except Exception as exc:  # librosa/soundfile decode errors
            print(f"FAILED {ann.audio_file} [{ann.start}-{ann.end}]: {exc}")
            continue

        stem = _short_hash(ann.audio_file, ann.start, ann.end)
        for i, img in enumerate(images):
            img.save(out_dir / f"{ann.label}_{stem}_{i:02d}.png")
            counts[(split_dir.name, ann.label)] += 1

    print("Spectrograms written to", TRAIN_DIR.parent)
    for (split, label), n in sorted(counts.items()):
        print(f"  {split:5s}  {label:20s} {n}")
    if missing_audio:
        print(f"\nWARNING: {len(missing_audio)} referenced audio file(s) not found "
              f"in {audio_dir}:")
        for name in sorted(missing_audio):
            print(f"  {name}")
    if not counts:
        raise SystemExit("No spectrograms were produced — check audio/annotations.")
    return counts
