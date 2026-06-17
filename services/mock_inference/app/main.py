from uuid import uuid4

from fastapi import FastAPI

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

app = FastAPI(
    title="Mock Inference Service",
    version="0.1.0",
)


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
    request: ChatCompletionRequest,
) -> ChatCompletionResponse:
    latest_user_message = next(
        (
            message.content
            for message in reversed(request.messages)
            if message.role == "user"
        ),
        "No user message provided.",
    )

    running_requests = REQUESTS_RUNNING.labels(
        model_name=request.model,
    )

    running_requests.inc()

    try:
        result = simulate_inference(latest_user_message)

        record_successful_request(
            model_name=request.model,
            result=result,
        )

        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid4().hex}",
            object="chat.completion",
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(
                        role="assistant",
                        content=result.response_text,
                    ),
                    finish_reason="stop",
                )
            ],
        )
    finally:
        running_requests.dec()