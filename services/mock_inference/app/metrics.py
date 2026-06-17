from prometheus_client import Counter, Gauge, Histogram


MODEL_LABEL = "model_name"


REQUESTS_RUNNING = Gauge(
    "vllm:num_requests_running",
    "Number of requests in model execution batches.",
    labelnames=[MODEL_LABEL],
)

REQUESTS_WAITING = Gauge(
    "vllm:num_requests_waiting",
    "Number of requests waiting to be processed.",
    labelnames=[MODEL_LABEL],
)

REQUEST_SUCCESS = Counter(
    "vllm:request_success",
    "Count of successfully processed requests.",
    labelnames=[MODEL_LABEL, "finished_reason"],
)

PROMPT_TOKENS = Counter(
    "vllm:prompt_tokens",
    "Number of prefill tokens processed.",
    labelnames=[MODEL_LABEL],
)

GENERATION_TOKENS = Counter(
    "vllm:generation_tokens",
    "Number of generation tokens processed.",
    labelnames=[MODEL_LABEL],
)

TIME_TO_FIRST_TOKEN = Histogram(
    "vllm:time_to_first_token_seconds",
    "Histogram of time to first token in seconds.",
    labelnames=[MODEL_LABEL],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

E2E_REQUEST_LATENCY = Histogram(
    "vllm:e2e_request_latency_seconds",
    "Histogram of end-to-end request latency in seconds.",
    labelnames=[MODEL_LABEL],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

REQUEST_PROMPT_TOKENS = Histogram(
    "vllm:request_prompt_tokens",
    "Number of prefill tokens processed per request.",
    labelnames=[MODEL_LABEL],
    buckets=(1, 8, 16, 32, 64, 128, 256, 512, 1024),
)

REQUEST_GENERATION_TOKENS = Histogram(
    "vllm:request_generation_tokens",
    "Number of generation tokens processed per request.",
    labelnames=[MODEL_LABEL],
    buckets=(1, 8, 16, 32, 64, 128, 256, 512),
)

TIME_PER_OUTPUT_TOKEN = Histogram(
    "vllm:request_time_per_output_token_seconds",
    "Histogram of time per output token in seconds.",
    labelnames=[MODEL_LABEL],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5),
)