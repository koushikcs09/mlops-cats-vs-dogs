#!/usr/bin/env bash
# Download Kaggle Dog and Cat dataset to data/raw
# Requires: pip install kaggle, and Kaggle API key at ~/.kaggle/kaggle.json
# Run from repo root: bash scripts/download_data.sh
set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
DATASET="${1:-bhavikjikadara/dog-and-cat-classification-dataset}"
RAW_DIR="${2:-data/raw}"
mkdir -p "$RAW_DIR"
cd "$RAW_DIR"
echo "Downloading $DATASET into $(pwd)..."
kaggle datasets download -d "$DATASET"
ZIP=$(ls -t *.zip 2>/dev/null | head -1)
if [ -n "$ZIP" ]; then
  echo "Unzipping $ZIP..."
  unzip -o -q "$ZIP"
  rm -f "$ZIP"
  echo "Done. Sample layout:"
  find . -maxdepth 3 -type d | head -20
  echo "Image count: $(find . -maxdepth 4 \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) 2>/dev/null | wc -l)"
else
  echo "No zip found; check download."
fi
