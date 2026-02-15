# MLOps Assignment 2 - Cats vs Dogs inference service
FROM python:3.11-slim

WORKDIR /app

# Install dependencies with pinned versions
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY src/ ./src/
COPY api/ ./api/
COPY models/ ./models/

# Default: run API (models must be present in models/)
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
