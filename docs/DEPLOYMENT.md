# Cats vs Dogs – Deployment Guide

This document describes how to run and deploy the Cats vs Dogs inference API.

---

## Local run (no Docker)

1. Install dependencies: `pip install -r requirements.txt`
2. Ensure `models/model.pt` exists (run training first).
3. From project root:
   ```bash
   PYTHONPATH=. python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```
4. API: http://localhost:8000

---

## Docker

**Build:**
```bash
docker build -t cats-vs-dogs-api:latest .
```

**Run (mount model directory):**
```bash
docker run -d -p 8000:8000 --name cats-vs-dogs-api \
  -v $(pwd)/models:/app/models:ro \
  cats-vs-dogs-api:latest
```

**Verify:**
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict -F "file=@path/to/image.jpg"
```

---

## Docker Compose

From project root:

```bash
docker compose up -d
```

Service runs on port **8000**. Ensure `models/model.pt` exists (or place it in `models/` before `docker compose up`).  
To run smoke tests: `bash scripts/smoke_test.sh http://localhost:8000`.

---

## CI/CD (GitHub Actions)

- **CI** (`.github/workflows/ci.yml`): On push/PR – runs tests, builds Docker image, pushes to **GitHub Container Registry** (ghcr.io) when not a PR.
- **CD** (`.github/workflows/cd.yml`): After CI completes on `main` – pulls the image from the registry, runs the container, runs smoke tests. Pipeline fails if smoke tests fail.

**Registry image:** `ghcr.io/<owner>/<repo>:<branch>` (e.g. `ghcr.io/username/mlops-cats-vs-dogs:main`).

---

## Kubernetes (optional)

For a Kubernetes deployment (e.g. kind, minikube, or cloud), you can add:

- A **Deployment** (replicas, image from GHCR, resource limits, liveness/readiness on `/health`).
- A **Service** (e.g. LoadBalancer or ClusterIP).

Example image for the deployment:

```yaml
image: ghcr.io/<owner>/mlops-cats-vs-dogs:main
```

Model can be provided via a volume (e.g. PVC or ConfigMap for small artifacts) or baked into the image at build time.

---

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| (none required) | - | Model path is fixed as `models/model.pt` inside the container; mount `./models` or bake model into image. |

---

## Smoke test

After deployment (Docker or K8s), run:

```bash
bash scripts/smoke_test.sh http://<host>:<port>
```

Example for local Docker: `bash scripts/smoke_test.sh http://localhost:8000`
