"""
Prepare dataset: expect raw data in data/raw (e.g. Kaggle cats/dogs structure).
Writes processed splits to data/processed for DVC tracking.
"""
import argparse
import json
from pathlib import Path

from src.config import DATA_RAW, DATA_PROCESSED, TRAIN_RATIO, VAL_RATIO, TEST_RATIO
from src.data import get_train_val_test_splits


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DATA_RAW)
    parser.add_argument("--out-dir", type=Path, default=DATA_PROCESSED)
    parser.add_argument("--train-ratio", type=float, default=TRAIN_RATIO)
    parser.add_argument("--val-ratio", type=float, default=VAL_RATIO)
    parser.add_argument("--test-ratio", type=float, default=TEST_RATIO)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    data_dir = args.data_dir
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    train, val, test = get_train_val_test_splits(
        data_dir,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed,
    )

    # Save split metadata (paths and labels) so training can load from disk
    splits = {
        "train": [{"path": p, "label": l} for p, l in train],
        "val": [{"path": p, "label": l} for p, l in val],
        "test": [{"path": p, "label": l} for p, l in test],
    }
    with open(out_dir / "splits.json", "w") as f:
        json.dump(splits, f, indent=2)

    # Optionally save small numpy arrays for DVC (e.g. first 100 of each for testing)
    # For full data, DVC tracks the raw/processed folders
    print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
    print(f"Splits written to {out_dir / 'splits.json'}")


if __name__ == "__main__":
    main()
