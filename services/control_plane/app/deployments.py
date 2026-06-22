from datetime import datetime, timezone
from uuid import uuid4

from services.control_plane.app.model_catalog import (
    get_model_by_id,
)
from services.control_plane.app.models import (
    CreateDeploymentRequest,
    Deployment,
    DeploymentPlan,
    DeploymentRuntime,
    DeploymentStatus,
    ModelCatalogItem,
    ResourceSummary,
)
from services.control_plane.app.resources import get_resource_summary


_DEPLOYMENTS: dict[str, Deployment] = {}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _estimate_weight_memory_bytes(
    model: ModelCatalogItem,
) -> int:
    return int(
        model.parameters_billion
        * 1_000_000_000
        * model.bytes_per_parameter
    )


def _create_deployment_plan(
    model: ModelCatalogItem,
    resources: ResourceSummary,
    runtime: DeploymentRuntime,
) -> DeploymentPlan:
    estimated_weight_memory_bytes = (
        _estimate_weight_memory_bytes(model)
    )

    recommended_vram_bytes = int(
        estimated_weight_memory_bytes * 1.25
    )

    gpu_count = len(resources.gpu.devices)
    total_gpu_memory_bytes = resources.gpu.total_memory_bytes
    largest_gpu_memory_bytes = (
        resources.gpu.largest_device_memory_bytes
    )

    if runtime == DeploymentRuntime.MOCK:
        runnable = True
        tensor_parallel_size = 1
        pipeline_parallel_size = 1

        if gpu_count == 0:
            reason = (
                "Mock runtime can run without GPU. Real vLLM runtime "
                "would require GPU validation."
            )
        elif largest_gpu_memory_bytes >= recommended_vram_bytes:
            reason = (
                "Mock runtime selected. Detected GPU memory is "
                "estimated to fit the model on one GPU for a future "
                "vLLM runtime."
            )
        elif total_gpu_memory_bytes >= recommended_vram_bytes:
            pipeline_parallel_size = gpu_count
            reason = (
                "Mock runtime selected. Total GPU memory may fit the "
                "model, but single-GPU memory is insufficient; future "
                "real vLLM runtime may need multi-GPU parallelism."
            )
        else:
            reason = (
                "Mock runtime selected. Detected GPU memory is below "
                "the estimated requirement for a future real vLLM "
                "runtime."
            )

        return DeploymentPlan(
            model_id=model.id,
            runtime=runtime,
            estimated_weight_memory_bytes=(
                estimated_weight_memory_bytes
            ),
            recommended_vram_bytes=recommended_vram_bytes,
            detected_gpu_count=gpu_count,
            detected_total_gpu_memory_bytes=total_gpu_memory_bytes,
            detected_largest_gpu_memory_bytes=(
                largest_gpu_memory_bytes
            ),
            runnable_on_detected_hardware=runnable,
            suggested_tensor_parallel_size=tensor_parallel_size,
            suggested_pipeline_parallel_size=(
                pipeline_parallel_size
            ),
            reason=reason,
        )

    if gpu_count == 0:
        return DeploymentPlan(
            model_id=model.id,
            runtime=runtime,
            estimated_weight_memory_bytes=(
                estimated_weight_memory_bytes
            ),
            recommended_vram_bytes=recommended_vram_bytes,
            detected_gpu_count=0,
            detected_total_gpu_memory_bytes=0,
            detected_largest_gpu_memory_bytes=0,
            runnable_on_detected_hardware=False,
            suggested_tensor_parallel_size=1,
            suggested_pipeline_parallel_size=1,
            reason=(
                "No GPU detected. Real vLLM runtime is not "
                "available on this host."
            ),
        )

    if largest_gpu_memory_bytes >= recommended_vram_bytes:
        return DeploymentPlan(
            model_id=model.id,
            runtime=runtime,
            estimated_weight_memory_bytes=(
                estimated_weight_memory_bytes
            ),
            recommended_vram_bytes=recommended_vram_bytes,
            detected_gpu_count=gpu_count,
            detected_total_gpu_memory_bytes=total_gpu_memory_bytes,
            detected_largest_gpu_memory_bytes=(
                largest_gpu_memory_bytes
            ),
            runnable_on_detected_hardware=True,
            suggested_tensor_parallel_size=1,
            suggested_pipeline_parallel_size=1,
            reason=(
                "Estimated model weight memory fits on the largest "
                "detected GPU. This is a V1 heuristic and does not "
                "guarantee real vLLM startup success."
            ),
        )

    if total_gpu_memory_bytes >= recommended_vram_bytes:
        return DeploymentPlan(
            model_id=model.id,
            runtime=runtime,
            estimated_weight_memory_bytes=(
                estimated_weight_memory_bytes
            ),
            recommended_vram_bytes=recommended_vram_bytes,
            detected_gpu_count=gpu_count,
            detected_total_gpu_memory_bytes=total_gpu_memory_bytes,
            detected_largest_gpu_memory_bytes=(
                largest_gpu_memory_bytes
            ),
            runnable_on_detected_hardware=True,
            suggested_tensor_parallel_size=1,
            suggested_pipeline_parallel_size=gpu_count,
            reason=(
                "Estimated total GPU memory may fit the model, but "
                "single-GPU memory is insufficient. Future real vLLM "
                "runtime may need multi-GPU pipeline parallelism."
            ),
        )

    return DeploymentPlan(
        model_id=model.id,
        runtime=runtime,
        estimated_weight_memory_bytes=(
            estimated_weight_memory_bytes
        ),
        recommended_vram_bytes=recommended_vram_bytes,
        detected_gpu_count=gpu_count,
        detected_total_gpu_memory_bytes=total_gpu_memory_bytes,
        detected_largest_gpu_memory_bytes=(
            largest_gpu_memory_bytes
        ),
        runnable_on_detected_hardware=False,
        suggested_tensor_parallel_size=1,
        suggested_pipeline_parallel_size=1,
        reason=(
            "Estimated VRAM requirement exceeds detected GPU memory."
        ),
    )


def create_deployment(
    request: CreateDeploymentRequest,
) -> Deployment | None:
    model = get_model_by_id(request.model_id)

    if model is None:
        return None

    resources = get_resource_summary()
    plan = _create_deployment_plan(
        model=model,
        resources=resources,
        runtime=request.runtime,
    )

    now = _utc_now()

    deployment = Deployment(
        id=f"dep-{uuid4().hex}",
        model_id=model.id,
        served_model_name=model.served_model_name,
        runtime=request.runtime,
        status=DeploymentStatus.RUNNING,
        plan=plan,
        created_at=now,
        updated_at=now,
    )

    _DEPLOYMENTS[deployment.id] = deployment

    return deployment


def list_deployments() -> list[Deployment]:
    return list(_DEPLOYMENTS.values())


def get_deployment(
    deployment_id: str,
) -> Deployment | None:
    return _DEPLOYMENTS.get(deployment_id)


def delete_deployment(
    deployment_id: str,
) -> Deployment | None:
    deployment = _DEPLOYMENTS.get(deployment_id)

    if deployment is None:
        return None

    updated = deployment.model_copy(
        update={
            "status": DeploymentStatus.DELETED,
            "updated_at": _utc_now(),
        }
    )

    _DEPLOYMENTS[deployment_id] = updated

    return updated


def clear_deployments_for_tests() -> None:
    _DEPLOYMENTS.clear()