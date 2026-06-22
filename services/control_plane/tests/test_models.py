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


def test_model_catalog_marks_hf_token_and_vllm_defaults() -> None:
    response = client.get("/api/v1/models")

    assert response.status_code == 200

    payload = {
        model["id"]: model
        for model in response.json()
    }

    llama_1b = payload["llama-3.2-1b"]
    llama_3b_awq = payload["llama-3.2-3b-instruct-awq"]

    assert llama_1b["requires_hf_token"] is True
    assert llama_1b["hf_model_id"] == "meta-llama/Llama-3.2-1B"
    assert llama_1b["vllm_defaults"]["quantization"] is None
    assert llama_1b["bytes_per_parameter"] == 2.0

    assert (
        llama_3b_awq["hf_model_id"]
        == "AMead10/Llama-3.2-3B-Instruct-AWQ"
    )
    assert llama_3b_awq["requires_hf_token"] is False
    assert llama_3b_awq["vllm_defaults"]["quantization"] == "awq"
    assert llama_3b_awq["bytes_per_parameter"] == 0.5