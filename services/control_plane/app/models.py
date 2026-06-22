from typing import Literal

from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from enum import Enum

class CpuResources(BaseModel):
    logical_cores: int


class MemoryResources(BaseModel):
    total_bytes: int
    available_bytes: int


class GpuDevice(BaseModel):
    id: str
    name: str
    memory_total_bytes: int


class GpuResources(BaseModel):
    available: bool
    total_memory_bytes: int
    largest_device_memory_bytes: int
    devices: list[GpuDevice]


class ResourceSummary(BaseModel):
    cpu: CpuResources
    memory: MemoryResources
    gpu: GpuResources


ModelBackend = Literal[
    "mock-vllm",
    "vllm",
]


QuantizationType = Literal[
    "none",
    "awq",
]


class VllmDefaults(BaseModel):
    dtype: str = "auto"
    quantization: str | None = None
    max_model_len: int | None = None
    gpu_memory_utilization: float = 0.9
    tensor_parallel_size: int = 1
    pipeline_parallel_size: int = 1


class ModelCatalogItem(BaseModel):
    id: str
    hf_model_id: str
    served_model_name: str
    source_url: HttpUrl
    parameters_billion: float
    bytes_per_parameter: float
    requires_hf_token: bool
    vllm_defaults: VllmDefaults


class DeploymentStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DELETED = "DELETED"


class DeploymentRuntime(str, Enum):
    MOCK = "mock"
    VLLM = "vllm"


class CreateDeploymentRequest(BaseModel):
    model_id: str = Field(
        ...,
        description="Model catalog ID to deploy.",
    )
    runtime: DeploymentRuntime = DeploymentRuntime.MOCK


class DeploymentPlan(BaseModel):
    model_id: str
    runtime: DeploymentRuntime
    estimated_weight_memory_bytes: int
    recommended_vram_bytes: int
    detected_gpu_count: int
    detected_total_gpu_memory_bytes: int
    detected_largest_gpu_memory_bytes: int
    runnable_on_detected_hardware: bool
    suggested_tensor_parallel_size: int
    suggested_pipeline_parallel_size: int
    reason: str


class Deployment(BaseModel):
    id: str
    model_id: str
    served_model_name: str
    runtime: DeploymentRuntime
    status: DeploymentStatus
    plan: DeploymentPlan
    created_at: datetime
    updated_at: datetime