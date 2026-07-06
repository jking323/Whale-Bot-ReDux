"""Data loading for training and validation.

Expects the standard torchvision ImageFolder layout:

    datasets/train/<class_name>/*.jpg
    datasets/val/<class_name>/*.jpg

Class names are taken from the directory names (e.g. humpback, orca,
not_a_whale), so adding a new species is just adding a new folder.
"""

import torch
from torchvision import datasets, transforms

from .config import TRAIN_DIR, VAL_DIR
from .model import IMAGE_SIZE

# ImageNet normalization — required for pretrained backbones, harmless otherwise
NORMALIZE = transforms.Normalize(
    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
)

TRAIN_TRANSFORM = transforms.Compose(
    [
        transforms.RandomResizedCrop(IMAGE_SIZE, scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        NORMALIZE,
    ]
)

EVAL_TRANSFORM = transforms.Compose(
    [
        transforms.Resize(256),
        transforms.CenterCrop(IMAGE_SIZE),
        transforms.ToTensor(),
        NORMALIZE,
    ]
)


def _check_layout(path, split):
    classes = [p for p in path.iterdir() if p.is_dir()] if path.exists() else []
    if not classes:
        raise SystemExit(
            f"No {split} data found at {path}.\n"
            "Expected layout: datasets/"
            f"{split}/<class_name>/*.jpg — sort images from datasets/raw/"
            " into class folders first (see README)."
        )


def build_loaders(batch_size=16, num_workers=2):
    """Return (train_loader, val_loader, class_names)."""
    _check_layout(TRAIN_DIR, "train")
    _check_layout(VAL_DIR, "val")

    train_ds = datasets.ImageFolder(TRAIN_DIR, transform=TRAIN_TRANSFORM)
    val_ds = datasets.ImageFolder(VAL_DIR, transform=EVAL_TRANSFORM)

    if train_ds.classes != val_ds.classes:
        raise SystemExit(
            "train and val must contain the same class folders:\n"
            f"  train: {train_ds.classes}\n  val:   {val_ds.classes}"
        )

    train_loader = torch.utils.data.DataLoader(
        train_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers
    )
    val_loader = torch.utils.data.DataLoader(
        val_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers
    )
    return train_loader, val_loader, train_ds.classes
