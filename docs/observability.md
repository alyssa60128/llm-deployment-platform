# Observability

## Metrics

Prometheus scrapes:

```text
http://mock-inference:8000/metrics
```

## Some PromQL queries:

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

## Time zone

Application timestamps are emitted in UTC.

Grafana can display them in browser local time.

## Traces

The mock inference service uses OpenTelemetry to instrument incoming FastAPI
requests and custom inference operations.

Trace flow:

```text
Mock inference
→ OTLP
→ Grafana Alloy
→ Tempo
→ Grafana
```

Find inference traces with:
```text
{ name = "mock_inference.generate" }
```

The `/metrics` and `/healthz` endpoints are excluded from tracing to reduce
noise from frequent Prometheus scrapes and health checks.

Application logs include both `trace_id` and `span_id`.

Grafana supports:
* navigating from a Loki log entry to its Tempo trace
* opening a span and selecting Logs for this span to find related Loki logs

