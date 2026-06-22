from fastapi.testclient import TestClient

from services.control_plane.app.main import app

client = TestClient(app)


def test_list_models_returns_supported_models() -> None:
    response = client.get("/api/v1/models")

    assert response.status_code == 200

    payload = response.json()

    model_ids = {
        model["id"]
        for model in payload
    }

    assert model_ids == {
        "llama-3.2-1b",
        "llama-3.2-3b-instruct-awq",
    }


def test_model_catalog_marks_hf_token_requirement() -> None:
    response = client.get("/api/v1/models")

    assert response.status_code == 200

    payload = {
        model["id"]: model
        for model in response.json()
    }

    assert payload["llama-3.2-1b"]["requires_hf_token"] is True
    assert (
        payload["llama-3.2-3b-instruct-awq"]["quantization"]
        == "awq"
    )
    assert (
        payload["llama-3.2-3b-instruct-awq"]["requires_gpu"]
        is True
    )