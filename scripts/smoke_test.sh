#!/usr/bin/env bash
# M4: Post-deploy smoke test - health + one prediction. Exit non-zero on failure.
set -e
BASE_URL="${1:-http://localhost:8000}"
echo "Smoke testing $BASE_URL"

# Health check
echo ">>> GET /health"
curl -sf "$BASE_URL/health" | head -c 200
echo ""

# Prediction (small test image)
echo ">>> POST /predict (small test image)"
TMP=$(mktemp -d)
export TMP
python3 -c "
import os
from PIL import Image
from pathlib import Path
p = Path(os.environ['TMP']) / 'test.jpg'
Image.new('RGB', (224, 224), (128,128,128)).save(p)
"
curl -sf -X POST "$BASE_URL/predict" -F "file=@$TMP/test.jpg" | head -c 300
echo ""
rm -rf "$TMP"

echo "Smoke tests passed."
