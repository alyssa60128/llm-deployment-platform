import re
import subprocess

import psutil

from services.control_plane.app.models import (
    CpuResources,
    GpuDevice,
    GpuResources,
    MemoryResources,
    ResourceSummary,
)


def _get_gpu_resources() -> GpuResources:
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=index,name,memory.total",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        return GpuResources(
            available=False,
            devices=[],
        )

    devices: list[GpuDevice] = []

    for line in result.stdout.splitlines():
        parts = [
            part.strip()
            for part in line.split(",")
        ]

        if len(parts) != 3:
            continue

        gpu_id, name, memory_total_mib = parts

        if not re.fullmatch(r"\d+", memory_total_mib):
            continue

        devices.append(
            GpuDevice(
                id=gpu_id,
                name=name,
                memory_total_bytes=(
                    int(memory_total_mib) * 1024 * 1024
                ),
            )
        )

    return GpuResources(
        available=bool(devices),
        devices=devices,
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
        gpu=_get_gpu_resources(),
    )