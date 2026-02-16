# Documentation Index

Use this index to find the right guide for your task. All paths are from the **project root**.

---

## For new developers

| Step | Document | What you get |
|------|----------|--------------|
| **1. Setup from scratch** | [GETTING_STARTED.md](GETTING_STARTED.md) | Clone → environment → data → train → run API locally (step-by-step). |
| **2. Run the API locally** | [GETTING_STARTED.md#run-the-api](GETTING_STARTED.md#5-run-the-api) | Uvicorn, Docker, Docker Compose, or one-command Kubernetes (kind). |
| **3. Deploy to Render** | [DEPLOYMENT.md#render](DEPLOYMENT.md#rendercom-or-other-public-cloud) | Create Web Service, set `MODEL_URL`, deploy. |

**Recommended path:** [GETTING_STARTED.md](GETTING_STARTED.md) (full flow) → [DEPLOYMENT.md](DEPLOYMENT.md) (when you deploy to cloud or Kubernetes).

---

## Reference

| Document | Purpose |
|----------|---------|
| [GETTING_STARTED.md](GETTING_STARTED.md) | End-to-end setup: clone to local run (and optional deploy). |
| [DEPLOYMENT.md](DEPLOYMENT.md) | All deployment options: local Docker, Docker Compose, Kubernetes, CI/CD, **Render.com**, monitoring. |
| [API.md](API.md) | API reference: endpoints, request/response, examples. |
| [../k8s/README.md](../k8s/README.md) | Kubernetes-only: kind/minikube, GHCR image, one-command script. |

---

## Assignment & verification

| Document | Purpose |
|----------|---------|
| [../reports/MLOps_Assignment2_Report.md](../reports/MLOps_Assignment2_Report.md) | Assignment report (M1–M5). |
| [../VERIFICATION.md](../VERIFICATION.md) | Runtime verification checklist and evidence. |

---

## Quick links

- **I want to run the project locally** → [GETTING_STARTED.md](GETTING_STARTED.md)
- **I want to deploy to Render** → [DEPLOYMENT.md#render](DEPLOYMENT.md#rendercom-or-other-public-cloud)
- **I want to see the Grafana dashboard locally** → [DEPLOYMENT.md#monitoring-stack-prometheus--grafana](DEPLOYMENT.md#monitoring-stack-prometheus--grafana)
- **I want API details** → [API.md](API.md)
- **I use Kubernetes** → [../k8s/README.md](../k8s/README.md)
