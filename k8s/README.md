# Kubernetes deployment (M4)

Deploy the Cats vs Dogs API to a local Kubernetes cluster (kind, minikube, microk8s) or any K8s cluster.

## Prerequisites

- `kubectl` installed
- A cluster: [kind](https://kind.sigs.k8s.io/), [minikube](https://minikube.sigs.k8s.io/), or [microk8s](https://microk8s.io/)

## Local cluster (kind / minikube)

1. **Build and load the image** (so the cluster can pull it):

   **kind:**
   ```bash
   docker build -t cats-vs-dogs-api:latest .
   kind load docker-image cats-vs-dogs-api:latest
   ```

   **minikube:**
   ```bash
   eval $(minikube docker-env)
   docker build -t cats-vs-dogs-api:latest .
   ```

2. **Apply manifests:**
   ```bash
   kubectl apply -f k8s/
   ```

3. **Expose and test:**
   ```bash
   kubectl port-forward svc/cats-vs-dogs-api 8000:8000
   curl http://localhost:8000/health
   curl -X POST http://localhost:8000/predict -F "file=@/path/to/cat.jpg"
   ```

## Cluster using GHCR image

1. Create a pull secret (replace `YOUR_ORG` with your GitHub org/user):
   ```bash
   kubectl create secret docker-registry ghcr-secret \
     --docker-server=ghcr.io \
     --docker-username=YOUR_GITHUB_USER \
     --docker-password=YOUR_GITHUB_PAT \
     --docker-email=your@email.com
   ```

2. Edit `deployment.yaml`: set `image` to `ghcr.io/YOUR_ORG/mlops-cats-vs-dogs:main` and add under `spec.template.spec`:
   ```yaml
   imagePullSecrets:
     - name: ghcr-secret
   ```

3. Apply and port-forward (or use LoadBalancer/Ingress):
   ```bash
   kubectl apply -f k8s/
   kubectl port-forward svc/cats-vs-dogs-api 8000:8000
   ```

## Smoke test

After deployment, from the project root:
```bash
kubectl port-forward svc/cats-vs-dogs-api 8000:8000 &
./scripts/smoke_test.sh http://localhost:8000
```
