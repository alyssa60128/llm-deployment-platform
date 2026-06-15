from uuid import uuid4

from fastapi import FastAPI

from services.mock_inference.app.models import (
    ChatCompletionChoice,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
)

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

    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid4().hex}",
        object="chat.completion",
        model=request.model,
        choices=[
            ChatCompletionChoice(
                index=0,
                message=ChatMessage(
                    role="assistant",
                    content=(
                        "This is a simulated response to: "
                        f"{latest_user_message}"
                    ),
                ),
                finish_reason="stop",
            )
        ],
    )