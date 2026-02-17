# Getting Started: Clone to Run (and Deploy to Render)

This guide walks you from **cloning the repo** to **running the API locally**, and optionally **deploying to Render**. Run all commands from the **project root**.

---

## 1. Clone and enter the project

```bash
git clone https://github.com/YOUR_ORG/mlops-cats-vs-dogs.git
cd mlops-cats-vs-dogs
```

---

## 2. Create and activate a virtual environment

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` in your prompt.

---

## 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Get the dataset and prepare splits

**Option A – kagglehub (no API key):**
```bash
pip install kagglehub
python scripts/download_data.py
```

**Option B – Kaggle CLI (API key in `~/.kaggle/kaggle.json`):**
```bash
pip install kaggle
bash scripts/download_data.sh
```

**Option C – Local zip:**
```bash
mkdir -p data/raw
unzip -o ~/Downloads/archive.zip -d data/raw
```

Then create train/val/test splits:
```bash
PYTHONPATH=. python scripts/prepare_data.py
```
You should see something like: `Train: 19998, Val: 2499, Test: 2501`.

---

## 5. Train the model

```bash
PYTHONPATH=. python scripts/train.py --epochs 3
```

- Model is saved to `models/model.pt`.
- MLflow logs to `mlruns/` (optional: `mlflow ui --backend-store-uri ./mlruns`).

For a quicker run: `PYTHONPATH=. python scripts/train.py --fast` (2 epochs, 2000 samples).

---

## 6. Run the API locally

Choose one of the following.

### Option A – Uvicorn (no Docker)

```bash
PYTHONPATH=. python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Leave this terminal open. In another terminal:
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict -F "file=@data/raw/Cat/0.jpg"
```

### Option B – Docker

```bash
docker build -t cats-vs-dogs-api:latest .
docker run -p 8000:8000 -v $(pwd)/models:/app/models:ro cats-vs-dogs-api:latest
```

### Option C – Docker Compose

```bash
docker compose up -d
```

### Option D – Kubernetes (kind)

Requires [kind](https://kind.sigs.k8s.io/) and `kubectl`:

```bash
./scripts/deploy_k8s.sh
```

This creates a cluster (if needed), loads the image, deploys, and port-forwards. API at http://localhost:8000.

---

## 7. Test the API

| Action | Command |
|--------|---------|
| Health | `curl http://localhost:8000/health` |
| Predict | `curl -X POST http://localhost:8000/predict -F "file=@path/to/image.jpg"` |
| Docs | Open http://localhost:8000/docs |
| Smoke test | `bash scripts/smoke_test.sh http://localhost:8000` |

---

## 8. (Optional) Run tests

```bash
pytest tests/ -v
```

---

## 9. Deploy to Render

To run the API on [Render.com](https://render.com) (or similar):

1. **Host `model.pt` at a public URL**
   - Easiest: push a tag to trigger the **Release** workflow; it trains and attaches `model.pt` to a GitHub Release. Use the release asset URL (e.g. `https://github.com/OWNER/REPO/releases/download/v1.0.0/model.pt`).
   - Or upload `models/model.pt` to S3/GCS and use that URL.

2. **Create a Web Service on Render**
   - Connect your repo. Build: `docker build -t cats-vs-dogs-api .` (or use Render’s Dockerfile detection).
   - Add environment variable:
     - **Key:** `MODEL_URL`
     - **Value:** your public URL to `model.pt` (e.g. the GitHub Release asset URL above).

3. **Deploy**
   - Render builds and runs the container. On startup the app downloads the model from `MODEL_URL` and loads it. If the URL is wrong, startup logs will show an error.

Full deployment options (Docker, K8s, CI/CD, monitoring): [DEPLOYMENT.md](DEPLOYMENT.md).

---

## Summary

| Step | Command / action |
|------|-------------------|
| Clone | `git clone ... && cd mlops-cats-vs-dogs` |
| Env | `python3 -m venv venv && source venv/bin/activate` |
| Install | `pip install -r requirements.txt` |
| Data | `python scripts/download_data.py` (or Kaggle CLI / unzip) |
| Splits | `PYTHONPATH=. python scripts/prepare_data.py` |
| Train | `PYTHONPATH=. python scripts/train.py --epochs 3` |
| Run | Uvicorn, Docker, Compose, or `./scripts/deploy_k8s.sh` |
| Deploy to Render | Set `MODEL_URL` to a public `model.pt` URL; see [DEPLOYMENT.md](DEPLOYMENT.md). |
