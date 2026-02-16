# MLOps Assignment 2: Cats vs Dogs (Pet Adoption Platform)

[![Release](https://github.com/shahrukhsaba/mlops-cats-vs-dogs/actions/workflows/release.yml/badge.svg)](https://github.com/shahrukhsaba/mlops-cats-vs-dogs/actions/workflows/release.yml)
[![CI](https://github.com/shahrukhsaba/mlops-cats-vs-dogs/actions/workflows/ci.yml/badge.svg)](https://github.com/shahrukhsaba/mlops-cats-vs-dogs/actions/workflows/ci.yml)
[![CD](https://github.com/shahrukhsaba/mlops-cats-vs-dogs/actions/workflows/cd.yml/badge.svg)](https://github.com/shahrukhsaba/mlops-cats-vs-dogs/actions/workflows/cd.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

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

---

## Documentation index

**Start here:** [**docs/GETTING_STARTED.md**](docs/GETTING_STARTED.md) — step-by-step from **clone → run locally → deploy to Render**.

| What you need | Document |
|---------------|----------|
| **Setup from scratch (clone → run locally)** | [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) |
| **Deploy to Render (or other cloud)** | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#rendercom-or-other-public-cloud) |
| **Full doc index** | [docs/INDEX.md](docs/INDEX.md) |
| API reference | [docs/API.md](docs/API.md) |
| Deployment (Docker, K8s, CI/CD, Render) | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) |
| **View Grafana dashboard locally** | [docs/DEPLOYMENT.md#monitoring-stack-prometheus--grafana](docs/DEPLOYMENT.md#monitoring-stack-prometheus--grafana) |
| Kubernetes (kind, one-command deploy) | [k8s/README.md](k8s/README.md) |
| Assignment report | [reports/MLOps_Assignment2_Report.md](reports/MLOps_Assignment2_Report.md) |
| Verification (runtime evidence) | [VERIFICATION.md](VERIFICATION.md) |

---

## Live API (Render)

The API is deployed on Render. Base URL:

**https://mlops-cats-vs-dogs.onrender.com/**

| Endpoint | URL |
|----------|-----|
| Landing | [https://mlops-cats-vs-dogs.onrender.com/](https://mlops-cats-vs-dogs.onrender.com/) |
| Health | [https://mlops-cats-vs-dogs.onrender.com/health](https://mlops-cats-vs-dogs.onrender.com/health) |
| Swagger UI | [https://mlops-cats-vs-dogs.onrender.com/docs](https://mlops-cats-vs-dogs.onrender.com/docs) |
| Predict | `POST https://mlops-cats-vs-dogs.onrender.com/predict` (multipart: `file` = image) |
| Metrics | [https://mlops-cats-vs-dogs.onrender.com/metrics](https://mlops-cats-vs-dogs.onrender.com/metrics) |

Example: `curl https://mlops-cats-vs-dogs.onrender.com/health`

---

## Grafana dashboard (local)

To run the API with Prometheus and Grafana and view the dashboard locally:

1. Ensure the API image is built and `models/model.pt` exists (or use a placeholder).
2. Start the monitoring stack from project root:
   ```bash
   docker-compose -f monitoring/docker-compose-monitoring.yml up -d
   ```
3. Open **Grafana**: http://localhost:3000 (login: `admin` / `admin`). The **Cats vs Dogs API Dashboard** is auto-provisioned (predictions, latency, model status, uptime).
4. Prometheus: http://localhost:9090. API: http://localhost:8000.

To stop: `docker-compose -f monitoring/docker-compose-monitoring.yml down`.  
Full details: [docs/DEPLOYMENT.md § Monitoring stack](docs/DEPLOYMENT.md#monitoring-stack-prometheus--grafana).

---

## Setup from scratch (summary)

1. **Clone** → `git clone <repo> && cd mlops-cats-vs-dogs`
2. **Environment** → `python3 -m venv venv && source venv/bin/activate` (Windows: `venv\Scripts\activate`)
3. **Install** → `pip install -r requirements.txt`
4. **Data** → Download to `data/raw` (kagglehub, Kaggle CLI, or unzip); see [GETTING_STARTED](docs/GETTING_STARTED.md#4-get-the-dataset-and-prepare-splits).
5. **Splits** → `PYTHONPATH=. python scripts/prepare_data.py`
6. **Train** → `PYTHONPATH=. python scripts/train.py --epochs 3`
7. **Run API** → Uvicorn, Docker, Compose, or Kubernetes; see [GETTING_STARTED § Run the API](docs/GETTING_STARTED.md#6-run-the-api-locally).
8. **Deploy to Render** → Set `MODEL_URL` to a public `model.pt` URL; see [DEPLOYMENT § Render](docs/DEPLOYMENT.md#rendercom-or-other-public-cloud).

**Full step-by-step (including dataset options and Render):** [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md).

---

## Deliverables checklist

| Item | Status | Location / Notes |
|------|--------|------------------|
| Source code (src, api, scripts) | ✅ | `src/`, `api/`, `scripts/` |
| Configs (DVC, CI/CD, Docker, K8s) | ✅ | `dvc.yaml`, `.github/workflows/`, `Dockerfile`, `docker-compose.yml`, `k8s/` |
| Trained model artefact | ✅ | `models/model.pt` (after training) |
| requirements.txt (pinned) | ✅ | `requirements.txt` |
| Unit tests | ✅ | `tests/` |
| Screen recording (< 5 min) | ⏳ | Link: _add in report and below_ |

---

## Requirements

- **Python** 3.9+ (3.11 recommended)
- **Dataset:** [Kaggle Cats and Dogs](https://www.kaggle.com/datasets/bhavikjikadara/dog-and-cat-classification-dataset) — see [GETTING_STARTED § 4](docs/GETTING_STARTED.md#4-get-the-dataset-and-prepare-splits) for download options.
- Run all commands from the **project root**; use `PYTHONPATH=.` when running Python scripts.

---

## Project structure

```
├── api/main.py              # FastAPI: /, /health, /predict, /metrics, /docs
├── src/                     # config, data, model, inference
├── scripts/                 # download_data, prepare_data, train, smoke_test, deploy_k8s
├── tests/                   # pytest (preprocess + inference)
├── k8s/                     # Kubernetes Deployment + Service (+ README)
├── docs/                    # INDEX.md, GETTING_STARTED.md, DEPLOYMENT.md, API.md
├── monitoring/              # Optional: Prometheus + Grafana
├── data/raw, data/processed # Dataset and splits (DVC)
├── models/                  # model.pt (after train)
├── dvc.yaml, params.yaml
├── Dockerfile, docker-compose.yml
└── .github/workflows/       # ci.yml, cd.yml, release.yml
```

---

## M1: Model Development & Experiment Tracking

- **Git** for code; **DVC** for data/model (pipeline in `dvc.yaml`; `data/raw.dvc` for dataset).
- **Model:** CNN in `src/model/cnn.py`; saved as `models/model.pt`.
- **MLflow:** Params, metrics, confusion matrix, loss curves in `mlruns/`.
- **Commands:** [GETTING_STARTED](docs/GETTING_STARTED.md) § 4–5.

## M2: Model Packaging & Containerization

- **API:** FastAPI — `/health`, `/predict` (image → label + probabilities), `/metrics`. Docs: `/docs`.
- **Environment:** `requirements.txt` (pinned).
- **Docker:** `Dockerfile`; build and run: [GETTING_STARTED § 6](docs/GETTING_STARTED.md#6-run-the-api-locally).

## M3: CI Pipeline

- **Tests:** `pytest tests/` (preprocess + inference).
- **GitHub Actions** (`.github/workflows/ci.yml`): push/PR → test, build image, push to GHCR.

## M4: CD Pipeline & Deployment

- **Deploy:** Docker Compose (`docker-compose.yml`), Kubernetes (`k8s/`), or one-command `./scripts/deploy_k8s.sh`.
- **CD** (`.github/workflows/cd.yml`): After CI on `main` → pull image, run container, smoke tests.
- **Details:** [DEPLOYMENT.md](docs/DEPLOYMENT.md), [k8s/README.md](k8s/README.md).

## M5: Monitoring & Logging

- **Logging:** Request method, path, status, latency (no sensitive data).
- **Metrics:** `GET /metrics` (Prometheus). Optional: [monitoring stack](docs/DEPLOYMENT.md#monitoring-stack-prometheus--grafana).
- **Post-deploy:** `scripts/collect_predictions.py` → `predictions_batch.json`.

---

## Deliverables

1. **Zip:** Source code, configs (DVC, CI/CD, Docker, k8s), trained model. If too large, share a link.
2. **Screen recording:** &lt; 5 min (code change → deployed prediction). Add link in [report](reports/MLOps_Assignment2_Report.md) and in the checklist above.
