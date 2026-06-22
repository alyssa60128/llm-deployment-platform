# Roadmap

This document tracks planned improvements after the Version 1 MVP.

## Version 1 MVP Status

Version 1 focuses on building a local LLM deployment platform skeleton with real platform and observability workflows, while keeping the inference runtime simulated.

Completed MVP capabilities:

* FastAPI mock inference runtime
* OpenAI-style chat completion API
* vLLM-style Prometheus metrics
* Structured JSON logs
* OpenTelemetry traces
* Prometheus, Loki, Tempo, Grafana, and Grafana Alloy
* Log-to-trace and trace-to-log correlation
* Control-plane API
* Resource summary API with GPU VRAM detection
* Static vLLM-oriented model catalog
* Mock deployment planning
* Deployment-scoped chat completion proxy
* Docker Compose local platform
* GitHub Actions CI with tests and container build validation

## Version 1.1: Dashboard and Observability Polish

### Publishable Mock Runtime Dashboard

The current Grafana dashboard is manually imported and maintained privately.

Planned work:

* create a cleaned dashboard that can be safely committed to the repository
* align dashboard variables with current metric labels, especially `model_name`
* add panels for request rate, success count, token throughput, TTFT, TPOT, and end-to-end latency
* add panels for active and waiting requests
* add panels for simulated cache and runtime metrics that resemble vLLM dashboards
* document which metrics are real platform signals and which are synthetic simulation signals

Some vLLM dashboard fields may not exist in the mock runtime yet. For local learning purposes, the mock service may generate synthetic values for fields such as:

* GPU KV cache usage
* CPU KV cache usage
* prefix cache hit rate
* queue depth
* prefill throughput
* decode throughput

These should be clearly documented as simulated metrics.

### Logs and Traces Dashboards

Currently logs and traces are explored manually through Grafana Explore.

Planned work:

* create dashboard panels that show recent request logs
* create panels filtered by request ID, trace ID, model name, and deployment ID
* add links from dashboard panels to Loki Explore and Tempo traces
* visualize request latency using both metrics and traces
* show example queries for debugging a single request across metrics, logs, and traces

### Control-Plane Observability

The mock inference runtime currently has the richest observability.

The control plane should also expose the three observability pillars:

* Prometheus metrics
* structured JSON logs
* OpenTelemetry traces

This becomes especially important when the mock runtime is replaced with real vLLM.

Real vLLM will provide its own metrics, but application-level management actions such as deployment creation, resource planning, proxy behavior, validation failures, and runtime routing should be observable at the control-plane level.

Potential control-plane metrics:

* deployment creation count
* deployment deletion count
* deployment status count
* proxy request count
* proxy request latency
* runtime error count
* planner runnable / not-runnable decisions
* model catalog selection count

Potential control-plane logs:

* deployment.created
* deployment.deleted
* deployment.proxy.started
* deployment.proxy.completed
* deployment.proxy.failed
* deployment.plan.generated

Potential control-plane spans:

* control_plane.create_deployment
* control_plane.generate_plan
* control_plane.proxy_chat_completion
* control_plane.call_runtime

## Version 1.2: Proxy Layer Improvements

The deployment-scoped proxy is a valuable area for side-project practice.

Potential improvements:

### Request Routing

* route requests by deployment ID
* inject served model name
* prevent users from overriding deployment-bound model names
* attach deployment ID and model ID to logs and traces
* forward request IDs to runtime services

### Error Handling

* return clear errors when deployment is not running
* classify runtime timeout, connection failure, and bad response errors
* add retry policy for safe failure modes
* expose runtime error metrics

### Timeouts and Limits

* configure runtime request timeout
* reject overly large request bodies
* limit message count or message length
* add per-deployment rate limiting
* add concurrency limits per deployment

### Streaming Support

Future work may add streaming proxy support for OpenAI-compatible chat completions.

This would exercise:

* streaming HTTP responses
* cancellation handling
* timeout behavior
* trace spans for long-running streams
* partial output logging policy

### Auth and Multi-Tenancy Simulation

A future local version could simulate:

* API keys
* tenant ID
* project ID
* per-tenant deployment listing
* per-tenant rate limiting
* audit logs

This would make the project more realistic as a platform engineering example.

## Version 2: Runtime Orchestration

Version 1 uses one shared mock runtime.

Version 2 may move toward the original platform goal:

```text
control-plane
→ create deployment
→ start one runtime container or workload per deployment
→ route traffic by deployment ID
```

Possible runtime backends:

* Docker socket based local orchestrator
* Docker Compose generated services
* Kubernetes deployments
* Helm-managed vLLM workloads

### Docker Runtime Adapter

A local Docker runtime adapter could:

* create one container per deployment
* assign container names based on deployment ID
* attach containers to the platform network
* configure model ID, dtype, quantization, and parallelism
* expose health checks
* clean up containers when deployments are deleted

Important concerns:

* Docker socket security
* container cleanup
* port allocation
* network naming
* runtime health checks
* crash recovery
* state persistence
* race conditions during concurrent deployment creation

### Real vLLM Runtime

A future vLLM runtime should use the model catalog and deployment plan to generate startup options.

Potential configuration fields:

* Hugging Face model ID
* served model name
* dtype
* quantization
* max model length
* GPU memory utilization
* tensor parallel size
* pipeline parallel size
* Hugging Face token secret
* runtime image tag

The control plane should not assume that the V1 memory heuristic guarantees startup success. Real vLLM startup should be validated through runtime health checks and logs.

### GPU and Memory Planning

Future planning improvements:

* distinguish weight memory from KV cache memory
* estimate KV cache based on max model length and concurrency
* account for quantization format differences
* account for GPU memory utilization
* account for tensor parallel and pipeline parallel strategies
* detect multiple GPUs and recommend a parallelism strategy
* show why a model is or is not deployable on detected hardware

## Version 2.1: Kubernetes and Cloud

After the local Docker version is stable, the platform can evolve toward Kubernetes.

Potential work:

* Kubernetes manifests
* Helm chart
* GPU node scheduling
* resource requests and limits
* model cache volumes
* readiness and liveness probes
* service discovery
* ingress routing
* Terraform for cloud infrastructure
* AWS deployment

This should happen after the local runtime adapter is well understood.

## Version 2.2: Public Demo Assets

Before making the repository fully portfolio-ready:

* clean up and publish dashboard JSON
* add screenshots or demo GIFs
* add architecture diagram
* add example traces and LogQL / PromQL / TraceQL queries
* add troubleshooting guide
* add known limitations
* add a short demo script
