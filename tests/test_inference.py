"""Unit tests for model inference utilities."""
import tempfile
from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image

from src.inference import (
    load_model,
    preprocess_image,
    predict_proba,
    predict_label,
)
from src.model import get_model


@pytest.fixture
def dummy_model_path(tmp_path):
    """Create a minimal state_dict file for loading."""
    model = get_model(num_classes=2)
    p = tmp_path / "model.pt"
    torch.save(model.state_dict(), p)
    return p


def test_load_model_raises_if_file_missing():
    with pytest.raises(FileNotFoundError):
        load_model("/nonexistent/model.pt")


def test_load_model_returns_module(dummy_model_path):
    model = load_model(dummy_model_path)
    assert hasattr(model, "forward")


def test_predict_proba_returns_two_probabilities(dummy_model_path):
    model = load_model(dummy_model_path)
    x = np.random.rand(1, 3, 224, 224).astype(np.float32)
    probs = predict_proba(model, x)
    assert len(probs) == 2
    assert abs(sum(probs) - 1.0) < 1e-5
    assert all(0 <= p <= 1 for p in probs)


def test_predict_label_returns_cat_or_dog(dummy_model_path):
    model = load_model(dummy_model_path)
    x = np.random.rand(1, 3, 224, 224).astype(np.float32)
    label = predict_label(model, x)
    assert label in ("cat", "dog")


def test_preprocess_image_returns_correct_shape():
    """Test preprocess_image returns (1, C, H, W) for model input."""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        Image.new("RGB", (50, 50)).save(f.name)
        path = f.name
    try:
        arr = preprocess_image(path)
        assert arr.shape == (1, 3, 224, 224)
        assert arr.dtype == np.float32
    finally:
        Path(path).unlink(missing_ok=True)
