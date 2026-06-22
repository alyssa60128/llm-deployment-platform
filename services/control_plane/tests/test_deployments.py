import pytest
from fastapi.testclient import TestClient

from services.control_plane.app.deployments import (
    clear_deployments_for_tests,
)
from services.control_plane.app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_deployment_store() -> None:
    clear_deployments_for_tests()


def test_create_deployment_for_supported_model() -> None:
    response = client.post(
        "/api/v1/deployments",
        json={
            "model_id": "llama-3.2-1b",
        },
    )

    assert response.status_code == 201

    payload = response.json()

    assert payload["id"].startswith("dep-")
    assert payload["model_id"] == "llama-3.2-1b"
    assert payload["served_model_name"] == "llama-3.2-1b"
    assert payload["runtime"] == "mock"
    assert payload["status"] == "RUNNING"

    assert payload["plan"]["model_id"] == "llama-3.2-1b"
    assert payload["plan"]["runtime"] == "mock"
    assert (
        payload["plan"]["estimated_weight_memory_bytes"]
        == 2_000_000_000
    )
    assert (
        payload["plan"]["recommended_vram_bytes"]
        == 2_500_000_000
    )
    assert (
        payload["plan"]["runnable_on_detected_hardware"]
        is True
    )


def test_create_deployment_rejects_unknown_model() -> None:
    response = client.post(
        "/api/v1/deployments",
        json={
            "model_id": "unknown-model",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Model not found: unknown-model",
    }


def test_list_deployments_returns_created_deployment() -> None:
    create_response = client.post(
        "/api/v1/deployments",
        json={
            "model_id": "llama-3.2-3b-instruct-awq",
        },
    )

    assert create_response.status_code == 201

    list_response = client.get("/api/v1/deployments")

    assert list_response.status_code == 200

    deployments = list_response.json()

    assert len(deployments) == 1
    assert deployments[0]["model_id"] == (
        "llama-3.2-3b-instruct-awq"
    )
    assert deployments[0]["plan"][
        "estimated_weight_memory_bytes"
    ] == 1_500_000_000
    assert deployments[0]["plan"][
        "recommended_vram_bytes"
    ] == 1_875_000_000


def test_get_deployment_by_id() -> None:
    create_response = client.post(
        "/api/v1/deployments",
        json={
            "model_id": "llama-3.2-1b",
        },
    )

    deployment_id = create_response.json()["id"]

    get_response = client.get(
        f"/api/v1/deployments/{deployment_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["id"] == deployment_id


def test_get_unknown_deployment_returns_404() -> None:
    response = client.get(
        "/api/v1/deployments/dep-does-not-exist"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Deployment not found: dep-does-not-exist",
    }


def test_delete_deployment_marks_it_deleted() -> None:
    create_response = client.post(
        "/api/v1/deployments",
        json={
            "model_id": "llama-3.2-1b",
        },
    )

    deployment_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/deployments/{deployment_id}"
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "DELETED"

    get_response = client.get(
        f"/api/v1/deployments/{deployment_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["status"] == "DELETED"