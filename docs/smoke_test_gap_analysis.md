# Smoke Test & Gap Analysis Results

## Smoke Tests ✅

| Endpoint | Result |
|---|---|
| `GET /health` | `{"status": "ok", "service": "cats-vs-dogs"}` |
| `POST /predict` (224×224 gray image) | `{"label": "cat", "probabilities": {"cat": 0.5887, "dog": 0.4113}}` |
| `GET /metrics` | Prometheus-format: `predictions_total`, `request_count_total`, `prediction_latency_avg_ms`, `model_loaded`, `app_uptime_seconds` |

## Assignment Gap Analysis

### M1: Model Development & Experiment Tracking (10M) ✅
| Requirement | Status | Evidence |
|---|---|---|
| Git for source code versioning | ✅ | `.git/` present |
| DVC for dataset versioning | ✅ | `dvc.yaml`, `.dvc/`, `data/` |
| Baseline CNN model | ✅ | `src/model/cnn.py`, `scripts/train.py` |
| Serialized model (.pt) | ✅ | `models/model.pt` (1.7 MB) |
| MLflow experiment tracking | ✅ | `mlruns/`, MLflow in `requirements.txt` |

### M2: Model Packaging & Containerization (10M) ✅
| Requirement | Status | Evidence |
|---|---|---|
| REST API (FastAPI) | ✅ | `api/main.py` |
| Health check endpoint | ✅ | `GET /health` verified |
| Prediction endpoint | ✅ | `POST /predict` verified |
| `requirements.txt` with pinned versions | ✅ | All key libs pinned |
| Dockerfile | ✅ | `Dockerfile` (python:3.11-slim) |
| Local build & verify | ✅ | Built and verified via K8s |

### M3: CI Pipeline (10M) ✅
| Requirement | Status | Evidence |
|---|---|---|
| Unit tests (preprocessing) | ✅ | `tests/test_preprocess.py` |
| Unit tests (inference) | ✅ | `tests/test_inference.py` |
| pytest configured | ✅ | `pytest.ini` |
| CI pipeline (GitHub Actions) | ✅ | `.github/workflows/ci.yml` |
| Docker image build in CI | ✅ | Build job in `ci.yml` |
| Push to GHCR | ✅ | `ci.yml` pushes to `ghcr.io` |

### M4: CD Pipeline & Deployment (10M) ✅
| Requirement | Status | Evidence |
|---|---|---|
| K8s deployment target (kind) | ✅ | `scripts/deploy_k8s.sh`, kind cluster running |
| Deployment + Service YAML | ✅ | `k8s/deployment.yaml`, `k8s/service.yaml` |
| Docker Compose alternative | ✅ | `docker-compose.yml` |
| CD workflow (GitHub Actions) | ✅ | `.github/workflows/cd.yml` |
| Post-deploy smoke tests | ✅ | `scripts/smoke_test.sh`, smoke tests in `cd.yml` |
| Pipeline fails on smoke test failure | ✅ | `set -e` in script, separate steps in CD |

### M5: Monitoring, Logs & Final Submission (10M) ✅
| Requirement | Status | Evidence |
|---|---|---|
| Request/response logging (no sensitive data) | ✅ | Middleware in `api/main.py` logs method, path, status, latency |
| Request count & latency tracking | ✅ | In-app counters + `/metrics` endpoint |
| Prometheus metrics | ✅ | `monitoring/prometheus/`, `/metrics` endpoint |
| Grafana dashboard | ✅ | `monitoring/grafana/` |
| Docker Compose for monitoring stack | ✅ | `monitoring/docker-compose-monitoring.yml` |

## Summary
**All 5 milestones (M1–M5) are fully covered.** The deployed API is live on the kind cluster at `localhost:8000` with port-forwarding active.
