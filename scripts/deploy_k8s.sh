#!/usr/bin/env bash
# Build Docker image, (optionally) create kind cluster, load image, deploy to Kubernetes, port-forward.
# Usage: ./scripts/deploy_k8s.sh [--no-build] [--no-port-forward]
set -e
cd "$(dirname "$0")/.."
CLUSTER_NAME="${KIND_CLUSTER_NAME:-cats-vs-dogs}"
IMAGE_NAME="cats-vs-dogs-api:latest"

# Build image unless --no-build
if [[ "$1" != "--no-build" ]]; then
  echo ">>> Building Docker image: $IMAGE_NAME"
  docker build -t "$IMAGE_NAME" .
fi
[[ "$1" == "--no-build" ]] && shift

# Create kind cluster if not present
if ! kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
  echo ">>> Creating kind cluster: $CLUSTER_NAME"
  kind create cluster --name "$CLUSTER_NAME"
fi

# Use kind context
kubectl config use-context "kind-${CLUSTER_NAME}"

# Load image into kind
echo ">>> Loading image into kind cluster"
kind load docker-image "$IMAGE_NAME" --name "$CLUSTER_NAME"

# Deploy
echo ">>> Applying k8s manifests"
kubectl apply -f k8s/

# Wait for deployment
echo ">>> Waiting for deployment to be ready"
kubectl rollout status deployment/cats-vs-dogs-api -n default --timeout=120s

# Port-forward unless --no-port-forward
if [[ "$1" != "--no-port-forward" ]]; then
  echo ">>> Port-forwarding svc/cats-vs-dogs-api 8000:8000 (Ctrl+C to stop)"
  kubectl port-forward svc/cats-vs-dogs-api 8000:8000
fi
