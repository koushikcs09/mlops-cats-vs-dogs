"""Model loading and prediction utilities for inference API."""
from pathlib import Path
from typing import Any, Dict, List, Union

import numpy as np
import torch

from src.config import CLASS_NAMES, IMG_SIZE
from src.data import load_and_resize_image
from src.model import get_model


def _is_legacy_state_dict(state: Dict[str, torch.Tensor]) -> bool:
    """True if state_dict is from the older CNN without BatchNorm (features.3, features.6)."""
    return "features.3.weight" in state and "features.1.weight" not in state


def load_model(model_path: Union[str, Path]) -> torch.nn.Module:
    """Load trained model from .pt file (state_dict). Supports both BatchNorm and legacy (no-BN) checkpoints."""
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Model not found: {path}")
    state = torch.load(path, map_location="cpu", weights_only=True)
    legacy = _is_legacy_state_dict(state)
    model = get_model(num_classes=len(CLASS_NAMES), legacy=legacy)
    model.load_state_dict(state)
    model.eval()
    return model


def preprocess_image(image_path: Union[str, Path]) -> np.ndarray:
    """Load and preprocess a single image for model input. Returns (1, C, H, W)."""
    img = load_and_resize_image(image_path, target_size=IMG_SIZE)
    img = np.transpose(img, (2, 0, 1))
    return img[np.newaxis, ...].astype(np.float32)


def predict_proba(model: torch.nn.Module, image_array: np.ndarray) -> List[float]:
    """Return class probabilities [P(cat), P(dog)] for input (1, C, H, W)."""
    x = torch.from_numpy(image_array).float()
    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)
    return probs[0].tolist()


def predict_label(model: torch.nn.Module, image_array: np.ndarray) -> str:
    """Return class label (cat or dog) for input (1, C, H, W)."""
    probs = predict_proba(model, image_array)
    idx = int(np.argmax(probs))
    return CLASS_NAMES[idx]


def predict(model: torch.nn.Module, image_path: Union[str, Path]) -> Dict[str, Any]:
    """Full prediction: load image, run model, return label and probabilities."""
    arr = preprocess_image(image_path)
    probs = predict_proba(model, arr)
    label = CLASS_NAMES[int(np.argmax(probs))]
    return {
        "label": label,
        "probabilities": {CLASS_NAMES[i]: probs[i] for i in range(len(CLASS_NAMES))},
    }
