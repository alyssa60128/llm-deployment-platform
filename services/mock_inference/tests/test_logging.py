import json
import logging

from services.mock_inference.app.logging_config import JsonFormatter
from fastapi.testclient import TestClient
from services.mock_inference.app.main import app

client = TestClient(app)

def test_json_formatter_outputs_structured_fields() -> None:
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Inference completed",
        args=(),
        exc_info=None,
    )

    record.event = "inference.completed"
    record.request_id = "req-test-001"
    record.model_name = "model-a"
    record.prompt_tokens = 4

    formatted = JsonFormatter().format(record)
    payload = json.loads(formatted)

    assert payload["level"] == "INFO"
    assert payload["service"] == "mock-inference"
    assert payload["message"] == "Inference completed"
    assert payload["event"] == "inference.completed"
    assert payload["request_id"] == "req-test-001"
    assert payload["model_name"] == "model-a"
    assert payload["prompt_tokens"] == 4
    assert "timestamp" in payload

def test_response_contains_request_id() -> None:
    response = client.get(
        "/healthz",
        headers={
            "X-Request-ID": "req-from-test",
        },
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-from-test"