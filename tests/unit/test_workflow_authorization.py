import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from osca.security.api import AuthorizationContext, Capability
from osca.shared_kernel.api import CorrelationId
from osca.workflow.api import DiagnosticInput, SubmitDiagnosticRun
from osca.workflow.application.handlers import AuthorizationDenied, WorkflowService
from osca.workflow.infrastructure import SqliteDiagnosticRunRepository, WorkflowBase


def test_submit_requires_trusted_capability_before_persistence() -> None:
    engine = create_engine("sqlite://")
    WorkflowBase.metadata.create_all(engine)
    with Session(engine) as session, session.begin():
        service = WorkflowService(SqliteDiagnosticRunRepository(session))
        command = SubmitDiagnosticRun(
            authorization=AuthorizationContext(
                actor="local-os-user",
                capabilities=frozenset({Capability.WORKFLOW_READ}),
                authentication_method="test",
            ),
            correlation_id=CorrelationId.new(),
            idempotency_key="denied",
            input=DiagnosticInput(probe="storage"),
        )
        with pytest.raises(AuthorizationDenied):
            service.submit(command)
        assert service._repository.list((), 10) == ()
