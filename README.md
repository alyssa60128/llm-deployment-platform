# LLM Deployment and Observability Platform

A learning-oriented platform for simulating LLM inference workloads and practicing backend development, container delivery, CI/CD, and observability.

The current version uses a mock inference service instead of a real GPU-backed vLLM runtime. The API, container workflow, metrics, logs, CI pipeline, and observability infrastructure are real; only the model inference behavior and generated telemetry values are simulated.

## Current Goals

This project is designed to demonstrate and practice:

* FastAPI backend development
* Request and response validation with Pydantic
* Automated testing with pytest
* Docker image creation
* GitHub Actions CI
* Container publishing to GitHub Container Registry
* Prometheus metrics compatible with selected vLLM metric names
* Structured JSON logging
* Centralized log collection with Grafana Alloy and Loki
* Visualization and exploration with Grafana

## Architecture

```text
Client
  |
  v
Mock Inference API
  |-- Prometheus metrics --> Prometheus --> Grafana
  |
  `-- JSON stdout logs --> Grafana Alloy --> Loki --> Grafana

GitHub Pull Request
  |
  |-- pytest
  `-- Docker image build

Merge to main
  |
  `-- Build and publish image to GHCR
```

## Services

| Service        | Purpose                                   | Local URL              |
| -------------- | ----------------------------------------- | ---------------------- |
| Mock Inference | FastAPI-based simulated LLM inference API | http://localhost:8000  |
| Prometheus     | Metrics collection and querying           | http://localhost:9090  |
| Grafana        | Metrics and log exploration               | http://localhost:3000  |
| Loki           | Centralized log storage                   | http://localhost:3100  |
| Grafana Alloy  | Docker log discovery and forwarding       | http://localhost:12345 |

## API Endpoints

### Health check

```http
GET /healthz
```

### Mock chat completion

```http
POST /v1/chat/completions
```

Example request:

```json
{
  "model": "model-a",
  "messages": [
    {
      "role": "user",
      "content": "Explain container observability"
    }
  ]
}
```

### Prometheus metrics

```http
GET /metrics
```

## Observability

### Metrics

The mock inference service exports selected vLLM-compatible Prometheus metrics, including:

* Running requests
* Successful requests
* Prompt tokens
* Generation tokens
* Time to first token
* Time per output token
* End-to-end request latency

The generated values are synthetic and are intended to exercise the monitoring pipeline.

### Logs

The application writes one-line JSON logs to stdout.

Request logs include:

* Request ID
* HTTP method and path
* Status code
* Request duration

Inference logs include:

* Model name
* Prompt and generation token counts
* TTFT and TPOT
* End-to-end latency
* Finish reason

Grafana Alloy discovers the Docker container, reads its logs, and forwards them to Loki.

### Traces

* OpenTelemetry tracing
* Tempo trace storage
* Log-to-trace and trace-to-log correlation

## Local Development

### Requirements

* Docker Desktop with WSL 2 integration
* Docker Compose
* Python 3.12
* Git

### Run with Docker Compose

```bash
docker compose up --build -d
```

Check service status:

```bash
docker compose ps
```

Stop services without deleting stored data:

```bash
docker compose down
```

Do not use `docker compose down -v` if you want to preserve local Grafana and Prometheus data.

### Send a test request

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

### Run tests

```bash
python -m pytest services/mock_inference/tests -v
```

### Validate Docker Compose

```bash
docker compose config --quiet
```

## CI/CD

Pull requests targeting `main` automatically run:

* Python dependency installation
* pytest
* Docker Compose configuration validation
* Docker image build validation

After changes are merged into `main`, GitHub Actions also publishes the container image to GitHub Container Registry.

The GHCR package is currently private while the first project version is under development.

## Current Limitations

* No real GPU inference
* No real Hugging Face model download
* No vLLM runtime
* No Kubernetes deployment
* No AWS infrastructure
* No distributed tracing yet
* Grafana dashboard JSON is currently maintained privately and imported manually
* Token counts and inference latency are simulated

## Planned Work

### Version 1

* OpenTelemetry traces
* Tempo integration
* FastAPI control plane
* Server resource inspection
* Static model catalog
* Mock deployment lifecycle
* Improved integration tests and documentation

### Version 2

* Kubernetes and Helm
* Terraform
* AWS deployment
* Real GPU-backed vLLM runtime
* Improved and publishable Grafana dashboards
