from itertools import product

import pytest
from hypothesis import given
from hypothesis import strategies as st

from osca.workflow.api import DiagnosticRunState
from osca.workflow.domain import InvalidTransition, require_transition

ALLOWED = {
    (DiagnosticRunState.PENDING, DiagnosticRunState.RUNNING),
    (DiagnosticRunState.PENDING, DiagnosticRunState.CANCELLED),
    (DiagnosticRunState.RUNNING, DiagnosticRunState.BLOCKED),
    (DiagnosticRunState.RUNNING, DiagnosticRunState.SUCCEEDED),
    (DiagnosticRunState.RUNNING, DiagnosticRunState.FAILED),
    (DiagnosticRunState.RUNNING, DiagnosticRunState.CANCELLING),
    (DiagnosticRunState.RUNNING, DiagnosticRunState.INTERRUPTED),
    (DiagnosticRunState.BLOCKED, DiagnosticRunState.PENDING),
    (DiagnosticRunState.BLOCKED, DiagnosticRunState.CANCELLED),
    (DiagnosticRunState.CANCELLING, DiagnosticRunState.CANCELLED),
    (DiagnosticRunState.CANCELLING, DiagnosticRunState.INTERRUPTED),
    (DiagnosticRunState.INTERRUPTED, DiagnosticRunState.PENDING),
    (DiagnosticRunState.INTERRUPTED, DiagnosticRunState.FAILED),
    (DiagnosticRunState.INTERRUPTED, DiagnosticRunState.CANCELLED),
}


@given(st.sampled_from(list(DiagnosticRunState)), st.sampled_from(list(DiagnosticRunState)))
def test_transition_graph_is_complete(
    source: DiagnosticRunState, target: DiagnosticRunState
) -> None:
    if (source, target) in ALLOWED:
        require_transition(source, target)
    else:
        with pytest.raises(InvalidTransition):
            require_transition(source, target)


def test_every_state_pair_is_classified() -> None:
    assert len(list(product(DiagnosticRunState, repeat=2))) == 64
