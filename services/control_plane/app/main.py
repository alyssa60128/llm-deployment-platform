from fastapi import FastAPI, HTTPException, status

from services.control_plane.app.resources import get_resource_summary
from services.control_plane.app.model_catalog import list_models

from services.control_plane.app.models import (
    CreateDeploymentRequest,
    Deployment,
    DeploymentChatCompletionRequest,
    ModelCatalogItem,
    ResourceSummary,
)

from services.control_plane.app.deployments import (
    create_deployment,
    delete_deployment,
    get_deployment,
    get_runtime_base_url,
    list_deployments,
)

import httpx


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

@app.post(
    "/api/v1/deployments",
    response_model=Deployment,
    status_code=status.HTTP_201_CREATED,
)
def create_model_deployment(
    request: CreateDeploymentRequest,
) -> Deployment:
    deployment = create_deployment(request)

    if deployment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model not found: {request.model_id}",
        )

    return deployment


@app.get(
    "/api/v1/deployments",
    response_model=list[Deployment],
)
def read_deployments() -> list[Deployment]:
    return list_deployments()


@app.get(
    "/api/v1/deployments/{deployment_id}",
    response_model=Deployment,
)
def read_deployment(
    deployment_id: str,
) -> Deployment:
    deployment = get_deployment(deployment_id)

    if deployment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment not found: {deployment_id}",
        )

    return deployment


@app.delete(
    "/api/v1/deployments/{deployment_id}",
    response_model=Deployment,
)
def delete_model_deployment(
    deployment_id: str,
) -> Deployment:
    deployment = delete_deployment(deployment_id)

    if deployment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment not found: {deployment_id}",
        )

    return deployment

@app.post(
    "/api/v1/deployments/{deployment_id}/chat/completions",
)
def proxy_chat_completion(
    deployment_id: str,
    payload: DeploymentChatCompletionRequest,
) -> dict:
    deployment = get_deployment(deployment_id)

    if deployment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment not found: {deployment_id}",
        )

    if deployment.status != "RUNNING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Deployment is not running: "
                f"{deployment.status}"
            ),
        )

    proxied_payload = {
        "model": deployment.served_model_name,
        "messages": [
            message.model_dump()
            for message in payload.messages
        ],
    }

    try:
        response = httpx.post(
            f"{get_runtime_base_url()}/v1/chat/completions",
            json=proxied_payload,
            headers={
                "X-Deployment-ID": deployment.id,
            },
            timeout=10,
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Runtime request failed: {exc}",
        ) from exc

    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "runtime_status_code": response.status_code,
                "runtime_response": response.text,
            },
        )

    return response.json()