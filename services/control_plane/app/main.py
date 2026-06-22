from fastapi import FastAPI

from services.control_plane.app.models import ResourceSummary
from services.control_plane.app.resources import get_resource_summary

app = FastAPI(
    title="Control Plane Service",
    version="0.1.0",
)


@app.get("/healthz")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "control-plane",
    }

@app.get(
    "/api/v1/resources",
    response_model=ResourceSummary,
)
def read_resources() -> ResourceSummary:
    return get_resource_summary()