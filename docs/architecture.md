# Architecture

## Overview

The project currently consists of a simulated inference workload and a local observability stack.

The model output and performance characteristics are simulated, while the API, metrics, logs, containers, CI pipeline, and telemetry collection path use real engineering components.

## Application Flow

```text
Client
  |
  | POST /v1/chat/completions
  v
FastAPI mock inference service
  |
  |-- Validate request with Pydantic
  |-- Generate or propagate request ID
  |-- Simulate token counts and inference latency
  |-- Record Prometheus metrics
  |-- Emit structured JSON logs
  `-- Return an OpenAI-style response
```

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

Prometheus uses the Docker Compose service name `mock-inference` to scrape the application inside the Compose network.

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

Request IDs remain JSON fields instead of Loki stream labels to avoid high label cardinality.

## Tracing Flow

```text
Mock inference
→ OpenTelemetry SDK
→ OTLP gRPC
→ Grafana Alloy
→ Tempo
→ Grafana
```

## Delivery Flow

```text
Feature branch
  |
  v
Pull request
  |-- pytest
  |-- Compose validation
  `-- Docker build
  |
  v
Merge to main
  |
  `-- Publish commit-tagged image to GHCR
```

Pull requests do not publish images. Publishing requires package write permission and only occurs after changes are accepted into the main branch.

## MVP Runtime Model

Version 1 does not create one runtime container per deployment.

Instead, all mock deployments share one `mock-inference` runtime service.
The control plane stores deployment records and proxies deployment-scoped chat
requests to the shared runtime.

```text
POST /api/v1/deployments
  → create deployment record

POST /api/v1/deployments/{id}/chat/completions
  → validate deployment
  → inject served model name
  → proxy to mock-inference
```