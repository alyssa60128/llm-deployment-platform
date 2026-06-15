from fastapi.testclient import TestClient

from services.mock_inference.app.main import app

client = TestClient(app)


def test_create_chat_completion_returns_mock_response() -> None:
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "model-a",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello",
                }
            ],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["object"] == "chat.completion"
    assert body["model"] == "model-a"
    assert body["id"].startswith("chatcmpl-")
    assert body["choices"][0]["index"] == 0
    assert body["choices"][0]["message"] == {
        "role": "assistant",
        "content": "This is a simulated response to: Hello",
    }
    assert body["choices"][0]["finish_reason"] == "stop"


def test_create_chat_completion_rejects_empty_messages() -> None:
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "model-a",
            "messages": [],
        },
    )

    assert response.status_code == 422


def test_create_chat_completion_rejects_invalid_role() -> None:
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "model-a",
            "messages": [
                {
                    "role": "cat",
                    "content": "Meow",
                }
            ],
        },
    )

    assert response.status_code == 422