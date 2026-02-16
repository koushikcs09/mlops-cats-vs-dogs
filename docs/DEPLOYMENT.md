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

## Release workflow: upload model from CI

The **Release** workflow (`.github/workflows/release.yml`) trains the model in CI and uploads `model.pt` so you never have to commit it or upload it by hand.

### Trigger options

1. **Push a tag** (e.g. `v1.0.0`):
   - Runs: download data (kagglehub) → prepare splits → train (5 epochs) → create **GitHub Release** and attach `model.pt`.
   - Use the release asset URL as `MODEL_URL` on Render (e.g. `https://github.com/OWNER/REPO/releases/download/v1.0.0/model.pt`).
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Run manually** (Actions → Release → Run workflow):
   - You can choose epochs, whether to create a GitHub Release, and whether to upload to Artifactory.

### GitHub Release

After a tag push, open **Releases** in the repo; the new release will have `model.pt` as an asset. Copy the asset URL and set it as `MODEL_URL` in Render (or any app that supports `MODEL_URL`).

---

## Artifactory (JFrog)

You can store the model in **JFrog Artifactory** and point the app at it with `MODEL_URL`.

### 1. Create a generic repo in Artifactory

In your Artifactory instance, create a generic repository (e.g. `ml-models`) where you will store `model.pt`.

### 2. GitHub Secrets

In the repo: **Settings → Secrets and variables → Actions**. Add:

| Secret | Required | Description |
|--------|----------|-------------|
| `ARTIFACTORY_URL` | Yes | Base URL, e.g. `https://your-company.jfrog.io` (no trailing slash). |
| `ARTIFACTORY_REPO` | No | Repository name (default: `ml-models`). |
| `ARTIFACTORY_PATH` | No | Path inside the repo (default: `cats-vs-dogs/model.pt`). |
| **Auth (one of):** | | |
| `ARTIFACTORY_API_KEY` | Or | JFrog API key (preferred). |
| `ARTIFACTORY_USER` + `ARTIFACTORY_PASSWORD` | Or | Username and password. |

### 3. When the model is uploaded

- **On tag push:** If `ARTIFACTORY_URL` (and auth) are set, the Release workflow uploads `model.pt` to Artifactory after creating the GitHub Release.
- **On manual run:** Run the Release workflow, enable “Upload model to Artifactory”, and ensure the secrets above are set.

### 4. Download URL for the app

The URL your app will use (e.g. as `MODEL_URL` on Render) is:

```text
https://<ARTIFACTORY_URL>/artifactory/<ARTIFACTORY_REPO>/<ARTIFACTORY_PATH>
```

Example: `https://your-company.jfrog.io/artifactory/ml-models/cats-vs-dogs/model.pt`.  
If the repo is configured for anonymous read, that URL can be used directly. Otherwise use a token or dedicated user for read-only access and put the URL (with credentials if required) in `MODEL_URL` or use a signed/redirect URL if your Artifactory supports it.

---

## Kubernetes

Manifests are in **`k8s/`**: `deployment.yaml` (Deployment) and `service.yaml` (Service). See **[k8s/README.md](../k8s/README.md)** for full steps.

**Local (kind / minikube):**

```bash
docker build -t cats-vs-dogs-api:latest .
kind load docker-image cats-vs-dogs-api:latest   # or minikube: eval $(minikube docker-env) then build
kubectl apply -f k8s/
kubectl port-forward svc/cats-vs-dogs-api 8000:8000
```

**Cluster with GHCR image:** Set `image` in `k8s/deployment.yaml` to `ghcr.io/<owner>/mlops-cats-vs-dogs:main`, add an `imagePullSecret` for `ghcr.io`, then `kubectl apply -f k8s/`. Details in [k8s/README.md](../k8s/README.md).

---

## Render.com (or other public cloud)

The model file (`model.pt`) is not in the repo (it’s in `.gitignore`), so the container has no model unless you provide it.

**Option: download at startup (recommended for Render)**

1. **Host `model.pt` at a public URL**, e.g.:
   - **GitHub Release:** Create a release, attach `model.pt` as an asset, then use the “raw” or release asset URL (e.g. `https://github.com/OWNER/REPO/releases/download/v1.0/model.pt`).
   - **S3 / GCS / any HTTPS URL** that returns the file.

2. **In Render:** Open your Web Service → **Environment** → add:
   - **Key:** `MODEL_URL`  
   - **Value:** your public URL to `model.pt` (e.g. the GitHub Release asset URL).

3. **Redeploy.** On startup the app will download the model to `/app/models/model.pt` and then load it on first `/predict` (or at startup if `MODEL_URL` is set). If the URL is wrong or unreachable, startup logs will show the error.

**Optional:** To use a custom path after download, set `MODEL_PATH` (e.g. `/app/models/model.pt`). By default the app uses `/app/models/model.pt`.

---

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_URL` | (none) | If set and `model.pt` is missing, the app downloads the model from this URL at startup (e.g. for Render.com). |
| `MODEL_PATH` | `/app/models/model.pt` | Path to the model file. Only needed if you use a non-default path. |
| (otherwise) | - | For local/Docker: put `model.pt` in `models/` or mount a volume. |

---

## Monitoring stack (Prometheus + Grafana)

To run the API with Prometheus and Grafana for metrics and dashboards:

1. Build the API image and ensure `models/model.pt` exists (or use a placeholder for testing).
2. From project root:

   ```bash
   docker-compose -f monitoring/docker-compose-monitoring.yml up -d
   ```

3. **Grafana**: http://localhost:3000 (login: `admin` / `admin`). The **Cats vs Dogs API Dashboard** is auto-provisioned and shows:
   - Total predictions, total API requests, avg latency, model status, uptime
   - Time series for predictions and latency over time
4. **Prometheus**: http://localhost:9090 (scrapes `api:8000/metrics` every 10s).
5. **API**: http://localhost:8000 (same as standalone; `/metrics` returns Prometheus text format).

To stop: `docker-compose -f monitoring/docker-compose-monitoring.yml down`.

---

## Smoke test

After deployment (Docker or K8s), run:

```bash
bash scripts/smoke_test.sh http://<host>:<port>
```

Example for local Docker: `bash scripts/smoke_test.sh http://localhost:8000`
