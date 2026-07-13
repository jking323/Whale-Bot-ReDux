"""Run inference on audio with a trained checkpoint.

An audio file is converted to spectrogram windows using the exact same
parameters as training (config.py), each window is classified, and the
per-window probabilities are averaged into a single prediction for the clip.

    python whale_bot.py predict path/to/recording.wav
    python whale_bot.py predict data/audio/            # every recording in a folder
"""

from pathlib import Path

import numpy as np
import torch

from .config import DEFAULT_CHECKPOINT
from .dataset import EVAL_TRANSFORM
from .ingest import AUDIO_EXTENSIONS
from .model import build_model
from .spectrogram import audio_to_images


def load_checkpoint(checkpoint=DEFAULT_CHECKPOINT, device="cpu"):
    """Return (model, class_names) restored from a training checkpoint."""
    checkpoint = Path(checkpoint)
    if not checkpoint.exists():
        raise SystemExit(f"No checkpoint at {checkpoint} — run `train` first.")

    state = torch.load(checkpoint, map_location=device, weights_only=True)
    model = build_model(state["arch"], num_classes=len(state["classes"]),
                        pretrained=False)
    model.load_state_dict(state["model_state"])
    model.to(device).eval()
    return model, state["classes"]


def predict_audio(model, classes, audio_path, device="cpu", topk=3):
    """Classify one recording; returns (results, n_windows).

    results is [(class_name, mean_probability), ...] sorted by confidence,
    averaged over every spectrogram window in the recording.
    """
    images = audio_to_images(audio_path)
    if not images:
        return [], 0

    batch = torch.stack([EVAL_TRANSFORM(img) for img in images]).to(device)
    with torch.no_grad():
        probs = torch.softmax(model(batch), dim=1)  # (n_windows, n_classes)
    mean_probs = probs.mean(dim=0)

    topk = min(topk, len(classes))
    values, indices = mean_probs.topk(topk)
    results = [(classes[i], v.item()) for v, i in zip(values, indices)]
    return results, len(images)


def predict(target, checkpoint=DEFAULT_CHECKPOINT, topk=3):
    """Predict a single recording or every recording in a directory."""
    model, classes = load_checkpoint(checkpoint)

    target = Path(target)
    if target.is_dir():
        clips = sorted(
            p for p in target.iterdir() if p.suffix.lower() in AUDIO_EXTENSIONS
        )
        if not clips:
            raise SystemExit(f"No audio files found in {target}")
    elif target.is_file():
        clips = [target]
    else:
        raise SystemExit(f"No such file or directory: {target}")

    for path in clips:
        results, n_windows = predict_audio(model, classes, path, topk=topk)
        if not results:
            print(f"{path.name}: (empty / unreadable audio)")
            continue
        best_class, best_prob = results[0]
        rest = ", ".join(f"{c} {p:.1%}" for c, p in results[1:])
        line = f"{path.name}: {best_class} ({best_prob:.1%}, {n_windows} windows)"
        if rest:
            line += f"  [next: {rest}]"
        print(line)
