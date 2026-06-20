# Local Development

## Python environment
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r services/mock_inference/requirements-dev.txt
```

## Start the application directly
```bash
uvicorn services.mock_inference.app.main:app --reload
```

## Start the complete stack

```bash
docker compose up --build -d
docker compose ps

docker compose logs mock-inference
docker compose logs alloy
docker compose logs loki

docker compose down
# Named volumes are preserved unless -v is used.
```

## Useful check

```bash
python -m pytest services/mock_inference/tests -v
docker compose config --quiet
docker compose up --build -d
curl http://127.0.0.1:8000/healthz
```