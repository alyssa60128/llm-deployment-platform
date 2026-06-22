from services.control_plane.app.models import (
    ModelCatalogItem,
    VllmDefaults,
)

MODEL_CATALOG: list[ModelCatalogItem] = [
    ModelCatalogItem(
        id="llama-3.2-1b",
        hf_model_id="meta-llama/Llama-3.2-1B",
        served_model_name="llama-3.2-1b",
        source_url="https://huggingface.co/meta-llama/Llama-3.2-1B",
        parameters_billion=1.0,
        bytes_per_parameter=2.0,
        requires_hf_token=True,
        vllm_defaults=VllmDefaults(
            dtype="auto",
            quantization=None,
            max_model_len=8192,
            gpu_memory_utilization=0.9,
            tensor_parallel_size=1,
            pipeline_parallel_size=1,
        ),
    ),
    ModelCatalogItem(
        id="llama-3.2-3b-instruct-awq",
        hf_model_id="AMead10/Llama-3.2-3B-Instruct-AWQ",
        served_model_name="llama-3.2-3b-instruct-awq",
        source_url=(
            "https://huggingface.co/AMead10/"
            "Llama-3.2-3B-Instruct-AWQ"
        ),
        parameters_billion=3.0,
        bytes_per_parameter=0.5,
        requires_hf_token=False,
        vllm_defaults=VllmDefaults(
            dtype="auto",
            quantization="awq",
            max_model_len=8192,
            gpu_memory_utilization=0.9,
            tensor_parallel_size=1,
            pipeline_parallel_size=1,
        ),
    ),
]


def list_models() -> list[ModelCatalogItem]:
    return MODEL_CATALOG


def get_model_by_id(model_id: str) -> ModelCatalogItem | None:
    for model in MODEL_CATALOG:
        if model.id == model_id:
            return model

    return None