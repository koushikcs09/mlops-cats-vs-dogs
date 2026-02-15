"""
Train baseline CNN with MLflow experiment tracking.
Logs params, metrics, confusion matrix, and loss curves.
"""
import argparse
import json
import warnings
from pathlib import Path

# Suppress urllib3 LibreSSL warning on macOS when a dependency uses urllib3 v2
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL", category=UserWarning, module="urllib3")

import mlflow
import mlflow.pytorch
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image

from src.config import (
    DATA_PROCESSED,
    MODELS_DIR,
    IMG_SIZE,
    DEFAULT_EPOCHS,
    DEFAULT_BATCH_SIZE,
    DEFAULT_LEARNING_RATE,
    CLASS_NAMES,
)
from src.data import load_and_resize_image
from src.model import get_model

# Data augmentation for better generalization (PDF requirement)
TRAIN_TRANSFORMS_FULL = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=15),
    transforms.RandomAffine(degrees=0, translate=(0.05, 0.05), scale=(0.95, 1.05)),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
])
# Light augmentation for fast mode (faster, still helps a bit)
TRAIN_TRANSFORMS_FAST = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),
])
# No augmentation for val/test
IDENTITY_TRANSFORM = transforms.Compose([])


class ImagePathDataset(Dataset):
    def __init__(self, items, target_size=(224, 224), transform=None):
        self.items = items  # list of {"path": ..., "label": ...}
        self.target_size = target_size
        self.transform = transform

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        item = self.items[idx]
        img = load_and_resize_image(item["path"], self.target_size)
        if self.transform is not None:
            pil_img = Image.fromarray((img * 255).astype("uint8"))
            pil_img = self.transform(pil_img)
            img = np.array(pil_img, dtype=np.float32) / 255.0
        x = np.transpose(img, (2, 0, 1))
        x = torch.from_numpy(x.astype(np.float32)).float()
        y = torch.tensor(item["label"], dtype=torch.long)
        return x, y


def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss = 0.0
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(loader)


@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    all_preds, all_labels = [], []
    total_loss = 0.0
    criterion = nn.CrossEntropyLoss()
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        logits = model(x)
        loss = criterion(logits, y)
        total_loss += loss.item()
        preds = logits.argmax(dim=1)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(y.cpu().numpy())
    acc = (np.array(all_preds) == np.array(all_labels)).mean()
    return total_loss / len(loader), acc, np.array(all_preds), np.array(all_labels)


def main():
    import sys
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    print("Training starting...", flush=True)

    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DATA_PROCESSED)
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--lr", type=float, default=DEFAULT_LEARNING_RATE)
    parser.add_argument("--out-dir", type=Path, default=MODELS_DIR)
    parser.add_argument("--experiment-name", default="cats_vs_dogs")
    parser.add_argument("--num-workers", type=int, default=4, help="DataLoader workers (0=main thread only)")
    parser.add_argument("--fast", action="store_true", help="Quick run: 2 epochs, subsample data, light augmentation")
    parser.add_argument("--max-train-samples", type=int, default=None, help="Cap training samples (for quick runs)")
    args = parser.parse_args()

    # --fast overrides for speed
    if args.fast:
        args.epochs = 2
        if args.max_train_samples is None:
            args.max_train_samples = 2000
        args.num_workers = 0  # avoid fork overhead when data is small
        train_transform = TRAIN_TRANSFORMS_FAST
        print("Fast mode: 2 epochs, max 2000 train samples, light augmentation", flush=True)
    else:
        train_transform = TRAIN_TRANSFORMS_FULL
        if args.max_train_samples is not None:
            print(f"Limiting to {args.max_train_samples} train samples", flush=True)

    with open(args.data_dir / "splits.json") as f:
        splits = json.load(f)
    train_items = splits["train"]
    val_items = splits["val"]
    if args.max_train_samples is not None and len(train_items) > args.max_train_samples:
        import random
        random.Random(42).shuffle(train_items)
        train_items = train_items[: args.max_train_samples]
    if not train_items:
        raise FileNotFoundError(
            "No training data. Run prepare_data.py first and ensure data/raw has cats/dogs images."
        )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_cuda = device.type == "cuda"
    train_ds = ImagePathDataset(train_items, IMG_SIZE, transform=train_transform)
    val_ds = ImagePathDataset(val_items, IMG_SIZE, transform=IDENTITY_TRANSFORM)
    train_loader = DataLoader(
        train_ds,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=use_cuda,
        persistent_workers=args.num_workers > 0,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=use_cuda,
        persistent_workers=args.num_workers > 0,
    )

    model = get_model(num_classes=2).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=2
    )

    mlflow.set_experiment(args.experiment_name)
    with mlflow.start_run():
        mlflow.log_params({
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "lr": args.lr,
        })
        history = {"train_loss": [], "val_loss": [], "val_acc": []}
        for epoch in range(args.epochs):
            train_loss = train_epoch(model, train_loader, criterion, optimizer, device)
            val_loss, val_acc, val_preds, val_labels = evaluate(
                model, val_loader, device
            )
            scheduler.step(val_loss)
            history["train_loss"].append(train_loss)
            history["val_loss"].append(val_loss)
            history["val_acc"].append(val_acc)
            mlflow.log_metrics(
                {"train_loss": train_loss, "val_loss": val_loss, "val_acc": val_acc},
                step=epoch,
            )
            print(
                f"Epoch {epoch+1}/{args.epochs} train_loss={train_loss:.4f} "
                f"val_loss={val_loss:.4f} val_acc={val_acc:.4f}",
                flush=True,
            )

        # Confusion matrix
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(val_labels, val_preds)
        mlflow.log_dict(
            {"confusion_matrix": cm.tolist(), "labels": CLASS_NAMES},
            "confusion_matrix.json",
        )
        # Log loss curve as artifact
        mlflow.log_dict(history, "history.json")

        args.out_dir.mkdir(parents=True, exist_ok=True)
        model_path = args.out_dir / "model.pt"
        torch.save(model.state_dict(), model_path)
        mlflow.pytorch.log_model(model, "model")
        mlflow.log_artifact(str(model_path))

    print(f"Model saved to {model_path}", flush=True)


if __name__ == "__main__":
    main()
