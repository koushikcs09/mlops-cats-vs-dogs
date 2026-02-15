# Run the project step by step

Do everything from the **project root**:  
`/Users/skshahrukh.saba/MTECH/mlops-cats-vs-dogs`

---

## Step 1: Open terminal at project root

```bash
cd /Users/skshahrukh.saba/MTECH/mlops-cats-vs-dogs
```

---

## Step 2: Create and activate a virtual environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

You should see `(venv)` in your prompt.

---

## Step 3: Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 4: Get the dataset (choose one)

**Option A – You already have the zip (e.g. in Downloads):**
```bash
mkdir -p data/raw
unzip -o ~/Downloads/archive.zip -d data/raw
```

**Option B – Download with kagglehub (no Kaggle account):**
```bash
pip install kagglehub
python scripts/download_data.py
```

**Option C – Download with Kaggle CLI (need API key in ~/.kaggle/kaggle.json):**
```bash
pip install kaggle
export PATH="$HOME/Library/Python/3.9/bin:$PATH"   # macOS, if kaggle not on PATH
bash scripts/download_data.sh
```

Check that images exist under `data/raw` (e.g. `data/raw/PetImages/Cat/` and `data/raw/PetImages/Dog/`):
```bash
ls data/raw/PetImages/
```

---

## Step 5: Create train/val/test splits

```bash
PYTHONPATH=. python scripts/prepare_data.py
```

You should see something like: `Train: 19998, Val: 2499, Test: 2501` and `Splits written to data/processed/splits.json`.

---

## Step 6: Train the model

```bash
PYTHONPATH=. python scripts/train.py --epochs 3
```

- Training logs will print each epoch.
- Model is saved to `models/model.pt`.
- MLflow logs to `mlruns/` (params, metrics, confusion matrix, history).

To run a quick test with fewer epochs:
```bash
PYTHONPATH=. python scripts/train.py --epochs 2
```

---

## Step 7: Run the API locally

```bash
PYTHONPATH=. python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Leave this terminal open. You should see something like: `Uvicorn running on http://0.0.0.0:8000`.

---

## Step 8: Test the API (new terminal)

Open a **new** terminal, go to the project root, then:

**Health check:**
```bash
curl http://localhost:8000/health
```
Expected: `{"status":"ok","service":"cats-vs-dogs"}`

**Prediction (use any cat or dog image path):**
```bash
curl -X POST http://localhost:8000/predict -F "file=@data/raw/PetImages/Cat/0.jpg"
```
Expected: JSON with `"label"` and `"probabilities"`.

**Metrics:**
```bash
curl http://localhost:8000/metrics
```

When done testing, go back to the terminal where uvicorn is running and press **Ctrl+C** to stop the API.

---

## Step 9 (optional): Run unit tests

In the project root (with venv activated):

```bash
pytest tests/ -v
```

All 10 tests should pass.

---

## Step 10 (optional): Run with Docker

**Build the image (after Step 6 so `models/model.pt` exists):**
```bash
docker build -t cats-vs-dogs-api:latest .
```

**Run the container:**
```bash
docker run -p 8000:8000 -v $(pwd)/models:/app/models:ro cats-vs-dogs-api:latest
```

Test again with `curl http://localhost:8000/health` and the predict command from Step 8.

**Stop the container:**  
Find the container ID: `docker ps`  
Then: `docker stop <container_id>`

---

## Step 11 (optional): Smoke test script

If the API is running (either uvicorn or Docker) on port 8000:

```bash
bash scripts/smoke_test.sh http://localhost:8000
```

You should see: `Smoke tests passed.`

---

## Quick reference: minimal run (if data is already in data/raw)

```bash
cd /Users/skshahrukh.saba/MTECH/mlops-cats-vs-dogs
source venv/bin/activate
PYTHONPATH=. python scripts/prepare_data.py
PYTHONPATH=. python scripts/train.py --epochs 3
PYTHONPATH=. python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Then in another terminal: `curl http://localhost:8000/health`
