import io
import json

from osca.operations.infrastructure.logging import configure_json_logging


def test_structured_logging_redacts_sensitive_fields_recursively() -> None:
    stream = io.StringIO()
    logger = configure_json_logging(stream)
    logger.info(
        "vault probe",
        extra={
            "correlation_id": "correlation-1",
            "secret_value": "canary-secret-value",
            "details": {"access_token": "nested-canary", "state": "available"},
        },
    )

    output = stream.getvalue()
    payload = json.loads(output)
    assert "canary-secret-value" not in output
    assert "nested-canary" not in output
    assert payload["secret_value"] == "[REDACTED]"
    assert payload["details"]["access_token"] == "[REDACTED]"
    assert payload["correlation_id"] == "correlation-1"

