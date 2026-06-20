import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any
from opentelemetry import trace

class JsonFormatter(logging.Formatter):
    """Format Python log records as one-line JSON objects."""

    extra_fields = (
        "event",
        "request_id",
        "http_method",
        "http_path",
        "status_code",
        "duration_seconds",
        "model_name",
        "prompt_tokens",
        "generation_tokens",
        "ttft_seconds",
        "tpot_seconds",
        "e2e_latency_seconds",
        "error_type",
        "finish_reason",
    )

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(timezone.utc).isoformat().replace(
            "+00:00",
            "Z",
        )
        payload: dict[str, Any] = {
            "timestamp": timestamp,
            "level": record.levelname,
            "service": "mock-inference",
            "logger": record.name,
            "message": record.getMessage(),
        }

        span_context = trace.get_current_span().get_span_context()

        if span_context.is_valid:
            payload["trace_id"] = format(
                span_context.trace_id,
                "032x",
            )
            payload["span_id"] = format(
                span_context.span_id,
                "016x",
            )

        for field_name in self.extra_fields:
            if hasattr(record, field_name):
                payload[field_name] = getattr(record, field_name)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
        )


def configure_logging() -> None:
    """Configure application logs to be written as JSON to stdout."""

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)