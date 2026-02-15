"""
FastAPI inference service: health check and prediction endpoints.
Includes request/response logging and basic metrics (M5).
"""
import io
import time
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
import numpy as np

# Lazy load model to avoid import-time path issues
_model = None
_REQUEST_COUNT = 0
_LATENCIES = []  # simple in-app latency tracking (last N)


def get_model():
    global _model
    if _model is None:
        from src.inference import load_model
        model_path = Path(__file__).resolve().parent.parent / "models" / "model.pt"
        _model = load_model(model_path)
    return _model


app = FastAPI(
    title="Cats vs Dogs API",
    version="1.0.0",
    description="Binary image classification (cat vs dog) for pet adoption platform.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
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
    <li><a href="/redoc">ReDoc (/redoc)</a></li>
    <li><a href="/openapi.json">OpenAPI schema (JSON)</a></li>
    <li><a href="/health">Health check</a></li>
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
    """Basic metrics: request count and latency (in-app)."""
    global _REQUEST_COUNT, _LATENCIES
    avg_latency = sum(_LATENCIES) / len(_LATENCIES) if _LATENCIES else 0
    return {
        "request_count": _REQUEST_COUNT,
        "latency_ms_avg": round(avg_latency, 2),
        "latency_ms_recent": _LATENCIES[-10:] if _LATENCIES else [],
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Accept an image file; return class label and probabilities.
    """
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
