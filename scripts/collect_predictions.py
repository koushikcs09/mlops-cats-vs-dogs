"""
M5: Collect a small batch of predictions and true labels for post-deployment performance tracking.
Usage: Call API or run model locally on test set, save (path, true_label, pred_label, probs) to JSON.
"""
import argparse
import json
import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import DATA_PROCESSED, CLASS_NAMES
from src.inference import load_model, predict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=Path, default=Path("models/model.pt"))
    parser.add_argument("--splits", type=Path, default=DATA_PROCESSED / "splits.json")
    parser.add_argument("--out", type=Path, default=Path("predictions_batch.json"))
    parser.add_argument("--max-samples", type=int, default=20)
    args = parser.parse_args()

    with open(args.splits) as f:
        splits = json.load(f)
    test_items = splits.get("test", [])
    if not test_items:
        test_items = splits.get("val", [])[: args.max_samples]
    else:
        test_items = test_items[: args.max_samples]

    model = load_model(args.model_path)
    results = []
    for item in test_items:
        path, true_label_idx = item["path"], item["label"]
        true_label = CLASS_NAMES[true_label_idx]
        out = predict(model, path)
        results.append({
            "path": path,
            "true_label": true_label,
            "pred_label": out["label"],
            "probabilities": out["probabilities"],
            "correct": out["label"] == true_label,
        })
    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)
    acc = sum(r["correct"] for r in results) / len(results) if results else 0
    print(f"Collected {len(results)} predictions -> {args.out} (accuracy on batch: {acc:.2%})")


if __name__ == "__main__":
    main()
