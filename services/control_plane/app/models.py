from typing import Literal

from pydantic import BaseModel, HttpUrl


class CpuResources(BaseModel):
    logical_cores: int


class MemoryResources(BaseModel):
    total_bytes: int
    available_bytes: int


class GpuDevice(BaseModel):
    id: str
    name: str
    memory_total_bytes: int | None = None


class GpuResources(BaseModel):
    available: bool
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


class ModelCatalogItem(BaseModel):
    id: str
    display_name: str
    provider: str
    source: str
    source_url: HttpUrl
    backend: ModelBackend
    parameter_count_billions: float
    context_window: int | None = None
    quantization: QuantizationType
    requires_gpu: bool
    requires_hf_token: bool
    recommended_for: str
    notes: str