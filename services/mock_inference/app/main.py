from fastapi import FastAPI

app = FastAPI(
    title="Mock Inference Service",
    version="0.1.0",
)


@app.get("/healthz")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "mock-inference",
    }