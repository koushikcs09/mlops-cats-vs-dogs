#!/usr/bin/env python3
"""
Download Dog and Cat dataset using kagglehub (no Kaggle API key required).
Copies the dataset into data/raw for the rest of the pipeline.

Usage:
    pip install kagglehub
    python scripts/download_data.py
"""
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
DATASET = "bhavikjikadara/dog-and-cat-classification-dataset"


def main():
    try:
        import kagglehub
    except ImportError:
        print("Install kagglehub: pip install kagglehub", file=sys.stderr)
        sys.exit(1)

    # Download latest version (no Kaggle API key needed)
    print(f"Downloading {DATASET} via kagglehub...")
    path = kagglehub.dataset_download(DATASET)
    print("Path to dataset files:", path)

    path = Path(path)
    if not path.exists():
        print("Download path does not exist.", file=sys.stderr)
        sys.exit(1)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    # kagglehub often returns a versioned cache dir; contents may be in a subdir or at root
    items = list(path.iterdir())
    if len(items) == 1 and items[0].is_dir():
        src = items[0]
    else:
        src = path
    print(f"Copying from {src} to {RAW_DIR}...")
    for child in src.iterdir():
        dest = RAW_DIR / child.name
        if dest.exists():
            if dest.is_dir():
                shutil.rmtree(dest)
            else:
                dest.unlink()
        if child.is_dir():
            shutil.copytree(child, dest)
        else:
            shutil.copy2(child, dest)
    print("Done. Contents in data/raw:")
    for d in sorted(RAW_DIR.iterdir())[:15]:
        print(f"  {d.name}/")
    count = sum(1 for _ in RAW_DIR.rglob("*.jpg") if _.is_file()) + sum(
        1 for _ in RAW_DIR.rglob("*.png") if _.is_file()
    )
    print(f"  ... ({count} image files)")


if __name__ == "__main__":
    main()
