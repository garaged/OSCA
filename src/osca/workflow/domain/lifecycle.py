from osca.workflow.api import DiagnosticRunState

_TRANSITIONS: dict[DiagnosticRunState, frozenset[DiagnosticRunState]] = {
    DiagnosticRunState.PENDING: frozenset(
        {DiagnosticRunState.RUNNING, DiagnosticRunState.CANCELLED}
    ),
    DiagnosticRunState.RUNNING: frozenset(
        {
            DiagnosticRunState.BLOCKED,
            DiagnosticRunState.SUCCEEDED,
            DiagnosticRunState.FAILED,
            DiagnosticRunState.CANCELLING,
            DiagnosticRunState.INTERRUPTED,
        }
    ),
    DiagnosticRunState.BLOCKED: frozenset(
        {DiagnosticRunState.PENDING, DiagnosticRunState.CANCELLED}
    ),
    DiagnosticRunState.CANCELLING: frozenset(
        {DiagnosticRunState.CANCELLED, DiagnosticRunState.INTERRUPTED}
    ),
    DiagnosticRunState.INTERRUPTED: frozenset(
        {DiagnosticRunState.PENDING, DiagnosticRunState.FAILED, DiagnosticRunState.CANCELLED}
    ),
    DiagnosticRunState.SUCCEEDED: frozenset(),
    DiagnosticRunState.FAILED: frozenset(),
    DiagnosticRunState.CANCELLED: frozenset(),
}


class InvalidTransition(ValueError):
    pass


def require_transition(source: DiagnosticRunState, target: DiagnosticRunState) -> None:
    if target not in _TRANSITIONS[source]:
        raise InvalidTransition(f"transition {source.value}->{target.value} is prohibited")
