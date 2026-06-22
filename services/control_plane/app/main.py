from fastapi import FastAPI

from services.control_plane.app.resources import get_resource_summary

from services.control_plane.app.model_catalog import list_models
from services.control_plane.app.models import (
    ModelCatalogItem,
    ResourceSummary,
)

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

@app.get(
    "/api/v1/models",
    response_model=list[ModelCatalogItem],
)
def read_models() -> list[ModelCatalogItem]:
    return list_models()