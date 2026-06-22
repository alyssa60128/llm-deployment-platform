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
* A control-plane API for resources, model catalog, deployment planning, and deployment-scoped inference requests
* A shared mock inference runtime that simulates a vLLM-compatible OpenAI-style API
* Prometheus metrics compatible with selected vLLM metric names
* Structured JSON logging
* OpenTelemetry tracing
* Centralized log collection with Grafana Alloy and Loki
* Trace storage with Tempo
* Visualization and exploration with Grafana

## Architecture

```text
Client
  |
  | Create deployment / send deployment-scoped chat request
  v
Control Plane API
  |
  | Validate deployment
  | Inject served model name
  | Proxy chat request
  v
Shared Mock Inference Runtime
  |-- Prometheus metrics --> Prometheus --> Grafana
  |
  |-- JSON stdout logs --> Grafana Alloy --> Loki --> Grafana
  |
  `-- OTLP traces --> Grafana Alloy --> Tempo --> Grafana

GitHub Pull Request
  |
  |-- pytest
  |-- Docker Compose validation
  `-- Docker image build validation

Merge to main
  |
  `-- Build and publish mock-inference image to GHCR
```

## Services

| Service        | Purpose                                                                                             | Local URL              |
| -------------- | --------------------------------------------------------------------------------------------------- | ---------------------- |
| Control Plane  | FastAPI API for resources, model catalog, deployment planning, and deployment-scoped proxy requests | http://localhost:8080  |
| Mock Inference | FastAPI-based simulated vLLM-compatible inference runtime                                           | http://localhost:8000  |
| Prometheus     | Metrics collection and querying                                                                     | http://localhost:9090  |
| Grafana        | Metrics, logs, and traces exploration                                                               | http://localhost:3000  |
| Loki           | Centralized log storage                                                                             | http://localhost:3100  |
| Tempo          | Trace storage                                                                                       | http://localhost:3200  |
| Grafana Alloy  | Docker log collection and OTLP trace forwarding                                                     | http://localhost:12345 |

## API Endpoints

### Control Plane

```http
GET /healthz
GET /api/v1/resources
GET /api/v1/models
POST /api/v1/deployments
GET /api/v1/deployments
GET /api/v1/deployments/{deployment_id}
DELETE /api/v1/deployments/{deployment_id}
POST /api/v1/deployments/{deployment_id}/chat/completions
```

### Mock Inference Runtime

```http
GET /healthz
POST /v1/chat/completions
GET /metrics
```

The recommended MVP path is to call chat completions through the control plane:

```text
POST /api/v1/deployments/{deployment_id}/chat/completions
```

The direct mock inference endpoint remains available for local testing:

```text
POST /v1/chat/completions
```

## MVP Deployment Flow

Version 1 uses a shared mock inference runtime.

The control plane creates deployment records and proxies deployment-scoped chat requests to the shared `mock-inference` service. The request body does not accept a `model` field; the control plane injects the deployed model name based on the deployment record.

```text
Client
→ control-plane
→ deployment record
→ shared mock-inference runtime
→ metrics / logs / traces
```

## Local Development

See [`docs/local-development.md`](docs/local-development.md).

## Observability

See [`docs/observability.md`](docs/observability.md).

## Current Limitations

* No real GPU inference
* No real Hugging Face model download
* No real vLLM runtime
* No Kubernetes deployment
* No AWS infrastructure
* Control-plane deployment state is stored in memory
* Version 1 uses one shared mock inference runtime instead of one runtime container per deployment
* Grafana dashboard JSON is currently maintained privately and imported manually
* Token counts, latency, and selected runtime metrics are simulated

## Planned Work

See [`docs/roadmap.md`](docs/roadmap.md).

## CI/CD

Pull requests targeting `main` automatically run:

* Python dependency installation
* pytest
* Docker Compose configuration validation
* Docker image build validation

After changes are merged into `main`, GitHub Actions also publishes the container image to GitHub Container Registry.

The GHCR package is currently private while the first project version is under development.