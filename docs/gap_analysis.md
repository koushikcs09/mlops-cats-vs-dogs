# MLOps Assignment 2 — Gap Analysis

## Summary

The codebase is **substantially complete** and covers all 5 milestones (M1–M5) of the assignment. Only **one deliverable** remains outstanding — the screen recording. Below is a detailed per-task mapping.

---

## M1: Model Development & Experiment Tracking (10M)

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
| 1.1 | Git for source code versioning | ✅ Covered | `.git/` directory, [.gitignore](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/.gitignore), full repo on GitHub |
| 1.2 | DVC for dataset versioning | ✅ Covered | [dvc.yaml](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/dvc.yaml), [data/raw.dvc](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/data/raw.dvc), [.dvc/](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/data/raw.dvc), [.dvcignore](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/.dvcignore) |
| 1.3 | Track pre-processed data | ✅ Covered | DVC pipeline stage `prepare` outputs `data/processed/splits.json` |
| 1.4 | Pre-process to 224×224 RGB | ✅ Covered | [preprocess.py](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/src/data/preprocess.py) — [load_and_resize_image()](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/src/data/preprocess.py#10-26) resizes to (224, 224) RGB |
| 1.5 | 80/10/10 train/val/test split | ✅ Covered | [params.yaml](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/params.yaml) defines 0.8/0.1/0.1; [config.py](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/src/config.py) has constants |
| 1.6 | Data augmentation | ✅ Covered | [train.py](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/scripts/train.py) — `TRAIN_TRANSFORMS_FULL` with flip, rotation, affine, color jitter |
| 1.7 | Baseline model (CNN) | ✅ Covered | [cnn.py](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/src/model/cnn.py) — [SimpleCNN](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/src/model/cnn.py#38-73) (4-layer CNN with BatchNorm) |
| 1.8 | Save model as `.pt` | ✅ Covered | `torch.save(model.state_dict(), model_path)` in [train.py](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/scripts/train.py); output → `models/model.pt` |
| 1.9 | MLflow experiment tracking | ✅ Covered | [train.py](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/scripts/train.py) logs params, metrics (train_loss, val_loss, val_acc), confusion matrix, loss curves, model artifact |

> [!TIP]
> **M1 is fully covered.** The DVC pipeline (`dvc repro`) chains `prepare → train` with full dependency tracking and parameter management.

---

## M2: Model Packaging & Containerization (10M)

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
| 2.1 | REST API (FastAPI/Flask) | ✅ Covered | [api/main.py](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/api/main.py) — FastAPI app |
| 2.2 | Health check endpoint | ✅ Covered | `GET /health` → `{"status": "ok", "service": "cats-vs-dogs"}` |
| 2.3 | Prediction endpoint | ✅ Covered | `POST /predict` — accepts image, returns label + probabilities |
| 2.4 | [requirements.txt](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/requirements.txt) with version pinning | ✅ Covered | [requirements.txt](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/requirements.txt) — all major libs pinned (torch==2.2.0, fastapi==0.109.2, etc.) |
| 2.5 | Dockerfile | ✅ Covered | [Dockerfile](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/Dockerfile) — python:3.11-slim, copies src/api/models, runs uvicorn |
| 2.6 | Build and run locally, verify via curl | ✅ Covered | `docker build` & `docker run` instructions; [smoke_test.sh](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/scripts/smoke_test.sh) verifies with curl |

> [!TIP]
> **M2 is fully covered.** Has two endpoints (health + predict) as required, plus bonus endpoints (`/metrics`, `/docs`).

---

## M3: CI Pipeline — Build, Test & Image Creation (10M)

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
| 3.1 | Unit test for data pre-processing | ✅ Covered | [test_preprocess.py](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/tests/test_preprocess.py) — 5 tests for `load_and_resize_image`, `get_train_val_test_splits`, `normalize_for_model` |
| 3.2 | Unit test for model/inference | ✅ Covered | [test_inference.py](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/tests/test_inference.py) — 5 tests for `load_model`, `predict_proba`, `predict_label`, `preprocess_image` |
| 3.3 | Tests run via pytest | ✅ Covered | `pytest.ini` configured; CI runs `pytest tests/ -v` |
| 3.4 | CI pipeline (GitHub Actions) | ✅ Covered | [ci.yml](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/.github/workflows/ci.yml) — triggers on push/PR to main/master |
| 3.5 | Pipeline: checkout → install → test → build | ✅ Covered | `test` job → `build` job (sequential, `needs: test`) |
| 3.6 | Push Docker image to registry | ✅ Covered | Pushes to GHCR (`ghcr.io/${{ github.repository }}`) on push (not on PRs) |

> [!TIP]
> **M3 is fully covered.** Additionally includes a `release.yml` workflow for model training + GitHub Releases + optional Artifactory upload.

---

## M4: CD Pipeline & Deployment (10M)

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
| 4.1 | Deployment target (K8s / Docker Compose) | ✅ Covered | **Both** options: [docker-compose.yml](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/docker-compose.yml) + [k8s/](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/k8s/deployment.yaml) (Deployment + Service) |
| 4.2 | K8s manifests (Deployment + Service) | ✅ Covered | `k8s/deployment.yaml` + `k8s/service.yaml` with health probes, resource limits |
| 4.3 | CD / GitOps flow | ✅ Covered | [cd.yml](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/.github/workflows/cd.yml) — triggers after CI → pulls image → deploys → smoke tests |
| 4.4 | Auto-deploy on main branch changes | ✅ Covered | CD triggers via `workflow_run` on CI completion for `main/master` |
| 4.5 | Post-deploy smoke test (health + predict) | ✅ Covered | CD workflow runs `curl /health` + `curl /predict` with test image |
| 4.6 | Fail pipeline if smoke tests fail | ✅ Covered | Uses `curl -sf` (fail-fast); pipeline fails on non-zero exit code |

> [!TIP]
> **M4 is fully covered.** Also includes a `deploy_k8s.sh` convenience script for one-command local K8s deployment via `kind`.

---

## M5: Monitoring, Logs & Final Submission (10M)

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
| 5.1 | Request/response logging (no sensitive data) | ✅ Covered | `log_requests` middleware in `api/main.py` — logs method, path, status, latency (no body/headers) |
| 5.2 | Track request count + latency | ✅ Covered | In-app counters (`_REQUEST_COUNT`, `_PREDICT_COUNT`, `_LATENCIES`); exposed via `/metrics` |
| 5.3 | Prometheus-style metrics endpoint | ✅ Covered | `GET /metrics` returns Prometheus text format |
| 5.4 | Prometheus + Grafana monitoring stack | ✅ Covered | [docker-compose-monitoring.yml](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/monitoring/docker-compose-monitoring.yml), `prometheus.yml`, Grafana dashboards + datasources |
| 5.5 | Post-deployment performance tracking | ✅ Covered | [collect_predictions.py](file:///c:/Users/koush/OneDrive/Documents/BITS%20Pilani/MLOPS/Assignment2/mlops-cats-vs-dogs/scripts/collect_predictions.py) — runs model on test batch, outputs `predictions_batch.json` with true labels, accuracy |
| 5.6 | All source code + configs in zip | ✅ Covered | Full repo has all code, DVC, CI/CD, Docker, K8s configs |
| 5.7 | Trained model artifacts | ✅ Covered | `models/model.pt` after training; also attached to GitHub Releases |
| 5.8 | Screen recording (< 5 min) | ⚠️ **PENDING** | README checklist shows "⏳" — recording needs to be created |

> [!WARNING]
> **M5 has one gap:** The **screen recording** demonstrating the end-to-end workflow (code change → deployed prediction) has not yet been created. This is explicitly required in the Deliverables section of the assignment.

---

## Overall Gap Summary

| Area | Status | Details |
|------|--------|---------|
| M1 (10M) | ✅ Complete | All 9 sub-requirements met |
| M2 (10M) | ✅ Complete | All 6 sub-requirements met |
| M3 (10M) | ✅ Complete | All 6 sub-requirements met |
| M4 (10M) | ✅ Complete | All 6 sub-requirements met |
| M5 (10M) | ⚠️ 1 Gap | 7/8 sub-requirements met; **screen recording** pending |

### The Only Gap

> [!CAUTION]
> **Screen Recording (Deliverable #2):** The assignment requires a screen recording of less than 5 minutes demonstrating the complete MLOps workflow from code change to deployed model prediction. This must be created and linked in the report.

### Bonus Coverage (Beyond Requirements)

The codebase goes beyond the minimum requirements in several areas:
- **Dual model architectures** (`SimpleCNN` + `SimpleCNNLegacy` with auto-detection)
- **Release workflow** (`release.yml`) for automated model training + GitHub Releases + Artifactory
- **Live deployment** on Render with `MODEL_URL` support
- **Grafana dashboard** with provisioned dashboards + datasources
- **Comprehensive documentation** (README, GETTING_STARTED, DEPLOYMENT, API, INDEX, VERIFICATION, Report)
