# Architecture

## Overview

The project currently consists of a control-plane service, a shared mock inference runtime, and a local observability stack.

The control plane provides platform APIs for resource inspection, model catalog lookup, deployment planning, and deployment-scoped chat requests.

The mock inference runtime simulates a vLLM-compatible OpenAI-style inference server. The model output and performance characteristics are simulated, while the APIs, containers, CI pipeline, metrics, logs, traces, and telemetry collection path use real engineering components.

## Service Responsibilities

| Service          | Responsibility                                                                          |
| ---------------- | --------------------------------------------------------------------------------------- |
| `control-plane`  | Management API for resources, models, deployments, and deployment-scoped proxy requests |
| `mock-inference` | Shared simulated inference runtime with OpenAI-style API and vLLM-style metrics         |
| `prometheus`     | Metrics scraping and querying                                                           |
| `grafana`        | Metrics, logs, and traces exploration                                                   |
| `loki`           | Log storage                                                                             |
| `tempo`          | Trace storage                                                                           |
| `alloy`          | Docker log collection and OTLP trace forwarding                                         |

## MVP Request Flow

```text
Client
  |
  | POST /api/v1/deployments/{id}/chat/completions
  v
Control Plane
  |
  |-- Validate deployment exists
  |-- Ensure deployment is RUNNING
  |-- Inject served model name
  |-- Proxy request to runtime
  v
Mock Inference Runtime
  |
  |-- Validate chat request
  |-- Simulate token counts and inference latency
  |-- Record Prometheus metrics
  |-- Emit structured JSON logs
  |-- Emit OpenTelemetry traces
  `-- Return OpenAI-style response
```

## Deployment Model

Version 1 does not create one runtime container per deployment.

Instead, all mock deployments share one `mock-inference` runtime service. The control plane stores deployment records and proxies deployment-scoped chat requests to the shared runtime.

```text
POST /api/v1/deployments
  → create deployment record
  → attach model catalog entry
  → generate V1 resource plan
  → mark deployment RUNNING

POST /api/v1/deployments/{id}/chat/completions
  → validate deployment
  → inject served model name
  → proxy to mock-inference
```

A future version may use the Docker socket, Kubernetes API, or another runtime adapter to create one runtime container or workload per deployment.

## Resource Planning

The control plane exposes a resource summary API:

```text
GET /api/v1/resources
```

The current implementation detects:

* CPU logical cores
* total and available memory
* GPU availability through `nvidia-smi`
* total GPU memory
* largest single-device GPU memory

The deployment planner estimates model weight memory using:

```text
parameters_billion × bytes_per_parameter × 1,000,000,000
```

It then applies a simple safety factor to estimate recommended VRAM.

This is a V1 heuristic. It is not a full vLLM memory planner and does not account for all runtime memory such as KV cache, CUDA overhead, fragmentation, batching, or temporary buffers.

## Model Catalog

The model catalog is static in Version 1.

It stores vLLM-oriented fields that are useful for future runtime startup and deployment planning:

* model catalog ID
* Hugging Face model ID
* served model name
* source URL
* parameter count
* bytes per parameter estimate
* Hugging Face token requirement
* default vLLM options such as dtype, quantization, max model length, GPU memory utilization, tensor parallel size, and pipeline parallel size

The current catalog includes small models selected for future local GPU experiments:

* `meta-llama/Llama-3.2-1B`
* `AMead10/Llama-3.2-3B-Instruct-AWQ`

## Metrics Flow

```text
Mock inference
  |
  | GET /metrics
  v
Prometheus
  |
  v
Grafana
```

Prometheus uses the Docker Compose service name `mock-inference` to scrape the runtime inside the Compose network.

## Logging Flow

```text
Mock inference stdout
  |
  v
Docker container logs
  |
  v
Grafana Alloy
  |
  v
Loki
  |
  v
Grafana Explore
```

Request IDs and trace IDs remain JSON fields instead of Loki stream labels to avoid high label cardinality.

## Tracing Flow

```text
Mock inference
  |
  v
OpenTelemetry SDK
  |
  | OTLP gRPC
  v
Grafana Alloy
  |
  v
Tempo
  |
  v
Grafana
```

The `/metrics` and `/healthz` endpoints are excluded from tracing to reduce noise from Prometheus scrapes and health checks.

## Delivery Flow

```text
Feature branch
  |
  v
Pull request
  |-- pytest
  |-- Compose validation
  |-- mock-inference Docker build
  `-- control-plane Docker build
  |
  v
Merge to main
  |
  `-- Publish mock-inference image to GHCR
```

Pull requests do not publish images. Publishing requires package write permission and only occurs after changes are accepted into the main branch.

The control-plane image is currently build-validated in CI but is not yet published to GHCR.