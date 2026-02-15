# Cats vs Dogs – API Documentation

Base URL (local): `http://localhost:8000`

**Docs:** [Swagger UI](/docs) · [OpenAPI JSON](/openapi.json)

---

## Endpoints

### GET /

Landing page (HTML) with links to API docs, health, and OpenAPI schema.

**Example:** Open http://localhost:8000 in a browser.

---

### GET /health

Health check for smoke tests and orchestration (e.g. Docker, Kubernetes).

**Response:** `200 OK`

```json
{
  "status": "ok",
  "service": "cats-vs-dogs"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### POST /predict

Accepts an image file and returns the predicted class (cat or dog) and class probabilities.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body:** One file field named `file` (image: JPEG, PNG, etc.)

**Response:** `200 OK`

```json
{
  "label": "cat",
  "probabilities": {
    "cat": 0.92,
    "dog": 0.08
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/predict -F "file=@/path/to/image.jpg"
```

**Errors:**
- `400` – Missing or invalid image (e.g. not an image file).

---

### GET /metrics

Returns basic in-app metrics: request count and latency.

**Response:** `200 OK`

```json
{
  "request_count": 42,
  "latency_ms_avg": 15.3,
  "latency_ms_recent": [12.1, 18.5, ...]
}
```

**Example:**
```bash
curl http://localhost:8000/metrics
```

---

## OpenAPI & docs

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Landing page with links |
| http://localhost:8000/docs | Swagger UI (interactive) |
| http://localhost:8000/openapi.json | OpenAPI 3.0 schema (JSON) |
