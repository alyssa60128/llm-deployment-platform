# Local Development

## Start the complete stack (RECOMMENDED)
```bash
docker compose up --build -d
docker compose ps
docker compose down
# Do not use `docker compose down -v` if you want to preserve local Grafana and Prometheus data.
```

## Python environment
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r services/mock_inference/requirements-dev.txt
python -m pip install -r services/control_plane/requirements-dev.txt
```

## Start the application directly
```bash
uvicorn services.mock_inference.app.main:app --reload
uvicorn services.control_plane.app.main:app --reload
```

## Useful check

```bash
python -m pytest services/mock_inference/tests services/control_plane/tests -v
docker compose config --quiet
docker compose up --build -d
curl http://127.0.0.1:8080/healthz
curl http://127.0.0.1:8000/healthz
```

### Send a test request for mock inference

```bash
curl -X POST \
  http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: readme-test-001" \
  -d '{
    "model": "model-a",
    "messages": [
      {
        "role": "user",
        "content": "Hello from the README"
      }
    ]
  }'
```

### Create a deployment in control plane

```bash
curl -s -X POST \
  http://127.0.0.1:8080/api/v1/deployments \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "llama-3.2-1b"
  }'
```

### Send a chat request through the deployment in control plane

```bash
curl -s -X POST \
  http://127.0.0.1:8080/api/v1/deployments/<deployment_id>/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: mvp-test-001" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Hello from the MVP control plane"
      }
    ]
  }'
```