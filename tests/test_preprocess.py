"""Unit tests for data preprocessing functions."""
import tempfile
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from src.data import load_and_resize_image, get_train_val_test_splits, normalize_for_model


def test_load_and_resize_image_returns_correct_shape():
    """Test that load_and_resize_image returns (224, 224, 3) RGB in [0, 1]."""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        img = Image.new("RGB", (100, 100), color=(128, 128, 128))
        img.save(f.name)
        path = f.name
    try:
        arr = load_and_resize_image(path, target_size=(224, 224))
        assert arr.shape == (224, 224, 3)
        assert arr.dtype == np.float32
        assert arr.min() >= 0 and arr.max() <= 1.0
    finally:
        Path(path).unlink(missing_ok=True)


def test_load_and_resize_image_nonexistent_raises():
    """Test that missing file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_and_resize_image("/nonexistent/path/image.jpg")


def test_get_train_val_test_splits_ratios_sum_to_one():
    """Test that split ratios must sum to 1.0."""
    with pytest.raises(ValueError):
        get_train_val_test_splits(Path("/tmp"), train_ratio=0.5, val_ratio=0.5, test_ratio=0.1)


def test_get_train_val_test_splits_empty_dir_returns_empty_lists():
    """Test that empty data dir returns empty train/val/test."""
    with tempfile.TemporaryDirectory() as d:
        train, val, test = get_train_val_test_splits(Path(d), seed=42)
        assert train == [] and val == [] and test == []


def test_normalize_for_model_preserves_float32():
    """Test normalize_for_model returns float32."""
    x = np.random.rand(2, 224, 224, 3).astype(np.float32)
    out = normalize_for_model(x)
    assert out.dtype == np.float32
    np.testing.assert_array_almost_equal(x, out)
