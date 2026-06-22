from fastapi.testclient import TestClient

from services.control_plane.app.main import app

client = TestClient(app)


def test_read_resources_returns_cpu_memory_and_gpu() -> None:
    response = client.get("/api/v1/resources")

    assert response.status_code == 200

    payload = response.json()

    assert payload["cpu"]["logical_cores"] >= 1

    assert payload["memory"]["total_bytes"] > 0
    assert payload["memory"]["available_bytes"] >= 0
    assert (
        payload["memory"]["available_bytes"]
        <= payload["memory"]["total_bytes"]
    )

    assert payload["gpu"] == {
        "available": False,
        "devices": [],
    }