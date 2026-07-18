from osca.operations.infrastructure import configure_telemetry


def test_local_telemetry_requires_no_external_collector() -> None:
    telemetry = configure_telemetry(service_version="0.1.0.dev0")
    assert telemetry.tracer is not None
    assert telemetry.meter is not None

