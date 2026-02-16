# MLOps Assignment 2: Cats vs Dogs (Pet Adoption Platform)

**BITS Pilani - MLOps Assignment 2 (S1-25_AIMLCZG523)**  
**Use case:** Binary image classification (Cats vs Dogs) for a pet adoption platform.

| # | Task | Marks | Status | Section |
|---|------|-------|--------|---------|
| 1 | M1: Model Development & Experiment Tracking | 10 | ✅ Complete | [M1](#m1-model-development--experiment-tracking) |
| 2 | M2: Model Packaging & Containerization | 10 | ✅ Complete | [M2](#m2-model-packaging--containerization) |
| 3 | M3: CI Pipeline (Build, Test & Image Creation) | 10 | ✅ Complete | [M3](#m3-ci-pipeline) |
| 4 | M4: CD Pipeline & Deployment | 10 | ✅ Complete | [M4](#m4-cd-pipeline--deployment) |
| 5 | M5: Monitoring, Logs & Final Submission | 10 | ✅ Complete | [M5](#m5-monitoring--logging) |
| | **Total** | **50** | ✅ | |

📋 **[Step-by-step run guide](RUN_STEPS.md)** | 🚀 **[Quick Start (Docker)](QUICKSTART.md)** | 📄 **[Assignment Report](reports/MLOps_Assignment2_Report.md)** | 📖 **[API Documentation](docs/API.md)** | 📦 **[Deployment Guide](docs/DEPLOYMENT.md)**

---

## Deliverables Checklist

| Item | Status | Location / Notes |
|------|--------|------------------|
| Source code (src, api, scripts) | ✅ | `src/`, `api/`, `scripts/` |
| Configs (DVC, CI/CD, Docker, deployment) | ✅ | `dvc.yaml`, `.github/workflows/`, `Dockerfile`, `docker-compose.yml` |
| Trained model artefact | ✅ | `models/model.pt` (after training) |
| requirements.txt (pinned versions) | ✅ | `requirements.txt` |
| Unit tests | ✅ | `tests/` |
| Screen recording (< 5 min) | ⏳ | Link to video: _add your link_ |

---

## Table of Contents

- [Requirements](#requirements) · [Dataset](#dataset) · [Project Structure](#project-structure)
- [M1: Model Development & Experiment Tracking](#m1-model-development--experiment-tracking)
- [M2: Model Packaging & Containerization](#m2-model-packaging--containerization)
- [M3: CI Pipeline](#m3-ci-pipeline)
- [M4: CD Pipeline & Deployment](#m4-cd-pipeline--deployment)
- [M5: Monitoring & Logging](#m5-monitoring--logging)
- [Deliverables](#deliverables) · [Quick Start](#quick-start-after-cloning)

---

## Requirements

- Python 3.9+ (3.11 recommended)
- Dataset: Dog and Cat classification dataset (see below). Run all commands from the **project root**; use `PYTHONPATH=.` when running scripts so `src` is importable (e.g. `PYTHONPATH=. python scripts/prepare_data.py`).

## Dataset

This project uses the **Dog and Cat classification dataset** from Kaggle. Download it into `data/raw` using either method below.

**Option A – kagglehub (no API key):**

```bash
pip install kagglehub
python scripts/download_data.py
```

The script uses `kagglehub.dataset_download("bhavikjikadara/dog-and-cat-classification-dataset")` and copies the result to `data/raw`. The dataset is ~775 MB; allow a few minutes on a good connection.

**Option B – Kaggle CLI (needs API key):**

```bash
pip install kaggle
# Place kaggle.json at ~/.kaggle/kaggle.json (from Kaggle → Create New API Token)
bash scripts/download_data.sh
```

**Option C – Manual:** Open [the dataset on Kaggle](https://www.kaggle.com/datasets/bhavikjikadara/dog-and-cat-classification-dataset), click **Download**, then unzip the file into `data/raw`.

**Option D – Use a zip you already downloaded:** If you have the dataset zip (e.g. `~/Downloads/archive.zip`), unzip it into `data/raw`; the code supports the `PetImages/Cat` and `PetImages/Dog` layout:

```bash
unzip -o ~/Downloads/archive.zip -d data/raw
```

The code supports common folder layouts: `train/cats`, `train/dogs`; `training_set/cats`, `training_set/dogs`; or flat `cats/`, `dogs/` (and singular `cat`/`dog`, or `Cat`/`Dog`). After unpacking, ensure images live under `data/raw` in such a structure, then run `python scripts/prepare_data.py`.

## Project Structure

```
├── monitoring/               # Optional: Prometheus + Grafana (docker-compose-monitoring.yml)
├── api/
│   └── main.py              # FastAPI: /, /health, /predict, /metrics (Prometheus), /docs
├── src/
│   ├── config.py            # Paths and constants
│   ├── data/                # Preprocessing, train/val/test splits
│   ├── model/               # CNN model (src/model/cnn.py)
│   └── inference/           # Load model, predict
├── scripts/
│   ├── download_data.py     # kagglehub download → data/raw (no API key)
│   ├── download_data.sh     # Kaggle CLI download → data/raw
│   ├── prepare_data.py      # Train/val/test splits → data/processed/splits.json
│   ├── train.py             # Train with MLflow, save models/model.pt
│   ├── collect_predictions.py  # M5: batch predictions + true labels
│   └── smoke_test.sh        # Post-deploy health + predict check
├── tests/                   # Unit tests (preprocess + inference)
├── models/                  # Trained model.pt (from train or DVC)
├── data/
│   ├── raw/                 # Raw images (DVC or unzip here)
│   └── processed/           # splits.json (DVC)
├── dvc.yaml                 # DVC pipeline (prepare → train)
├── params.yaml              # DVC/training parameters
├── pytest.ini               # pytest pythonpath and testpaths
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .github/workflows/
    ├── ci.yml               # Test + build + push image
    └── cd.yml               # Deploy + smoke test
```

## M1: Model Development & Experiment Tracking

- **Git**: Source code versioned in this repo.
- **DVC**: Track data and model (see below).
- **Model**: Baseline CNN in `src/model/cnn.py`; saved as `models/model.pt`.
- **MLflow**: Run `scripts/train.py`; logs params, metrics, confusion matrix, loss curves to `mlruns/`.

```bash
# 1. Put dataset in data/raw (see Dataset section for download options)
pip install -r requirements.txt
PYTHONPATH=. python scripts/prepare_data.py

# 2. Train (MLflow logs to mlruns/, model saved to models/model.pt)
PYTHONPATH=. python scripts/train.py --epochs 3
```

### DVC + GitHub

**DVC is fully compatible with GitHub.** Here’s how it fits together:

- **Git (GitHub)** stores your source code and DVC *metadata* (small `.dvc` pointer files and `dvc.lock`). No large files are committed to the repo.
- **DVC remote** stores the actual large files (datasets, processed data, model artifacts). This can be:
  - **Amazon S3**, **Google Cloud Storage**, **Azure Blob**, or **SSH** (recommended for teams).
  - **Git LFS** (e.g. `dvc remote add myremote gdrive://...` or an LFS-backed repo) for smaller datasets if you prefer.

So: **GitHub = code + .dvc files**; **DVC remote = data and model files**. Teammates clone the repo from GitHub, then run `dvc pull` to get the data from the DVC remote.

**Setup (example with an S3 bucket):**

```bash
dvc init
git add .dvc .gitignore
git commit -m "Initialize DVC"

# Add a DVC remote (e.g. S3; use your bucket/credentials)
dvc remote add myremote s3://your-bucket/dvc-store
dvc push

# Others clone the repo from GitHub, then:
dvc pull
```

**What’s versioned:**

- **`data/raw`** – tracked with `dvc add data/raw` (pointer: `data/raw.dvc`). Commit this file so the dataset is versioned.
- **`data/processed`** and **`models/model.pt`** – tracked by the pipeline in `dvc.yaml` (outputs of `prepare` and `train`). Run `dvc repro` to update `dvc.lock` and outputs.

**Commit DVC metadata (after `dvc init` and `dvc add data/raw`):**

```bash
git add .dvc data/.gitignore data/raw.dvc dvc.yaml dvc.lock params.yaml
git commit -m "Track data with DVC (data/raw); pipeline tracks processed data and model"
# Optional: add a remote and push large files
# dvc remote add myremote s3://your-bucket/dvc-store
# dvc push
git push origin main
```

## M2: Model Packaging & Containerization

- **API**: FastAPI with `GET /` (landing + doc links), `GET /health`, `POST /predict` (image file → label + probabilities), `GET /metrics`. Interactive docs: `/docs` (Swagger UI).
- **Environment**: `requirements.txt` with pinned versions.
- **Docker**: Build and run locally:

```bash
# After training (models/model.pt exists)
docker build -t cats-vs-dogs-api:latest .
docker run -p 8000:8000 -v $(pwd)/models:/app/models:ro cats-vs-dogs-api:latest

# Verify
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict -F "file=@/path/to/cat.jpg"
```

## M3: CI Pipeline

- **Tests**: From project root run `pytest tests/` (covers preprocessing and inference). Config in `pytest.ini` sets `pythonpath = .` so `src` is found.
- **GitHub Actions** (`.github/workflows/ci.yml`): On push/PR → checkout, install deps, run tests, build Docker image, push to GitHub Container Registry.

## M4: CD Pipeline & Deployment

- **Deployment**: Docker Compose (or use the same image on a VM/Kubernetes). See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).
- **CD** (`.github/workflows/cd.yml`): After CI completes on `main` → **pull image from GHCR** → run container → smoke tests (health + one prediction). Pipeline fails if smoke tests fail.
- **Local**:

```bash
docker compose up -d
./scripts/smoke_test.sh http://localhost:8000
```

## M5: Monitoring & Logging

- **Logging**: Request method, path, status, latency (no sensitive data) in middleware.
- **Metrics**: `GET /metrics` returns **Prometheus-format** metrics (request count, predictions total, latency, model loaded, uptime) for scraping by Prometheus/Grafana.
- **Grafana stack**: Optional monitoring with Prometheus + Grafana. From project root:
  ```bash
  docker-compose -f monitoring/docker-compose-monitoring.yml up -d
  ```
  Then open **Grafana** at http://localhost:3000 (admin/admin). The **Cats vs Dogs API Dashboard** is provisioned automatically; Prometheus scrapes the API at `api:8000/metrics`.
- **Model performance tracking**: After deployment, collect a batch of predictions and true labels with `scripts/collect_predictions.py` (reads test/val splits and model, writes `predictions_batch.json`).

## Deliverables

1. **Zip**: Source code, configs (DVC, CI/CD, Docker, docker-compose), and trained model artefact.
2. **Screen recording**: Under 5 minutes showing workflow from code change to deployed model prediction. Add your video link in [reports/MLOps_Assignment2_Report.md](reports/MLOps_Assignment2_Report.md) and in the Deliverables Checklist above.

## Quick Start (after cloning)

Run from the **project root**; set `PYTHONPATH=.` so `src` is importable.

```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 1. Get dataset (choose one)
#    A) kagglehub (no API key):  pip install kagglehub && python scripts/download_data.py
#    B) Kaggle CLI:              bash scripts/download_data.sh  (requires ~/.kaggle/kaggle.json)
#    C) Local zip:               unzip -o ~/Downloads/archive.zip -d data/raw

# 2. Prepare splits and train
PYTHONPATH=. python scripts/prepare_data.py
PYTHONPATH=. python scripts/train.py --epochs 3

# 3. Run API (model in models/model.pt)
docker build -t cats-vs-dogs-api .
docker run -p 8000:8000 -v $(pwd)/models:/app/models:ro cats-vs-dogs-api
# In another terminal:
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict -F "file=@<path-to-any-cat-or-dog.jpg>"
```
