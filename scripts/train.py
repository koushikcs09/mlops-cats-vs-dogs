"""
Train baseline CNN with MLflow experiment tracking.
Logs params, metrics, confusion matrix, and loss curves.
"""
import argparse
import json
from pathlib import Path

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
TRAIN_TRANSFORMS = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DATA_PROCESSED)
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--lr", type=float, default=DEFAULT_LEARNING_RATE)
    parser.add_argument("--out-dir", type=Path, default=MODELS_DIR)
    parser.add_argument("--experiment-name", default="cats_vs_dogs")
    args = parser.parse_args()

    with open(args.data_dir / "splits.json") as f:
        splits = json.load(f)
    train_items = splits["train"]
    val_items = splits["val"]
    if not train_items:
        raise FileNotFoundError(
            "No training data. Run prepare_data.py first and ensure data/raw has cats/dogs images."
        )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_ds = ImagePathDataset(train_items, IMG_SIZE, transform=TRAIN_TRANSFORMS)
    val_ds = ImagePathDataset(val_items, IMG_SIZE, transform=IDENTITY_TRANSFORM)
    train_loader = DataLoader(
        train_ds, batch_size=args.batch_size, shuffle=True, num_workers=0
    )
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False)

    model = get_model(num_classes=2).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

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
            history["train_loss"].append(train_loss)
            history["val_loss"].append(val_loss)
            history["val_acc"].append(val_acc)
            mlflow.log_metrics(
                {"train_loss": train_loss, "val_loss": val_loss, "val_acc": val_acc},
                step=epoch,
            )
            print(
                f"Epoch {epoch+1}/{args.epochs} train_loss={train_loss:.4f} "
                f"val_loss={val_loss:.4f} val_acc={val_acc:.4f}"
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

    print(f"Model saved to {model_path}")


if __name__ == "__main__":
    main()
