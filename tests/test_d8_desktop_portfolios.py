from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from osca.desktop_api.contracts import DesktopRequest, DesktopResponse
from osca.desktop_api.portfolio_accounting import PortfolioAccountingDesktopService


def _call(
    service: PortfolioAccountingDesktopService,
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


def _profile(
    tmp_path: Path,
    name: str = "profile",
) -> tuple[PortfolioAccountingDesktopService, Path]:
    service = PortfolioAccountingDesktopService(state_root=tmp_path / "state")
    profile_root = tmp_path / name
    created = _call(service, "profile.create", {"profile_root": str(profile_root)})
    assert created.status == "ok", created.error
    return service, profile_root


def _create_portfolio(
    service: PortfolioAccountingDesktopService,
    profile_root: Path,
    *,
    name: str = "Research USD",
) -> dict[str, Any]:
    response = _call(
        service,
        "portfolio.create",
        {
            "profile_root": str(profile_root),
            "name": name,
            "base_currency": "USD",
            "starting_cash": "5000.01",
        },
    )
    assert response.status == "ok", response.error
    assert response.result is not None
    return cast(dict[str, Any], response.result)


def test_desktop_supports_multiple_independent_portfolios(tmp_path: Path) -> None:
    service, profile_root = _profile(tmp_path)
    first = _create_portfolio(service, profile_root, name="First")
    second = _create_portfolio(service, profile_root, name="Second")

    first_id = first["portfolio"]["portfolio_id"]
    second_id = second["portfolio"]["portfolio_id"]
    assert first_id != second_id
    assert first["projection"]["cash_by_currency"] == {"USD": "5000.01"}

    listed = _call(service, "portfolio.list", {"profile_root": str(profile_root)})
    assert listed.status == "ok", listed.error
    assert listed.result is not None
    identities = {item["portfolio_id"] for item in listed.result["portfolios"]}
    assert identities == {first_id, second_id}
    assert listed.result["network_access_enabled"] is False
    assert listed.result["recommendations_enabled"] is False
    assert listed.result["real_capital_execution_enabled"] is False


def test_desktop_rejects_binary_float_accounting_input(tmp_path: Path) -> None:
    service, profile_root = _profile(tmp_path)
    response = _call(
        service,
        "portfolio.create",
        {
            "profile_root": str(profile_root),
            "name": "Float rejected",
            "starting_cash": 100.25,
        },
    )

    assert response.status == "error"
    assert response.error is not None
    assert response.error.code == "invalid_parameters"
    assert "exact decimal string or integer" in response.error.message


def test_desktop_records_events_and_returns_journal_evidence(tmp_path: Path) -> None:
    service, profile_root = _profile(tmp_path)
    created = _create_portfolio(service, profile_root)
    portfolio_id = created["portfolio"]["portfolio_id"]

    acquired = _call(
        service,
        "portfolio.acquisition.record",
        {
            "profile_root": str(profile_root),
            "portfolio_id": portfolio_id,
            "instrument_id": "equity:XNAS:AAPL",
            "quantity": "5",
            "unit_price": "100",
            "currency": "USD",
            "fee": "1",
            "source_id": "manual-buy-1",
        },
    )
    assert acquired.status == "ok", acquired.error
    assert acquired.result is not None
    assert acquired.result["projection"]["cash_by_currency"] == {"USD": "4499.01"}
    assert acquired.result["projection"]["positions"][0]["quantity"] == "5"

    fetched = _call(
        service,
        "portfolio.get",
        {"profile_root": str(profile_root), "portfolio_id": portfolio_id},
    )
    assert fetched.status == "ok", fetched.error
    assert fetched.result is not None
    assert len(fetched.result["events"]) == 2
    assert len(fetched.result["journal"]) == 2
    for transaction in fetched.result["journal"]:
        debit = sum(
            float(item["amount"])
            for item in transaction["postings"]
            if item["side"] == "debit"
        )
        credit = sum(
            float(item["amount"])
            for item in transaction["postings"]
            if item["side"] == "credit"
        )
        assert debit == credit
    assert fetched.result["broker_connections_enabled"] is False
    assert fetched.result["live_order_execution"] is False


def test_desktop_ambiguous_disposal_fails_closed_then_accepts_allocation(
    tmp_path: Path,
) -> None:
    service, profile_root = _profile(tmp_path)
    portfolio_id = _create_portfolio(service, profile_root)["portfolio"]["portfolio_id"]
    for index, unit_price in enumerate(("100", "110"), start=1):
        response = _call(
            service,
            "portfolio.acquisition.record",
            {
                "profile_root": str(profile_root),
                "portfolio_id": portfolio_id,
                "instrument_id": "AAPL",
                "quantity": "5",
                "unit_price": unit_price,
                "currency": "USD",
                "source_id": f"buy-{index}",
            },
        )
        assert response.status == "ok", response.error

    ambiguous = _call(
        service,
        "portfolio.disposal.record",
        {
            "profile_root": str(profile_root),
            "portfolio_id": portfolio_id,
            "instrument_id": "AAPL",
            "quantity": "2",
            "unit_price": "120",
            "currency": "USD",
            "source_id": "sell-ambiguous",
        },
    )
    assert ambiguous.status == "error"
    assert ambiguous.error is not None
    assert ambiguous.error.code == "application_error"
    assert "explicit lot allocations" in ambiguous.error.message

    fetched = _call(
        service,
        "portfolio.get",
        {"profile_root": str(profile_root), "portfolio_id": portfolio_id},
    )
    assert fetched.result is not None
    lot_id = fetched.result["projection"]["lots"][0]["lot_id"]
    allocated = _call(
        service,
        "portfolio.disposal.record",
        {
            "profile_root": str(profile_root),
            "portfolio_id": portfolio_id,
            "instrument_id": "AAPL",
            "quantity": "2",
            "unit_price": "120",
            "currency": "USD",
            "source_id": "sell-allocated",
            "lot_allocations": {lot_id: "2"},
        },
    )
    assert allocated.status == "ok", allocated.error


def test_desktop_clone_reset_export_restore_preserve_source(tmp_path: Path) -> None:
    service, profile_root = _profile(tmp_path, "source-profile")
    created = _create_portfolio(service, profile_root)
    portfolio_id = created["portfolio"]["portfolio_id"]
    acquired = _call(
        service,
        "portfolio.acquisition.record",
        {
            "profile_root": str(profile_root),
            "portfolio_id": portfolio_id,
            "instrument_id": "AAPL",
            "quantity": "5",
            "unit_price": "100",
            "currency": "USD",
            "source_id": "buy-1",
        },
    )
    assert acquired.status == "ok", acquired.error

    cloned = _call(
        service,
        "portfolio.clone",
        {
            "profile_root": str(profile_root),
            "portfolio_id": portfolio_id,
            "name": "Clone",
        },
    )
    assert cloned.status == "ok", cloned.error
    assert cloned.result is not None
    assert cloned.result["portfolio"]["source_portfolio_id"] == portfolio_id
    assert cloned.result["projection"]["positions"][0]["quantity"] == "5"

    reset = _call(
        service,
        "portfolio.reset",
        {
            "profile_root": str(profile_root),
            "portfolio_id": portfolio_id,
            "name": "Reset successor",
            "starting_cash": "2000",
        },
    )
    assert reset.status == "ok", reset.error
    assert reset.result is not None
    assert reset.result["portfolio"]["source_portfolio_id"] == portfolio_id
    assert reset.result["projection"]["positions"] == []

    exported = _call(
        service,
        "portfolio.export.prepare",
        {"profile_root": str(profile_root), "portfolio_id": portfolio_id},
    )
    assert exported.status == "ok", exported.error
    assert exported.result is not None
    export_path = Path(exported.result["output_path"])
    assert export_path.is_file()
    assert exported.result["provider_data_embedded"] is False

    target_service, target_root = _profile(tmp_path, "target-profile")
    restored = _call(
        target_service,
        "portfolio.restore",
        {"profile_root": str(target_root), "input_path": str(export_path)},
    )
    assert restored.status == "ok", restored.error
    assert restored.result is not None
    assert restored.result["portfolio"]["portfolio_id"] == portfolio_id
    assert restored.result["projection"]["positions"][0]["quantity"] == "5"

    source_after = _call(
        service,
        "portfolio.get",
        {"profile_root": str(profile_root), "portfolio_id": portfolio_id},
    )
    assert source_after.result is not None
    assert source_after.result["projection"]["positions"][0]["quantity"] == "5"
