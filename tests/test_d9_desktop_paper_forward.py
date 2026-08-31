from __future__ import annotations

from pathlib import Path
from typing import Any, cast
from uuid import UUID

from osca.desktop_api.contracts import DesktopRequest, DesktopResponse
from osca.desktop_api.paper_forward import PaperForwardDesktopService

RUN_ID = "91000000-0000-0000-0000-000000000001"
ACCOUNT_ID = "92000000-0000-0000-0000-000000000002"
ASSUMPTION_ID = "93000000-0000-0000-0000-000000000003"
DRAFT_ID = "94000000-0000-0000-0000-000000000004"
DATASET_ID = "95000000-0000-0000-0000-000000000005"
BAR_ID = "96000000-0000-0000-0000-000000000006"


def call(
    service: PaperForwardDesktopService,
    method: str,
    params: dict[str, Any] | None = None,
) -> DesktopResponse:
    return service.handle(
        DesktopRequest(
            request_id=f"test-{method}",
            method=method,
            params=params or {},
        )
    )


def prepare(tmp_path: Path) -> tuple[PaperForwardDesktopService, Path, str]:
    service = PaperForwardDesktopService(state_root=tmp_path / "state")
    profile_root = tmp_path / "profile"
    created = call(service, "profile.create", {"profile_root": str(profile_root)})
    assert created.status == "ok", created.error
    portfolio = call(
        service,
        "portfolio.create",
        {
            "profile_root": str(profile_root),
            "name": "D9 simulated research",
            "base_currency": "USD",
            "starting_cash": "10000",
        },
    )
    assert portfolio.status == "ok", portfolio.error
    assert portfolio.result is not None
    portfolio_id = cast(dict[str, Any], portfolio.result)["portfolio"]["portfolio_id"]
    return service, profile_root, str(portfolio_id)


def bind_and_assumptions(
    service: PaperForwardDesktopService,
    profile_root: Path,
    portfolio_id: str,
) -> None:
    bound = call(
        service,
        "paper.run.bind",
        {
            "profile_root": str(profile_root),
            "paper_run_id": RUN_ID,
            "paper_account_id": ACCOUNT_ID,
            "portfolio_id": portfolio_id,
            "created_at": "2026-08-21T08:00:00+00:00",
        },
    )
    assert bound.status == "ok", bound.error
    assumptions = call(
        service,
        "paper.assumptions.retain",
        {
            "profile_root": str(profile_root),
            "assumption_id": ASSUMPTION_ID,
            "spread_bps": "0",
            "slippage_bps": "0",
            "fee_bps": "0",
            "flat_fee": "0",
            "max_volume_participation": "1",
            "require_volume": True,
            "created_at": "2026-08-21T08:00:00+00:00",
        },
    )
    assert assumptions.status == "ok", assumptions.error


def retain_draft(
    service: PaperForwardDesktopService,
    profile_root: Path,
    portfolio_id: str,
) -> DesktopResponse:
    return call(
        service,
        "paper.order.draft.retain",
        {
            "profile_root": str(profile_root),
            "draft_id": DRAFT_ID,
            "draft_version": 1,
            "paper_run_id": RUN_ID,
            "paper_account_id": ACCOUNT_ID,
            "portfolio_id": portfolio_id,
            "source_kind": "manual",
            "source_id": "desktop-manual-draft",
            "instrument_id": "equity:XNAS:AAPL",
            "timeframe": "1h",
            "currency": "USD",
            "dataset_revision_id": DATASET_ID,
            "side": "buy",
            "order_type": "market",
            "quantity": "10",
            "assumption_id": ASSUMPTION_ID,
            "created_at": "2026-08-21T08:30:00+00:00",
        },
    )


def bar_params(profile_root: Path, order_id: str) -> dict[str, Any]:
    return {
        "profile_root": str(profile_root),
        "order_id": order_id,
        "paper_account_id": ACCOUNT_ID,
        "paper_run_id": RUN_ID,
        "data_status": "healthy",
        "operational_status": "healthy",
        "evidence_id": BAR_ID,
        "instrument_id": "equity:XNAS:AAPL",
        "dataset_revision_id": DATASET_ID,
        "market_source_id": "local-synthetic-d9",
        "timeframe": "1h",
        "bar_started_at": "2026-08-21T10:00:00+00:00",
        "bar_ended_at": "2026-08-21T11:00:00+00:00",
        "available_at": "2026-08-21T11:00:01+00:00",
        "open": "100",
        "high": "102",
        "low": "99",
        "close": "101",
        "volume": "1000",
        "complete": True,
        "market_calendar_id": "XNAS",
        "session_open": True,
    }


