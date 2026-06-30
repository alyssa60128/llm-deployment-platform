from uuid import uuid4
import logging
from time import perf_counter
from fastapi import FastAPI, Request

from services.mock_inference.app.models import (
    ChatCompletionChoice,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
)

from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from services.mock_inference.app.metrics import (
    REQUESTS_RUNNING,
    record_successful_request,
)
from services.mock_inference.app.simulation import simulate_inference
from services.mock_inference.app.logging_config import configure_logging

from opentelemetry.instrumentation.fastapi import (
    FastAPIInstrumentor,
)

from services.mock_inference.app.tracing import (
    configure_tracing,
    get_tracer,
)

NOISY_PATHS = {
    "/metrics",
    "/healthz",
}

configure_logging()
configure_tracing()

logger = logging.getLogger(__name__)
tracer = get_tracer()

app = FastAPI(
    title="Mock Inference Service",
    version="0.1.0",
)

FastAPIInstrumentor.instrument_app(
    app,
    excluded_urls="/metrics,/healthz",
)

@app.middleware("http")
async def add_request_context(
    request: Request,
    call_next,
):
    should_log_request = request.url.path not in NOISY_PATHS

    request_id = request.headers.get(
        "X-Request-ID",
        f"req-{uuid4().hex}",
    )

    request.state.request_id = request_id
    started_at = perf_counter()

    if should_log_request:
        logger.info(
            "HTTP request started",
            extra={
                "event": "request.started",
                "request_id": request_id,
                "http_method": request.method,
                "http_path": request.url.path,
            },
        )

    try:
        response = await call_next(request)
    except Exception:
        duration = perf_counter() - started_at

        logger.exception(
            "HTTP request failed",
            extra={
                "event": "request.failed",
                "request_id": request_id,
                "http_method": request.method,
                "http_path": request.url.path,
                "duration_seconds": round(duration, 6),
            },
        )
        raise

    duration = perf_counter() - started_at

    response.headers["X-Request-ID"] = request_id
    if should_log_request:
        logger.info(
            "HTTP request completed",
            extra={
                "event": "request.completed",
                "request_id": request_id,
                "http_method": request.method,
                "http_path": request.url.path,
                "status_code": response.status_code,
                "duration_seconds": round(duration, 6),
            },
        )

    return response

@app.get("/healthz")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "mock-inference",
    }


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.post(
    "/v1/chat/completions",
    response_model=ChatCompletionResponse,
)
def create_chat_completion(
    payload: ChatCompletionRequest,
    http_request: Request, #In order to obtain HTTP requests simultaneously
) -> ChatCompletionResponse:
    latest_user_message = next(
        (
            message.content
            for message in reversed(payload.messages)
            if message.role == "user"
        ),
        "No user message provided.",
    )

    running_requests = REQUESTS_RUNNING.labels(
        model_name=payload.model,
    )

    running_requests.inc()

    try:
        with tracer.start_as_current_span(
            "mock_inference.generate",
        ) as inference_span:
            inference_span.set_attribute(
                "gen_ai.request.model",
                payload.model,
            )
            inference_span.set_attribute(
                "gen_ai.operation.name",
                "chat",
            )

            result = simulate_inference(
                latest_user_message,
            )

            inference_span.set_attribute(
                "gen_ai.usage.input_tokens",
                result.prompt_tokens,
            )
            inference_span.set_attribute(
                "gen_ai.usage.output_tokens",
                result.generation_tokens,
            )
            inference_span.set_attribute(
                "mock.ttft_seconds",
                result.time_to_first_token_seconds,
            )
            inference_span.set_attribute(
                "mock.tpot_seconds",
                result.time_per_output_token_seconds,
            )
            inference_span.set_attribute(
                "gen_ai.response.finish_reasons",
                result.finish_reason,
            )

        with tracer.start_as_current_span(
            "mock_inference.record_metrics",
        ):
            record_successful_request(
                model_name=payload.model,
                result=result,
            )

        logger.info(
            "Inference completed",
            extra={
                "event": "inference.completed",
                "request_id": http_request.state.request_id,
                "model_name": payload.model,
                "prompt_tokens": result.prompt_tokens,
                "generation_tokens": result.generation_tokens,
                "finish_reason": result.finish_reason,
                "ttft_seconds": round(
                    result.time_to_first_token_seconds,
                    6,
                ),
                "tpot_seconds": round(
                    result.time_per_output_token_seconds,
                    6,
                ),
                "e2e_latency_seconds": round(
                    result.e2e_latency_seconds,
                    6,
                ),
            },
        )

        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid4().hex}",
            object="chat.completion",
            model=payload.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(
                        role="assistant",
                        content=result.response_text,
                    ),
                    finish_reason=result.finish_reason,
                )
            ],
        )
    finally:
        running_requests.dec()