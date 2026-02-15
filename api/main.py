"""
FastAPI inference service: health check and prediction endpoints.
Includes request/response logging and basic metrics (M5).
Exposes /metrics in Prometheus text format for Grafana monitoring.
On cloud (e.g. Render): set MODEL_URL so the app downloads model.pt at startup if missing.
"""
import io
import os
import time
from pathlib import Path
from datetime import datetime
from urllib.request import urlretrieve

from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse
import numpy as np

# Lazy load model to avoid import-time path issues
_model = None
_REQUEST_COUNT = 0
_PREDICT_COUNT = 0
_LATENCIES = []  # simple in-app latency tracking (last N)
_STARTUP_TIME = datetime.now()

# Default path; overridden when MODEL_URL is used
MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
DEFAULT_MODEL_PATH = MODEL_DIR / "model.pt"


def _ensure_model_file() -> Path:
    """Return path to model.pt, downloading from MODEL_URL if missing and URL is set."""
    path = Path(os.environ.get("MODEL_PATH", str(DEFAULT_MODEL_PATH)))
    if path.exists():
        return path
    model_url = os.environ.get("MODEL_URL")
    if model_url:
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            urlretrieve(model_url, path)
            return path
        except Exception as e:
            raise RuntimeError(f"Failed to download model from MODEL_URL: {e}") from e
    raise FileNotFoundError(
        f"Model not found: {path}. "
        "Mount models/ or set MODEL_URL to a URL that serves model.pt (e.g. GitHub Release, S3)."
    )


def get_model():
    global _model
    if _model is None:
        from src.inference import load_model
        model_path = _ensure_model_file()
        _model = load_model(model_path)
    return _model


@asynccontextmanager
async def lifespan(app: FastAPI):
    """On startup: ensure model file exists (download from MODEL_URL if set) and preload model."""
    try:
        path = _ensure_model_file()
        print(f"[STARTUP] Model file ready: {path}", flush=True)
        # Preload model so first /predict does not block and we fail fast if load fails
        get_model()
        print("[STARTUP] Model loaded successfully.", flush=True)
    except Exception as e:
        print(f"[STARTUP] Model not available: {e}", flush=True)
        raise RuntimeError(
            "Model required at startup. Set MODEL_URL to a URL serving model.pt (e.g. GitHub Release), "
            "or build the Docker image with models/model.pt included."
        ) from e
    yield
    # shutdown: nothing to do


app = FastAPI(
    title="Cats vs Dogs API",
    version="1.0.0",
    description="Binary image classification (cat vs dog) for pet adoption platform.",
    docs_url="/docs",
    redoc_url=None,  # Disabled; assignment does not require it; use /docs (Swagger) for API docs
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(request, call_next):
    """Log request method/path and track latency (no sensitive data)."""
    global _REQUEST_COUNT, _LATENCIES
    start = time.perf_counter()
    response = await call_next(request)
    latency_ms = (time.perf_counter() - start) * 1000
    _REQUEST_COUNT += 1
    _LATENCIES.append(latency_ms)
    if len(_LATENCIES) > 1000:
        _LATENCIES.pop(0)
    # Log without body/headers to avoid sensitive data
    print(f"[LOG] {request.method} {request.url.path} status={response.status_code} latency_ms={latency_ms:.2f} request_count={_REQUEST_COUNT}")
    return response


@app.get("/", response_class=HTMLResponse)
def root():
    """Landing page with links to API docs."""
    return """
    <html>
    <head><title>Cats vs Dogs API</title></head>
    <body>
    <h1>Cats vs Dogs API</h1>
    <p>Binary image classification for pet adoption platform.</p>
    <ul>
    <li><a href="/docs">Swagger UI (/docs)</a></li>
    <li><a href="/openapi.json">OpenAPI schema (JSON)</a></li>
    <li><a href="/health">Health check</a></li>
    <li><a href="/metrics">Metrics (Prometheus)</a></li>
    </ul>
    </body>
    </html>
    """


@app.get("/health")
def health():
    """Health check endpoint for smoke tests and orchestration."""
    return {"status": "ok", "service": "cats-vs-dogs"}


@app.get("/metrics")
def metrics():
    """
    Prometheus-style metrics endpoint for scraping by Prometheus/Grafana.
    Returns text/plain with metric names compatible with the monitoring dashboard.
    """
    global _REQUEST_COUNT, _PREDICT_COUNT, _LATENCIES, _model, _STARTUP_TIME
    avg_latency = sum(_LATENCIES) / len(_LATENCIES) if _LATENCIES else 0
    uptime = (datetime.now() - _STARTUP_TIME).total_seconds()
    metrics_text = f"""# HELP app_info Application information
# TYPE app_info gauge
app_info{{version="1.0.0",service="cats-vs-dogs"}} 1

# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds gauge
app_uptime_seconds {uptime}

# HELP model_loaded Whether the model is loaded (1=yes, 0=no)
# TYPE model_loaded gauge
model_loaded {1 if _model is not None else 0}

# HELP predictions_total Total number of /predict requests
# TYPE predictions_total counter
predictions_total {_PREDICT_COUNT}

# HELP request_count_total Total API requests
# TYPE request_count_total counter
request_count_total {_REQUEST_COUNT}

# HELP prediction_latency_avg_ms Average request latency in milliseconds
# TYPE prediction_latency_avg_ms gauge
prediction_latency_avg_ms {avg_latency:.2f}
"""
    return PlainTextResponse(content=metrics_text, media_type="text/plain")


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Accept an image file; return class label and probabilities.
    """
    global _PREDICT_COUNT
    _PREDICT_COUNT += 1
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Expected an image file")
    contents = await file.read()
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(400, f"Invalid image: {e}")

    from src.inference import predict_proba
    from src.config import IMG_SIZE, CLASS_NAMES
    img = img.resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = np.transpose(arr, (2, 0, 1))[np.newaxis, ...]

    model = get_model()
    probs = predict_proba(model, arr)
    label = CLASS_NAMES[int(np.argmax(probs))]
    return {
        "label": label,
        "probabilities": {CLASS_NAMES[i]: round(probs[i], 4) for i in range(len(CLASS_NAMES))},
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
