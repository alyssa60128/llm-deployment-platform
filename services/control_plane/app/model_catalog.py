from services.control_plane.app.models import ModelCatalogItem


MODEL_CATALOG: list[ModelCatalogItem] = [
    ModelCatalogItem(
        id="llama-3.2-1b",
        display_name="Llama 3.2 1B",
        provider="Meta",
        source="meta-llama/Llama-3.2-1B",
        source_url="https://huggingface.co/meta-llama/Llama-3.2-1B",
        backend="mock-vllm",
        parameter_count_billions=1.0,
        context_window=None,
        quantization="none",
        requires_gpu=False,
        requires_hf_token=True,
        recommended_for=(
            "Baseline small-model deployment simulation and future "
            "CPU/GPU compatibility testing."
        ),
        notes=(
            "Meta Llama models may require accepting the license and "
            "using a Hugging Face token before downloading the real weights. "
            "In V1 this platform only simulates deployment."
        ),
    ),
    ModelCatalogItem(
        id="llama-3.2-3b-instruct-awq",
        display_name="Llama 3.2 3B Instruct AWQ",
        provider="AMead10",
        source="AMead10/Llama-3.2-3B-Instruct-AWQ",
        source_url=(
            "https://huggingface.co/AMead10/"
            "Llama-3.2-3B-Instruct-AWQ"
        ),
        backend="mock-vllm",
        parameter_count_billions=3.0,
        context_window=None,
        quantization="awq",
        requires_gpu=True,
        requires_hf_token=False,
        recommended_for=(
            "Future low-VRAM GPU experiment with quantized instruction "
            "following model."
        ),
        notes=(
            "AWQ quantization is included to make future real inference "
            "experiments more feasible on limited GPU memory. V1 does not "
            "download or run the model."
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