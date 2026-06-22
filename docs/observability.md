# Observability

## Metrics

The mock inference runtime exports selected vLLM-compatible Prometheus metrics, including:

* Running requests
* Successful requests
* Prompt tokens
* Generation tokens
* Time to first token
* Time per output token
* End-to-end request latency

When requests are sent through the control plane, metrics are grouped by the deployed model name, such as `llama-3.2-1b`.

The generated values are synthetic and are intended to exercise the monitoring pipeline.

### Prometheus scrapes:

```text
http://mock-inference:8000/metrics
```

### Some PromQL queries:

```text
vllm:request_success_total

rate(vllm:generation_tokens_total[1m])

histogram_quantile(
  0.95,
  sum by (le, model_name) (
    rate(vllm:time_to_first_token_seconds_bucket[5m])
  )
)
```

## Logs

The mock inference runtime writes one-line JSON logs to stdout.

Request logs include:

* Request ID
* Trace ID and span ID
* HTTP method and path
* Status code
* Request duration

Inference logs include:

* Model name
* Prompt and generation token counts
* TTFT and TPOT
* End-to-end latency
* Finish reason

Grafana Alloy discovers Docker container logs and forwards them to Loki.

## Some Grafana Loki datasource query:

```text
{service_name="mock-inference"} | json

{service_name="mock-inference"}
| json
| request_id="loki-test-001"

{service_name="mock-inference"}
| json
| event="inference.completed"
```

## Traces

The mock inference runtime uses OpenTelemetry to emit traces through Grafana Alloy to Tempo.

Grafana supports:

* navigating from a Loki log entry to its Tempo trace
* opening a Tempo span and selecting logs for that span
* correlating request IDs, trace IDs, model names, and deployment-scoped traffic

### Trace flow:

```text
Mock inference
→ OTLP
→ Grafana Alloy
→ Tempo
→ Grafana
```

### Find inference traces with:
```text
{ name = "mock_inference.generate" }
```

The `/metrics` and `/healthz` endpoints are excluded from tracing to reduce
noise from frequent Prometheus scrapes and health checks.

Application logs include both `trace_id` and `span_id`.


## How to start with MVP Request Path

A deployment-scoped chat request flows through both services:

```text
Client
→ control-plane
→ mock-inference (shared)
→ Prometheus / Loki / Tempo
```
When requests are sent through the control plane, metrics are grouped by the
deployment model name, such as llama-3.2-1b.

In Grafana dashboards, select the deployed model name from the model_name
filter.

1. Create deployment：

```bash
DEPLOYMENT_ID=$(
  curl -s -X POST \
    http://127.0.0.1:8080/api/v1/deployments \
    -H "Content-Type: application/json" \
    -d '{
      "model_id": "llama-3.2-1b"
    }' \
  | python -c "import sys,json; print(json.load(sys.stdin)['id'])"
)

echo $DEPLOYMENT_ID
```

2. Use control-plane proxy to call mock-inference：

```bash
curl -s -X POST \
  "http://127.0.0.1:8080/api/v1/deployments/${DEPLOYMENT_ID}/chat/completions" \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: mvp-test-001" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Hello from the MVP control plane"
      }
    ]
  }' | python -m json.tool
```

3. Check record

```text
Loki:
{service_name="mock-inference"} | json | request_id="mvp-test-001"

Tempo:
{ name = "mock_inference.generate" }

Prometheus/Grafana:
model_name = llama-3.2-1b
```

## Time zone

Application timestamps are emitted in UTC.

Grafana can display them in browser local time.