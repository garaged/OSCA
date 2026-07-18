import json

from osca.bootstrap.authorization import local_authorization_context
from osca.shared_kernel.api import CorrelationId
from osca.workflow.api import DiagnosticInput, DiagnosticRun, SubmitDiagnosticRun
from osca.workflow.api.contracts import GOVERNING_DECISION, GOVERNING_REQUIREMENTS


def test_contract_trace_and_schema_are_deterministic() -> None:
    assert GOVERNING_REQUIREMENTS == ("REQ-0011", "REQ-0012", "REQ-0013", "REQ-0014", "REQ-0015")
    assert GOVERNING_DECISION == "ADR-0013"
    first = json.dumps(DiagnosticRun.model_json_schema(), sort_keys=True)
    second = json.dumps(DiagnosticRun.model_json_schema(), sort_keys=True)
    assert first == second
    assert '"const": "osca.workflow.diagnostic-run"' in first


def test_version_1_semantic_fixture_round_trips() -> None:
    fixture = SubmitDiagnosticRun(
        authorization=local_authorization_context(),
        correlation_id=CorrelationId.new(),
        idempotency_key="fixture",
        input=DiagnosticInput(probe="storage", parameters={"scope": "metadata"}),
    )
    assert SubmitDiagnosticRun.model_validate_json(fixture.model_dump_json()) == fixture
