"""Data preprocessing: load, resize to 224x224 RGB, split, and augment."""
import os
from pathlib import Path
from typing import Tuple, Union

import numpy as np
from PIL import Image


def load_and_resize_image(
    image_path: Union[str, Path],
    target_size: Tuple[int, int] = (224, 224),
) -> np.ndarray:
    """
    Load an image from path and resize to target_size as RGB.
    Returns numpy array of shape (H, W, 3) with values in [0, 1].
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    img = Image.open(path)
    img = img.convert("RGB")
    img = img.resize(target_size, Image.Resampling.BILINEAR)
    arr = np.array(img, dtype=np.float32) / 255.0
    return arr


# Class folder names to try (label 0=cat, 1=dog). Handles Kaggle variants.
_CAT_NAMES = ("cats", "cat", "Cats", "Cat", "CAT")
_DOG_NAMES = ("dogs", "dog", "Dogs", "Dog", "DOG")


def _collect_class_images(data_dir: Path, class_folders: tuple, label: int) -> list:
    """Collect (path, label) for one class, trying multiple folder names and layouts."""
    data_dir = Path(data_dir)
    out = []
    for class_name in class_folders:
        for sub in ["train", "Train", "training_set", "training_set/training_set", "valid", "test", "PetImages", ""]:
            if sub:
                d = data_dir / sub / class_name
            else:
                d = data_dir / class_name
            if not d.exists():
                continue
            for ext in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"):
                for p in d.glob(ext):
                    out.append((str(p), label))
            if out:
                return out
    return out


def get_train_val_test_splits(
    data_dir: Path,
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    seed: int = 42,
) -> Tuple[list, list, list]:
    """
    Split image paths into train/val/test by class.
    Supports: data/raw/train/cats, data/raw/train/dogs; data/raw/cats, data/raw/dogs;
    data/raw/training_set/cats; data/raw/cat, data/raw/dog (singular); etc.
    Returns (train_paths, val_paths, test_paths) each as list of (path, label).
    """
    if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-6:
        raise ValueError("Splits must sum to 1.0")
    rng = np.random.default_rng(seed)
    data_dir = Path(data_dir)
    samples = []
    samples.extend(_collect_class_images(data_dir, _CAT_NAMES, 0))
    samples.extend(_collect_class_images(data_dir, _DOG_NAMES, 1))
    rng.shuffle(samples)
    n = len(samples)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)
    n_test = n - n_train - n_val
    train = samples[:n_train]
    val = samples[n_train : n_train + n_val]
    test = samples[n_train + n_val :]
    return train, val, test


def normalize_for_model(images: np.ndarray) -> np.ndarray:
    """Normalize images for CNN (already in [0,1]; can add ImageNet mean/std if needed)."""
    return images.astype(np.float32)
