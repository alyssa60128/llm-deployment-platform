from pydantic import BaseModel


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