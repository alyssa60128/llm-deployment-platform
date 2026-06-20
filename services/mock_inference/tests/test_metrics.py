from fastapi.testclient import TestClient

from services.mock_inference.app.main import app
from services.mock_inference.app.metrics import (
    GENERATION_TOKENS,
    PROMPT_TOKENS,
    REQUEST_SUCCESS,
    REQUESTS_RUNNING,
)

client = TestClient(app)


def get_metric_value(
    metric: object,
    label_values: tuple[str, ...],
    sample_suffix: str,
) -> float:
    for collected_metric in metric.collect():
        for sample in collected_metric.samples:
            if (
                sample.name.endswith(sample_suffix)
                and tuple(sample.labels.values()) == label_values
            ):
                return float(sample.value)

    return 0.0


def test_chat_completion_updates_request_and_token_metrics() -> None:
    model_name = "metrics-test-model"

    model_labels = (model_name,)

    prompt_tokens_before = get_metric_value(
        PROMPT_TOKENS,
        model_labels,
        "_total",
    )
    generation_tokens_before = get_metric_value(
        GENERATION_TOKENS,
        model_labels,
        "_total",
    )

    stop_before = get_metric_value(
        REQUEST_SUCCESS,
        (model_name, "stop"),
        "_total",
    )
    length_before = get_metric_value(
        REQUEST_SUCCESS,
        (model_name, "length"),
        "_total",
    )

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello metrics test",
                }
            ],
        },
    )

    assert response.status_code == 200

    prompt_tokens_after = get_metric_value(
        PROMPT_TOKENS,
        model_labels,
        "_total",
    )
    generation_tokens_after = get_metric_value(
        GENERATION_TOKENS,
        model_labels,
        "_total",
    )

    stop_after = get_metric_value(
        REQUEST_SUCCESS,
        (model_name, "stop"),
        "_total",
    )
    length_after = get_metric_value(
        REQUEST_SUCCESS,
        (model_name, "length"),
        "_total",
    )

    success_delta = (
        stop_after
        - stop_before
        + length_after
        - length_before
    )

    assert success_delta == 1

    assert prompt_tokens_after > prompt_tokens_before
    assert generation_tokens_after > generation_tokens_before


def test_running_requests_returns_to_zero() -> None:
    model_name = "running-test-model"

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": "Check running requests",
                }
            ],
        },
    )

    assert response.status_code == 200

    running_requests = get_metric_value(
        REQUESTS_RUNNING,
        (model_name,),
        "",
    )

    assert running_requests == 0


def test_metrics_endpoint_exposes_vllm_metrics() -> None:
    model_name = "exposition-test-model"

    client.post(
        "/v1/chat/completions",
        json={
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": "Generate telemetry",
                }
            ],
        },
    )

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]

    body = response.text

    assert "vllm:request_success_total" in body
    assert "vllm:prompt_tokens_total" in body
    assert "vllm:generation_tokens_total" in body
    assert "vllm:time_to_first_token_seconds_bucket" in body
    assert f'model_name="{model_name}"' in body