"""Training loop for the whale classifier.

Saves the best-validation-accuracy checkpoint to models/whale_classifier.pt.
The checkpoint bundles the class names and architecture alongside the
weights, so prediction never has to guess how the model was built.
"""

import torch
import torch.nn as nn
import torch.optim as optim

from .config import DEFAULT_CHECKPOINT, MODEL_DIR
from .dataset import build_loaders
from .model import build_model


def pick_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def evaluate(model, loader, device):
    """Return (avg_loss, accuracy) over a data loader."""
    criterion = nn.CrossEntropyLoss()
    model.eval()
    total_loss = correct = total = 0
    with torch.no_grad():
        for inputs, labels in loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            total_loss += criterion(outputs, labels).item() * labels.size(0)
            correct += (outputs.argmax(1) == labels).sum().item()
            total += labels.size(0)
    return total_loss / total, correct / total


def train(
    epochs=10,
    batch_size=16,
    lr=1e-3,
    arch="resnet18",
    pretrained=True,
    checkpoint=DEFAULT_CHECKPOINT,
    num_workers=2,
):
    device = pick_device()
    train_loader, val_loader, classes = build_loaders(batch_size, num_workers)
    print(f"device: {device}")
    print(f"classes ({len(classes)}): {classes}")
    print(f"train images: {len(train_loader.dataset)}, "
          f"val images: {len(val_loader.dataset)}")

    model = build_model(arch, num_classes=len(classes), pretrained=pretrained)
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    best_acc = 0.0

    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = seen = 0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            loss = criterion(model(inputs), labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * labels.size(0)
            seen += labels.size(0)

        scheduler.step()
        val_loss, val_acc = evaluate(model, val_loader, device)
        marker = ""
        if val_acc >= best_acc:
            best_acc = val_acc
            torch.save(
                {
                    "model_state": model.state_dict(),
                    "classes": classes,
                    "arch": arch,
                },
                checkpoint,
            )
            marker = "  <- saved"
        print(
            f"epoch {epoch:3d}/{epochs}  "
            f"train_loss {running_loss / seen:.4f}  "
            f"val_loss {val_loss:.4f}  val_acc {val_acc:.1%}{marker}"
        )

    print(f"\nBest val accuracy: {best_acc:.1%}  checkpoint: {checkpoint}")
    return best_acc
