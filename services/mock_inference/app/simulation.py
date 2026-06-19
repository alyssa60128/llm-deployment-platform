import random
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationResult:
    response_text: str
    prompt_tokens: int
    generation_tokens: int
    time_to_first_token_seconds: float
    time_per_output_token_seconds: float
    e2e_latency_seconds: float


def estimate_token_count(text: str) -> int:
    """
    Rough token estimation for the mock service.

    This is intentionally simple and is not meant to match
    a real tokenizer.
    """
    return max(1, len(text.split()))


def simulate_inference(
    prompt: str,
    *,
    sleep_enabled: bool = True,
    random_generator: random.Random | None = None,
) -> SimulationResult:
    rng = random_generator or random.Random()

    prompt_tokens = estimate_token_count(prompt)
    generation_tokens = rng.randint(8, 32)

    time_to_first_token = rng.uniform(0.05, 0.3)
    time_per_output_token = rng.uniform(0.01, 0.05)

    generation_time = generation_tokens * time_per_output_token
    e2e_latency = time_to_first_token + generation_time

    if sleep_enabled:
        time.sleep(e2e_latency)

    return SimulationResult(
        response_text=f"This is a simulated response to: {prompt}",
        prompt_tokens=prompt_tokens,
        generation_tokens=generation_tokens,
        time_to_first_token_seconds=time_to_first_token,
        time_per_output_token_seconds=time_per_output_token,
        e2e_latency_seconds=e2e_latency,
    )