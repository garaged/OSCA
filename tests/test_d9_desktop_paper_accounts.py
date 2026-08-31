from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from osca.desktop_api.contracts import DesktopRequest, DesktopResponse
from osca.desktop_api.paper_evaluation import PaperEvaluationDesktopService

RUN_ID = "a1000000-0000-0000-0000-000000000001"
ASSUMPTION_ID = "a2000000-0000-0000-0000-000000000002"
DRAFT_ID = "a3000000-0000-0000-0000-000000000003"
DATASET_ID = "a4000000-0000-0000-0000-000000000004"
UNKNOWN_ACCOUNT_ID = "a5000000-0000-0000-0000-000000000005"


def call(
    service: PaperEvaluationDesktopService,
    method: str,
    params: dict[str, Any],
) -> DesktopResponse:
    return service.handle(
        DesktopRequest(
            request_id=f"test-{method}",
            method=method,
            params=params,
        )
    )


def prepare(tmp_path: Path) -> tuple[PaperEvaluationDesktopService, Path, str]:
    service = PaperEvaluationDesktopService(state_root=tmp_path / "state")
    profile_root = tmp_path / "profile"
    created = call(service, "profile.create", {"profile_root": str(profile_root)})
    assert created.status == "ok", created.error
    portfolio = call(
        service,
        "portfolio.create",
        {
            "profile_root": str(profile_root),
            "name": "D9 account integration",
            "base_currency": "USD",
            "starting_cash": "10000",
        },
    )
    assert portfolio.status == "ok", portfolio.error
    assert portfolio.result is not None
    portfolio_id = cast(dict[str, Any], portfolio.result)["portfolio"]["portfolio_id"]
    return service, profile_root, str(portfolio_id)


def create_account(service: PaperEvaluationDesktopService, profile_root: Path) -> str:
    response = call(
        service,
        "paper.account.create",
        {
            "profile_root": str(profile_root),
            "name": "retained-paper-account",
            "base_currency": "USD",
            "created_at": "2026-08-21T08:00:00+00:00",
        },
    )
    assert response.status == "ok", response.error
    assert response.result is not None
    return str(response.result["account"]["paper_account_id"])


def bind_run(
    service: PaperEvaluationDesktopService,
    profile_root: Path,
    portfolio_id: str,
    account_id: str,
) -> DesktopResponse:
    return call(
        service,
        "paper.run.bind",
        {
            "profile_root": str(profile_root),
            "paper_run_id": RUN_ID,
            "paper_account_id": account_id,
            "portfolio_id": portfolio_id,
            "created_at": "2026-08-21T08:05:00+00:00",
        },
    )


def retain_assumptions_and_draft(
    service: PaperEvaluationDesktopService,
    profile_root: Path,
    portfolio_id: str,
    account_id: str,
) -> None:
    assumptions = call(
        service,
        "paper.assumptions.retain",
        {
            "profile_root": str(profile_root),
            "assumption_id": ASSUMPTION_ID,
            "max_volume_participation": "1",
            "created_at": "2026-08-21T08:10:00+00:00",
        },
    )
    assert assumptions.status == "ok", assumptions.error
    draft = call(
        service,
        "paper.order.draft.retain",
        {
            "profile_root": str(profile_root),
            "draft_id": DRAFT_ID,
            "draft_version": 1,
            "paper_run_id": RUN_ID,
            "paper_account_id": account_id,
            "portfolio_id": portfolio_id,
            "source_kind": "manual",
            "source_id": "retained-account-test",
            "instrument_id": "equity:XNAS:AAPL",
            "timeframe": "1h",
            "currency": "USD",
            "dataset_revision_id": DATASET_ID,
            "side": "buy",
            "order_type": "market",
            "quantity": "1",
            "assumption_id": ASSUMPTION_ID,
            "created_at": "2026-08-21T08:15:00+00:00",
        },
    )
    assert draft.status == "ok", draft.error


def test_d9_run_binding_requires_retained_m8_paper_account(tmp_path: Path) -> None:
    service, profile_root, portfolio_id = prepare(tmp_path)
    response = bind_run(service, profile_root, portfolio_id, UNKNOWN_ACCOUNT_ID)
    assert response.status == "error"
    assert response.error is not None
    assert response.error.code == "paper_account_not_found"


def test_d9_paper_account_create_list_survives_service_restart(tmp_path: Path) -> None:
    service, profile_root, _ = prepare(tmp_path)
    account_id = create_account(service, profile_root)

    restarted = PaperEvaluationDesktopService(state_root=tmp_path / "other-state")
    listed = call(restarted, "paper.account.list", {"profile_root": str(profile_root)})
    assert listed.status == "ok", listed.error
    assert listed.result is not None
    assert listed.result["accounts"][0]["account"]["paper_account_id"] == account_id
    assert listed.result["accounts"][0]["account"]["status"] == "active"
    assert listed.result["accounts"][0]["latest_control"] is None


def test_d9_retained_pause_blocks_confirmation_and_is_inspectable(tmp_path: Path) -> None:
    service, profile_root, portfolio_id = prepare(tmp_path)
    account_id = create_account(service, profile_root)
    bound = bind_run(service, profile_root, portfolio_id, account_id)
    assert bound.status == "ok", bound.error
    retain_assumptions_and_draft(service, profile_root, portfolio_id, account_id)

    paused = call(
        service,
        "paper.account.control.record",
        {
            "profile_root": str(profile_root),
            "paper_account_id": account_id,
            "action": "pause",
            "reason": "manual D9 pause test",
        },
    )
    assert paused.status == "ok", paused.error
    assert paused.result is not None
    assert paused.result["control_decision"]["can_process"] is False

    confirmed = call(
        service,
        "paper.order.confirm",
        {
            "profile_root": str(profile_root),
            "paper_run_id": RUN_ID,
            "draft_id": DRAFT_ID,
            "draft_version": 1,
            "confirmed_at": "2026-08-21T09:00:00+00:00",
        },
    )
    assert confirmed.status == "error"
    assert confirmed.error is not None
    assert "control" in confirmed.error.message.lower()

    inspected = call(
        service,
        "paper.run.inspect",
        {"profile_root": str(profile_root), "paper_run_id": RUN_ID},
    )
    assert inspected.status == "ok", inspected.error
    assert inspected.result is not None
    assert inspected.result["paper_account"]["paper_account_id"] == account_id
    assert inspected.result["control_decisions"][-1]["action"] == "pause"
    assert inspected.result["health_gates"] == []
