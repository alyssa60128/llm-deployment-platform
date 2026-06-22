import psutil

from services.control_plane.app.models import (
    CpuResources,
    GpuResources,
    MemoryResources,
    ResourceSummary,
)


def get_resource_summary() -> ResourceSummary:
    memory = psutil.virtual_memory()

    return ResourceSummary(
        cpu=CpuResources(
            logical_cores=psutil.cpu_count(logical=True) or 1,
        ),
        memory=MemoryResources(
            total_bytes=memory.total,
            available_bytes=memory.available,
        ),
        gpu=GpuResources(
            available=False,
            devices=[],
        ),
    )