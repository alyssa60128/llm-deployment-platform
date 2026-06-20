import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def tracing_enabled() -> bool:
    return os.getenv(
        "OTEL_TRACING_ENABLED",
        "true",
    ).lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def configure_tracing() -> None:
    if not tracing_enabled():
        return

    resource = Resource.create(
        {
            "service.name": "mock-inference",
            "service.version": "0.1.0",
            "deployment.environment.name": os.getenv(
                "DEPLOYMENT_ENVIRONMENT",
                "local",
            ),
        }
    )

    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(
        endpoint=os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "http://alloy:4317",
        ),
        insecure=True,
    )

    provider.add_span_processor(
        BatchSpanProcessor(exporter)
    )

    trace.set_tracer_provider(provider)


def get_tracer() -> trace.Tracer:
    return trace.get_tracer(
        "services.mock_inference",
        "0.1.0",
    )