import random

import pytest

from services.mock_inference.app.simulation import (
    estimate_token_count,
    simulate_inference,
)


def test_estimate_token_count_counts_words() -> None:
    assert estimate_token_count("Hello mock model") == 3


def test_estimate_token_count_returns_at_least_one() -> None:
    assert estimate_token_count("") == 1


def test_simulate_inference_returns_deterministic_result() -> None:
    result = simulate_inference(
        "Hello world",
        sleep_enabled=False,
        random_generator=random.Random(42),
    )

    assert result.response_text == (
        "This is a simulated response to: Hello world"
    )
    assert result.prompt_tokens == 2
    assert result.generation_tokens > 0
    assert result.time_to_first_token_seconds > 0
    assert result.time_per_output_token_seconds > 0
    assert result.e2e_latency_seconds > 0


def test_e2e_latency_is_sum_of_ttft_and_generation_time() -> None:
    result = simulate_inference(
        "Hello",
        sleep_enabled=False,
        random_generator=random.Random(42),
    )

    expected_latency = (
        result.time_to_first_token_seconds
        + result.generation_tokens
        * result.time_per_output_token_seconds
    )

    assert result.e2e_latency_seconds == pytest.approx(
        expected_latency,
    )