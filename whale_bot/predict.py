"""Run inference with a trained checkpoint.

Usage (via the CLI):
    python whale_bot.py predict path/to/image.jpg
    python whale_bot.py predict datasets/raw/            # whole folder
"""

from pathlib import Path

import torch
from PIL import Image

from .config import DEFAULT_CHECKPOINT
from .dataset import EVAL_TRANSFORM
from .downloader import IMAGE_EXTENSIONS
from .model import build_model


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


def predict_image(model, classes, image_path, device="cpu", topk=3):
    """Return [(class_name, probability), ...] sorted by confidence."""
    image = Image.open(image_path).convert("RGB")
    batch = EVAL_TRANSFORM(image).unsqueeze(0).to(device)
    with torch.no_grad():
        probs = torch.softmax(model(batch)[0], dim=0)
    topk = min(topk, len(classes))
    values, indices = probs.topk(topk)
    return [(classes[i], v.item()) for v, i in zip(values, indices)]


def predict(target, checkpoint=DEFAULT_CHECKPOINT, topk=3):
    """Predict a single image or every image in a directory."""
    model, classes = load_checkpoint(checkpoint)

    target = Path(target)
    if target.is_dir():
        images = sorted(
            p for p in target.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS
        )
        if not images:
            raise SystemExit(f"No images found in {target}")
    elif target.is_file():
        images = [target]
    else:
        raise SystemExit(f"No such file or directory: {target}")

    for path in images:
        results = predict_image(model, classes, path, topk=topk)
        best_class, best_prob = results[0]
        rest = ", ".join(f"{c} {p:.1%}" for c, p in results[1:])
        line = f"{path.name}: {best_class} ({best_prob:.1%})"
        if rest:
            line += f"  [next: {rest}]"
        print(line)
