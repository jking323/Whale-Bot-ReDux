"""Training loop for the whale classifier.

Saves the best-validation-accuracy checkpoint to models/whale_classifier.pt.
The checkpoint bundles the class names and architecture alongside the
weights, so prediction never has to guess how the model was built.

Runs on CPU, CUDA GPU, Apple MPS, or a Cloud/Colab **TPU** via PyTorch/XLA —
the device is auto-detected. On a TPU the loaders are wrapped so host->device
transfer overlaps compute, and `xm.optimizer_step` drives the XLA execution.
"""

import torch
import torch.nn as nn
import torch.optim as optim

from .config import DEFAULT_CHECKPOINT, MODEL_DIR
from .dataset import build_loaders
from .model import build_model


def _try_import_xla():
    """Return torch_xla's xla_model module if available, else None."""
    try:
        import torch_xla.core.xla_model as xm

        return xm
    except ImportError:
        return None


def pick_device():
    """Prefer TPU (XLA) -> CUDA -> MPS -> CPU."""
    xm = _try_import_xla()
    if xm is not None:
        try:
            return xm.xla_device()
        except Exception:
            pass  # torch_xla installed but no TPU attached
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def _wrap_loader(loader, device, is_xla):
    """On XLA, wrap a DataLoader so batches stream onto the TPU efficiently."""
    if not is_xla:
        return loader
    import torch_xla.distributed.parallel_loader as pl

    return pl.MpDeviceLoader(loader, device)


def evaluate(model, loader, device):
    """Return (avg_loss, accuracy) over a data loader.

    Metrics accumulate on-device and sync once at the end, which keeps XLA
    from stalling on a host round-trip every batch.
    """
    criterion = nn.CrossEntropyLoss()
    model.eval()
    total_loss = torch.zeros((), device=device)
    correct = torch.zeros((), device=device)
    total = 0
    with torch.no_grad():
        for inputs, labels in loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            total_loss += criterion(outputs, labels) * labels.size(0)
            correct += (outputs.argmax(1) == labels).sum()
            total += labels.size(0)
    return total_loss.item() / total, correct.item() / total


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
    is_xla = device.type == "xla"
    xm = _try_import_xla() if is_xla else None

    train_loader, val_loader, classes = build_loaders(batch_size, num_workers)
    print(f"device: {device}{'  (TPU/XLA)' if is_xla else ''}")
    print(f"classes ({len(classes)}): {classes}")
    print(f"train images: {len(train_loader.dataset)}, "
          f"val images: {len(val_loader.dataset)}")

    model = build_model(arch, num_classes=len(classes), pretrained=pretrained)
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    train_device_loader = _wrap_loader(train_loader, device, is_xla)
    val_device_loader = _wrap_loader(val_loader, device, is_xla)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    best_acc = 0.0

    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = torch.zeros((), device=device)
        seen = 0
        for inputs, labels in train_device_loader:
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            loss = criterion(model(inputs), labels)
            loss.backward()
            if is_xla:
                xm.optimizer_step(optimizer)  # steps + XLA barrier
            else:
                optimizer.step()

            running_loss += loss.detach() * labels.size(0)
            seen += labels.size(0)

        scheduler.step()
        val_loss, val_acc = evaluate(model, val_device_loader, device)
        marker = ""
        if val_acc >= best_acc:
            best_acc = val_acc
            payload = {
                "model_state": model.state_dict(),
                "classes": classes,
                "arch": arch,
            }
            # xm.save moves tensors off the TPU to CPU before writing
            (xm.save if is_xla else torch.save)(payload, str(checkpoint))
            marker = "  <- saved"
        print(
            f"epoch {epoch:3d}/{epochs}  "
            f"train_loss {running_loss.item() / seen:.4f}  "
            f"val_loss {val_loss:.4f}  val_acc {val_acc:.1%}{marker}"
        )

    print(f"\nBest val accuracy: {best_acc:.1%}  checkpoint: {checkpoint}")
    return best_acc
