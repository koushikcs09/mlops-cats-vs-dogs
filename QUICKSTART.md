# Quick Start: Cats vs Dogs API (Docker)

Run the inference API locally with Docker. For full step-by-step (venv, data, train), see **[RUN_STEPS.md](RUN_STEPS.md)**.

---

## Prerequisites

| Requirement | Notes |
|-------------|--------|
| **Docker** | Docker Desktop or Docker Engine |
| **Trained model** | Run training first so `models/model.pt` exists, or use a pre-built image that includes the model |

---

## Option A: Build and run locally (after training)

```bash
# From project root (after you have run train.py and models/model.pt exists)
cd /path/to/mlops-cats-vs-dogs

# Build image
docker build -t cats-vs-dogs-api:latest .

# Run container (mount model dir so container sees model.pt)
docker run -d --name cats-vs-dogs-api -p 8000:8000 \
  -v $(pwd)/models:/app/models:ro \
  cats-vs-dogs-api:latest
```

---

## Option B: Docker Compose

```bash
# Ensure models/model.pt exists, then:
docker compose up -d
# API will be at http://localhost:8000
```

---

## Test the API

| Endpoint | Command |
|----------|--------|
| **Health** | `curl http://localhost:8000/health` |
| **Metrics** | `curl http://localhost:8000/metrics` |
| **Predict** | `curl -X POST http://localhost:8000/predict -F "file=@path/to/cat-or-dog.jpg"` |

**Example:**
```bash
curl http://localhost:8000/health
# {"status":"ok","service":"cats-vs-dogs"}

curl -X POST http://localhost:8000/predict -F "file=@data/raw/PetImages/Cat/0.jpg"
# {"label":"cat","probabilities":{"cat":0.92,"dog":0.08}}
```

**Docs:** http://localhost:8000 (landing with links), http://localhost:8000/docs (Swagger), http://localhost:8000/redoc (ReDoc).

---

## Stop and cleanup

```bash
# Stop container
docker stop cats-vs-dogs-api
docker rm cats-vs-dogs-api

# If using Docker Compose
docker compose down
```

---

## One-liner (after training)

```bash
docker build -t cats-vs-dogs-api:latest . && \
docker run -d --name cats-vs-dogs-api -p 8000:8000 -v $(pwd)/models:/app/models:ro cats-vs-dogs-api:latest && \
echo "API at http://localhost:8000 - try: curl http://localhost:8000/health"
```

---

## Troubleshooting

**"Model not found"**  
Ensure `models/model.pt` exists (run `PYTHONPATH=. python scripts/train.py --epochs 3` first) and that you mounted the volume: `-v $(pwd)/models:/app/models:ro`.

**Port 8000 in use**  
Use another port: `docker run -d -p 8080:8000 ...` then use `http://localhost:8080`.

**Full run from scratch**  
See [RUN_STEPS.md](RUN_STEPS.md) for dataset download, prepare_data, train, then Docker.
