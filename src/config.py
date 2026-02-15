"""Configuration and constants for the project."""
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

# Image preprocessing (224x224 for standard CNNs)
IMG_SIZE = (224, 224)
IMG_SHAPE = (224, 224, 3)
NUM_CLASSES = 2
CLASS_NAMES = ["cat", "dog"]

# Train/val/test split
TRAIN_RATIO = 0.8
VAL_RATIO = 0.1
TEST_RATIO = 0.1

# Training defaults (more epochs for better accuracy within assignment spec)
DEFAULT_EPOCHS = 12
DEFAULT_BATCH_SIZE = 64  # larger = fewer steps/epoch = faster (if memory allows)
DEFAULT_LEARNING_RATE = 1e-3

# Model artifact
DEFAULT_MODEL_FILENAME = "model.pt"
