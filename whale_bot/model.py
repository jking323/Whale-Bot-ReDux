"""Model definitions for the whale classifier.

Two options:
  * resnet18 — transfer learning from ImageNet weights. The right choice for
    small scraped datasets (hundreds of images); only the final layer starts
    from scratch.
  * simple — a small CNN trained from scratch. Useful as a baseline or for
    offline environments where pretrained weights can't be downloaded.
"""

import torch.nn as nn
import torch.nn.functional as F
from torchvision import models

IMAGE_SIZE = 224
ARCHITECTURES = ("resnet18", "simple")


class SimpleCNN(nn.Module):
    """Small from-scratch CNN for 224x224 RGB images."""

    def __init__(self, num_classes):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.conv3 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        # 224 -> 112 -> 56 -> 28 after three pools
        self.fc1 = nn.Linear(64 * 28 * 28, 256)
        self.fc2 = nn.Linear(256, num_classes)
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.flatten(1)
        x = self.dropout(F.relu(self.fc1(x)))
        return self.fc2(x)


def build_model(arch, num_classes, pretrained=True):
    """Construct a classifier with `num_classes` outputs."""
    if arch == "resnet18":
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        model = models.resnet18(weights=weights)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        return model
    if arch == "simple":
        return SimpleCNN(num_classes)
    raise ValueError(f"arch must be one of {ARCHITECTURES}, got {arch!r}")
