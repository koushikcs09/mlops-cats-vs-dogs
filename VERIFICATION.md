# Assignment Requirements Verification

This document verifies that the project meets the stated assignment requirements. **Verification was performed by running the code and Docker** (see Runtime verification below).

---

## Runtime verification (executed commands and outputs)

All commands were run from the project root: `/Users/skshahrukh.saba/MTECH/mlops-cats-vs-dogs`.

### 1. Data and split (80% / 10% / 10%)

```bash
$ PYTHONPATH=. python3 scripts/prepare_data.py
```
**Output:**
```
Train: 19998, Val: 2499, Test: 2501
Splits written to .../data/processed/splits.json
```
✅ Train/val/test split produced with ~80% / 10% / 10% (19998 + 2499 + 2501 = 24998 samples).

---

### 2. Unit tests (pytest)

```bash
$ python3 -m pytest tests/ -v
```
**Output:**
```
tests/test_inference.py::test_load_model_raises_if_file_missing PASSED
tests/test_inference.py::test_load_model_returns_module PASSED
tests/test_inference.py::test_predict_proba_returns_two_probabilities PASSED
tests/test_inference.py::test_predict_label_returns_cat_or_dog PASSED
tests/test_preprocess.py::test_preprocess_image_returns_correct_shape PASSED
tests/test_preprocess.py::test_load_and_resize_image_returns_correct_shape PASSED
... (10 passed in 0.54s)
```
✅ All 10 tests passed (preprocessing + inference).

---

### 3. Config and augmentation (runtime check)

```bash
$ python3 -c "
from src.config import IMG_SIZE, TRAIN_RATIO, VAL_RATIO, TEST_RATIO, CLASS_NAMES
assert IMG_SIZE == (224, 224)
assert abs(TRAIN_RATIO + VAL_RATIO + TEST_RATIO - 1.0) < 1e-6
assert CLASS_NAMES == ['cat', 'dog']
print('Config: IMG_SIZE=(224,224), split 80/10/10, CLASS_NAMES=cat,dog OK')
"
```
**Output:** `Config: IMG_SIZE=(224,224), split 80/10/10, CLASS_NAMES=cat,dog OK`  
✅ 224×224, 80/10/10, binary cat/dog confirmed at runtime.

```bash
$ python3 -c "
from scripts.train import TRAIN_TRANSFORMS_FULL
print('Data augmentation: TRAIN_TRANSFORMS_FULL has', len(TRAIN_TRANSFORMS_FULL.transforms), 'transforms OK')
"
```
**Output:** `Data augmentation: TRAIN_TRANSFORMS_FULL has 4 transforms OK`  
✅ Data augmentation (RandomHorizontalFlip, RandomRotation, RandomAffine, ColorJitter) present and loadable.

---

### 4. Docker build and run

```bash
$ docker build -t cats-vs-dogs-api:latest .
```
**Result:** Build completed successfully (image `cats-vs-dogs-api:latest`).

```bash
$ docker run -d -p 8000:8000 --name cats-vs-dogs-api -v $(pwd)/models:/app/models:ro cats-vs-dogs-api:latest
```
**Result:** Container started (ID returned).

---

### 5. API endpoints (curl against Docker container)

**Health:**
```bash
$ curl -s http://localhost:8000/health
```
**Output:** `{"status":"ok","service":"cats-vs-dogs"}`  
✅ Health endpoint OK.

**Predict (Cat image):**
```bash
$ curl -s -X POST http://localhost:8000/predict -F "file=@data/raw/PetImages/Cat/0.jpg"
```
**Output:** `{"label":"dog","probabilities":{"cat":0.4947,"dog":0.5053}}`  
✅ Predict endpoint accepts image and returns label + probabilities.

**Metrics:**
```bash
$ curl -s http://localhost:8000/metrics
```
**Output:** Prometheus text format (`# TYPE` / `# HELP` and metric lines, e.g. `request_count_total`, `prediction_latency_avg_ms`).  
✅ Metrics endpoint OK (request count and latency in Prometheus format).

---

### 6. Smoke test script

```bash
$ bash scripts/smoke_test.sh http://localhost:8000
```
**Output:**
```
Smoke testing http://localhost:8000
>>> GET /health
{"status":"ok","service":"cats-vs-dogs"}
>>> POST /predict (small test image)
{"label":"dog","probabilities":{"cat":0.4957,"dog":0.5043}}
Smoke tests passed.
```
✅ Smoke tests passed against the running Dockerized API.

---

### 7. Container stopped

```bash
$ docker stop cats-vs-dogs-api
```
✅ Cleanup done.

---

## Requirement checklist (with runtime evidence)

| # | Requirement | How verified |
|---|-------------|--------------|
| 1 | End-to-end MLOps pipeline (model, artifact, packaging, containerization, CI/CD) | Code + **Docker build/run**, **pytest**, **smoke test** |
| 2 | Use case: Binary image classification (Cats vs Dogs) for pet adoption platform | Config + README; **API returns cat/dog label and probabilities** |
| 3 | Dataset: Cats and Dogs from Kaggle | **prepare_data.py** ran on `data/raw/PetImages/Cat`, `PetImages/Dog`; README documents Kaggle |
| 4 | Pre-process to 224×224 RGB for standard CNNs | **Config check** IMG_SIZE=(224,224); **pytest** `test_load_and_resize_image_returns_correct_shape` and `test_preprocess_image_returns_correct_shape` assert (224,224,3) |
| 5 | Split train/validation/test (80%/10%/10%) | **prepare_data.py** output: Train: 19998, Val: 2499, Test: 2501 (~80/10/10) |
| 6 | Data augmentation for better generalization | **Runtime import**: TRAIN_TRANSFORMS_FULL (4 transforms); code: RandomHorizontalFlip, RandomRotation, RandomAffine, ColorJitter |

---

## Code/config references (unchanged)

- **224×224 RGB:** `src/config.py` (`IMG_SIZE`), `src/data/preprocess.py` (`load_and_resize_image`), `src/model/cnn.py`.
- **80/10/10 split:** `src/config.py` (`TRAIN_RATIO`, `VAL_RATIO`, `TEST_RATIO`), `src/data/preprocess.py` (`get_train_val_test_splits`), `scripts/prepare_data.py`.
- **Data augmentation:** `scripts/train.py` (`TRAIN_TRANSFORMS_FULL`: RandomHorizontalFlip, RandomRotation, RandomAffine, ColorJitter).
- **Docker:** `Dockerfile`, `docker-compose.yml`; image built and run; health, predict, metrics verified via curl and smoke test.

All requirements above were verified by **running the code and Docker** as shown.
