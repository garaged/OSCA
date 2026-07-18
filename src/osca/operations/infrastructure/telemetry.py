from __future__ import annotations

from dataclasses import dataclass

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider


@dataclass(frozen=True)
class Telemetry:
    tracer: trace.Tracer
    meter: metrics.Meter


def configure_telemetry(*, service_version: str) -> Telemetry:
    resource = Resource.create(
        {"service.name": "osca", "service.version": service_version}
    )
    tracer_provider = TracerProvider(resource=resource)
    meter_provider = MeterProvider(resource=resource)
    return Telemetry(
        tracer=tracer_provider.get_tracer("osca"),
        meter=meter_provider.get_meter("osca"),
    )