def test_d9_desktop_composes_portfolio_and_simulated_order_flow(tmp_path: Path) -> None:
    service, profile_root, portfolio_id = prepare(tmp_path)
    bind_and_assumptions(service, profile_root, portfolio_id)
    draft = retain_draft(service, profile_root, portfolio_id)
    assert draft.status == "ok", draft.error

    before = call(
        service,
        "paper.run.inspect",
        {"profile_root": str(profile_root), "paper_run_id": RUN_ID},
    )
    assert before.status == "ok", before.error
    assert before.result is not None
    assert before.result["orders"] == []

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
    assert confirmed.status == "ok", confirmed.error
    assert confirmed.result is not None
    assert confirmed.result["simulated_only"] is True
    assert confirmed.result["broker_connections_enabled"] is False
    assert confirmed.result["live_order_execution"] is False
    order_id = str(confirmed.result["order"]["order_id"])

    step = call(service, "paper.order.process_bar", bar_params(profile_root, order_id))
    assert step.status == "ok", step.error
    assert step.result is not None
    assert step.result["step"]["fill"] is not None
    assert step.result["real_capital_execution_enabled"] is False

    inspected = call(
        PaperForwardDesktopService(state_root=tmp_path / "other-state"),
        "paper.run.inspect",
        {"profile_root": str(profile_root), "paper_run_id": RUN_ID},
    )
    assert inspected.status == "ok", inspected.error
    assert inspected.result is not None
    assert inspected.result["orders"][0]["status"] == "filled"
    assert inspected.result["orders"][0]["remaining_quantity"] == "0"
    assert len(inspected.result["orders"][0]["fills"]) == 1
    assert inspected.result["projection"]["positions"][0]["quantity"] == "10"


def test_d9_desktop_rejects_binary_float_authoritative_values(tmp_path: Path) -> None:
    service, profile_root, portfolio_id = prepare(tmp_path)
    bind_and_assumptions(service, profile_root, portfolio_id)
    response = call(
        service,
        "paper.order.draft.retain",
        {
            "profile_root": str(profile_root),
            "draft_id": DRAFT_ID,
            "paper_run_id": RUN_ID,
            "paper_account_id": ACCOUNT_ID,
            "portfolio_id": portfolio_id,
            "source_kind": "manual",
            "source_id": "float-rejected",
            "instrument_id": "equity:XNAS:AAPL",
            "timeframe": "1h",
            "currency": "USD",
            "dataset_revision_id": DATASET_ID,
            "side": "buy",
            "order_type": "market",
            "quantity": 10.25,
            "assumption_id": ASSUMPTION_ID,
        },
    )
    assert response.status == "error"
    assert response.error is not None
    assert response.error.code == "invalid_parameters"
    assert "exact decimal string or integer" in response.error.message


def test_d9_checkpoint_retry_and_descriptive_comparison(tmp_path: Path) -> None:
    service, profile_root, portfolio_id = prepare(tmp_path)
    bind_and_assumptions(service, profile_root, portfolio_id)
    checkpoint_params = {
        "profile_root": str(profile_root),
        "paper_run_id": RUN_ID,
        "idempotency_key": "desktop-after-bar",
        "last_processed_at": "2026-08-21T11:00:01+00:00",
        "source_event_ids": [BAR_ID],
    }
    first = call(service, "paper.checkpoint.record", checkpoint_params)
    retry = call(service, "paper.checkpoint.record", checkpoint_params)
    assert first.status == "ok", first.error
    assert retry.status == "ok", retry.error
    assert first.result == retry.result

    comparison = call(
        service,
        "paper.comparison.build",
        {
            "profile_root": str(profile_root),
            "backtest_result_id": 7,
            "paper_run_id": RUN_ID,
            "strategy_version_id": 3,
            "assumption_id": ASSUMPTION_ID,
            "backtest_started_at": "2026-01-01T00:00:00+00:00",
            "backtest_ended_at": "2026-06-01T00:00:00+00:00",
            "forward_started_at": "2026-08-01T00:00:00+00:00",
            "forward_ended_at": "2026-08-20T00:00:00+00:00",
            "compared_at": "2026-08-21T00:00:00+00:00",
            "metrics": [
                {
                    "name": "return",
                    "backtest_value": "0.10",
                    "forward_value": "0.04",
                    "unit": "ratio",
                    "methodology": "retained window return",
                }
            ],
            "methodology_differences": [
                "historical backtest and forward paper windows are distinct"
            ],
        },
    )
    assert comparison.status == "ok", comparison.error
    assert comparison.result is not None
    assert comparison.result["descriptive_only"] is True
    assert comparison.result["comparison"]["research_only"] is True
    assert comparison.result["recommendations_enabled"] is False


def test_d9_manual_order_has_no_live_destination_fields(tmp_path: Path) -> None:
    service, profile_root, portfolio_id = prepare(tmp_path)
    bind_and_assumptions(service, profile_root, portfolio_id)
    draft = retain_draft(service, profile_root, portfolio_id)
    assert draft.status == "ok", draft.error
    assert draft.result is not None
    serialized = str(draft.result).lower()
    assert "broker" in serialized
    assert draft.result["broker_connections_enabled"] is False
    assert draft.result["live_order_execution"] is False
    assert "destination" not in draft.result["draft"]
    assert UUID(str(draft.result["draft"]["draft_id"])) == UUID(DRAFT_ID)
