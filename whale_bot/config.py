"""Central configuration for Whale Bot.

The pipeline turns tagged hydrophone recordings into spectrogram images and
trains an image classifier on them:

    audio + tags  ->  segment by tag  ->  mel-spectrogram  ->  train  ->  predict

Paths are anchored to the repository root so every command works no matter
which directory you run it from.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv is optional; plain env vars still work
    pass

REPO_ROOT = Path(__file__).resolve().parent.parent

# Raw inputs
DATA_DIR = REPO_ROOT / "data"
AUDIO_DIR = DATA_DIR / "audio"            # downloaded/imported recordings (.wav, .flac, .mp3)
ANNOTATIONS_DIR = DATA_DIR / "annotations"  # separate tag files (CSV / Audacity / Raven)

# Derived spectrogram image datasets (torchvision ImageFolder layout)
DATASETS_DIR = REPO_ROOT / "datasets"
SPECTROGRAM_DIR = DATASETS_DIR / "spectrograms"
TRAIN_DIR = SPECTROGRAM_DIR / "train"     # train/<label>/*.png
VAL_DIR = SPECTROGRAM_DIR / "val"         # val/<label>/*.png

# Model checkpoints
MODEL_DIR = REPO_ROOT / "models"
DEFAULT_CHECKPOINT = MODEL_DIR / "whale_classifier.pt"

# --- Audio / spectrogram parameters -------------------------------------------
# These define what "a spectrogram" means across the whole project. Keep them
# consistent between processing (training data) and prediction, or the model
# sees a different distribution at inference time.
SAMPLE_RATE = 22050      # Hz; audio is resampled to this on load
CLIP_SECONDS = 3.0       # length of each spectrogram window
N_FFT = 1024             # FFT window size
HOP_LENGTH = 256         # STFT hop; controls time resolution
N_MELS = 128             # mel frequency bins (spectrogram height)
FMIN = 0                 # lowest mel frequency (Hz)
FMAX = SAMPLE_RATE // 2  # highest mel frequency (Hz); Nyquist by default
