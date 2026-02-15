# MLOps Assignment 2 Report  
## Cats vs Dogs: End-to-End MLOps Pipeline for Pet Adoption Platform

**Course:** MLOps (S1-25_AIMLCZG523)  
**Institution:** BITS Pilani  
**Assignment:** Assignment 2 – Model building, artifact creation, packaging, containerization, CI/CD deployment  
**GitHub Repository:** _add your repo URL_

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [M1: Model Development & Experiment Tracking](#2-m1-model-development--experiment-tracking)
3. [M2: Model Packaging & Containerization](#3-m2-model-packaging--containerization)
4. [M3: CI Pipeline](#4-m3-ci-pipeline)
5. [M4: CD Pipeline & Deployment](#5-m4-cd-pipeline--deployment)
6. [M5: Monitoring & Logging](#6-m5-monitoring--logging)
7. [Deliverables](#7-deliverables)
8. [Appendix](#8-appendix)

---

## 1. Executive Summary

This report documents the implementation of an end-to-end MLOps pipeline for **binary image classification (Cats vs Dogs)** for a pet adoption platform, as per Assignment 2 (S1-25_AIMLCZG523). The project covers:

- **Data & code versioning:** Git for source code; DVC for dataset and pre-processed data versioning.
- **Model building:** Baseline CNN (224×224 RGB input), saved as `model.pt`; data augmentation for better generalization.
- **Experiment tracking:** MLflow for runs, parameters, metrics, confusion matrix, and loss curves.
- **Inference service:** FastAPI with `/health` and `/predict` (image upload → label and probabilities).
- **Containerization:** Dockerfile and docker-compose; build and run verified via curl.
- **CI:** GitHub Actions – checkout, install deps, run unit tests, build Docker image, push to GHCR.
- **CD:** On main, pull image from registry, deploy, run smoke tests (health + one prediction); pipeline fails if smoke tests fail.
- **Monitoring:** Request/response logging (no sensitive data), request count and latency via `/metrics`; script to collect a batch of predictions and true labels for post-deployment tracking.

**Deliverables:** Zip of source code, configs, and trained model artefact; screen recording (< 5 min) of the workflow from code change to deployed model prediction.

---

## 2. M1: Model Development & Experiment Tracking

### 2.1 Data & Code Versioning

| Tool | Purpose |
|------|--------|
| **Git** | Source code versioning (project structure, scripts, notebooks). |
| **DVC** | Dataset and pre-processed data versioning; pipeline in `dvc.yaml` (prepare → train). |

DVC is used with a remote (e.g. S3/GCS) for large files; Git holds only `.dvc` pointer files. See README for setup.

### 2.2 Dataset & Preprocessing

- **Dataset:** Cats and Dogs binary classification (Kaggle); supports layouts such as `PetImages/Cat`, `PetImages/Dog`, or `train/cats`, `train/dogs`.
- **Preprocessing:** Images resized to **224×224 RGB**; train/validation/test split **80% / 10% / 10%**.
- **Data augmentation (training only):** Random horizontal flip, rotation (±15°), color jitter (brightness, contrast, saturation) for better generalization.

### 2.3 Model Building

- **Model:** Simple CNN in `src/model/cnn.py` (conv blocks + classifier); input 224×224×3, output 2 classes (cat, dog).
- **Serialization:** Trained model saved as **`models/model.pt`** (PyTorch state_dict).

### 2.4 Experiment Tracking

- **Tool:** MLflow.
- **Logged:** Parameters (epochs, batch_size, lr), metrics (train_loss, val_loss, val_acc) per epoch, artifacts (confusion matrix JSON, loss curve history JSON), and the model.
- **Location:** `mlruns/` (local). Run `mlflow ui --backend-store-uri ./mlruns` to view.

---

## 3. M2: Model Packaging & Containerization

### 3.1 Inference Service

- **Framework:** FastAPI.
- **Endpoints:**
  - `GET /` – Landing page (HTML) with links to `/docs`, `/redoc`, `/openapi.json`, `/health`.
  - `GET /health` – Health check for smoke tests and orchestration.
  - `POST /predict` – Accepts an image file (multipart); returns `label` (cat/dog) and `probabilities` (P(cat), P(dog)).
  - `GET /metrics` – Request count and latency (in-app counters).
  - Interactive docs: `/docs` (Swagger UI), `/redoc` (ReDoc), `/openapi.json` (OpenAPI schema).

### 3.2 Environment Specification

- **File:** `requirements.txt` with **version pinning** for key ML and API libraries (e.g. torch, torchvision, fastapi, uvicorn) for reproducibility.

### 3.3 Containerization

- **Dockerfile:** Multi-stage not required; single stage with `requirements.txt`, `src/`, `api/`, and `models/` (or mount at run time).
- **Build & run:** Documented in README and QUICKSTART.md; verification via `curl` for `/health` and `/predict`.

---

## 4. M3: CI Pipeline

### 4.1 Automated Testing

- **Scope:** At least one **data pre-processing** function and one **model utility/inference** function.
- **Tool:** pytest (`tests/test_preprocess.py`, `tests/test_inference.py`); config in `pytest.ini` (pythonpath, testpaths).
- **Run:** `pytest tests/ -v` from project root.

### 4.2 CI Setup

- **Platform:** GitHub Actions (`.github/workflows/ci.yml`).
- **Trigger:** On every push/merge request to main (or default branch).
- **Steps:** Checkout → install dependencies → run unit tests → build Docker image (with placeholder model if needed for build).

### 4.3 Artifact Publishing

- **Registry:** GitHub Container Registry (ghcr.io).
- **Behavior:** On push (non–pull-request), the pipeline pushes the built Docker image to the registry (e.g. `ghcr.io/<owner>/<repo>:<branch>`).

---

## 5. M4: CD Pipeline & Deployment

### 5.1 Deployment Target

- **Choice:** Docker Compose (and/or local Kubernetes if desired).
- **Manifests:** `docker-compose.yml` for local/VM deployment; optional Kubernetes Deployment + Service YAML as in the first assignment.

### 5.2 CD / GitOps Flow

- **Tool:** GitHub Actions (`.github/workflows/cd.yml`).
- **Trigger:** Runs after the CI workflow completes successfully on main (workflow_run).
- **Steps:** Log in to GHCR → **pull the new image** from the registry → run container → execute smoke tests → stop container.
- **Outcome:** Deployment/update of the running service is driven by main branch changes via the CI/CD workflow.

### 5.3 Smoke Tests / Health Check

- **Implementation:** Script and CD job call the **health** endpoint and **one prediction** (e.g. small test image).
- **Failure:** Pipeline is failed if smoke tests fail (e.g. `curl -sf`).

---

## 6. M5: Monitoring & Logging

### 6.1 Basic Monitoring & Logging

- **Request/response logging:** Enabled in the inference service (middleware); logs method, path, status, latency; **no sensitive data** (no body/headers).
- **Metrics:** Request count and latency tracked in-app and exposed at **`GET /metrics`** (e.g. request_count, latency_ms_avg).

### 6.2 Model Performance Tracking (Post-Deployment)

- **Script:** `scripts/collect_predictions.py` – collects a small batch of real or simulated requests and true labels (from test/val splits), runs model inference, and writes results (e.g. `predictions_batch.json`) for post-deployment analysis.

---

## 7. Deliverables

| # | Deliverable | Status |
|---|-------------|--------|
| 1 | Zip file: source code, configs (DVC, CI/CD, Docker, deployment manifests), trained model artefact | ✅ |
| 2 | Screen recording (< 5 min): complete MLOps workflow from code change to deployed model prediction | _Add link_ |

**Repository structure:** See README “Project Structure” and Appendix.

**Video:** _Insert link to your screen recording (e.g. Google Drive / OneDrive) here._

---

## 8. Appendix

### A. Repository structure (key items)

```
├── api/main.py
├── src/config.py, data/, model/, inference/
├── scripts/prepare_data.py, train.py, download_data.py, smoke_test.sh, collect_predictions.py
├── tests/test_preprocess.py, test_inference.py
├── dvc.yaml, params.yaml
├── Dockerfile, docker-compose.yml
├── .github/workflows/ci.yml, cd.yml
├── requirements.txt
├── RUN_STEPS.md, QUICKSTART.md
├── reports/MLOps_Assignment2_Report.md
└── docs/API.md, DEPLOYMENT.md
```

### B. Quick command reference

| Action | Command |
|--------|--------|
| Prepare data | `PYTHONPATH=. python scripts/prepare_data.py` |
| Train | `PYTHONPATH=. python scripts/train.py --epochs 3` |
| Run API (Docker) | `docker run -p 8000:8000 -v $(pwd)/models:/app/models:ro cats-vs-dogs-api:latest` |
| Health | `curl http://localhost:8000/health` |
| Predict | `curl -X POST http://localhost:8000/predict -F "file=@<image.jpg>"` |
| Smoke test | `bash scripts/smoke_test.sh http://localhost:8000` |

### C. References

- Assignment 2 PDF (S1-25_AIMLCZG523).
- Kaggle Cats and Dogs dataset (e.g. bhavikjikadara/dog-and-cat-classification-dataset).
- MLflow, FastAPI, DVC, GitHub Actions documentation.
