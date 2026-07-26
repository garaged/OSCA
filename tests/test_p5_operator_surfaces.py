import json

from typer.testing import CliRunner

from osca.bootstrap.cli import app


runner = CliRunner()


def test_provider_catalog_list_includes_readiness() -> None:
    result = runner.invoke(app, ["provider-catalog-list", "--include-readiness"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    readiness_by_provider = {
        item["profile"]["provider_id"]: item["implementation_readiness"]["readiness"]
        for item in payload
    }

    assert readiness_by_provider["sec_edgar"] == "ready_for_contracts"
    assert readiness_by_provider["fred"] == "ready_for_contracts"
    assert readiness_by_provider["yahoo_finance_unofficial"] == "blocked"


def test_provider_adapter_contracts_report_deferred_boundaries() -> None:
    result = runner.invoke(app, ["provider-adapter-contracts"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    provider_ids = {contract["provider_id"] for contract in payload["contracts"]}
    assert provider_ids == {"sec_edgar", "fred"}
    assert payload["deferred_boundaries"] == {
        "live_provider_calls_enabled": False,
        "credential_materialization_enabled": False,
        "runtime_provider_routing_enabled": False,
        "production_ingestion_enabled": False,
        "real_capital_orders_enabled": False,
    }
    assert all(not contract["network_access_enabled"] for contract in payload["contracts"])


def test_provider_adapter_fixture_validation_reports_empty_fixture() -> None:
    result = runner.invoke(
        app,
        [
            "provider-adapter-validate-fixture",
            "sec_edgar",
            "sec_company_facts",
            "empty-company-facts",
            "CIK0000320193",
            "0" * 64,
            "0",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    assert payload["accepted"] is False
    assert payload["finding_ids"] == ["empty-fixture"]


def test_provider_promotion_status_remains_disabled_without_evidence() -> None:
    result = runner.invoke(app, ["provider-promotion-status"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    assert {provider["provider_id"] for provider in payload["providers"]} == {
        "twelve_data",
        "kraken",
    }
    assert all(not provider["provider_enabled"] for provider in payload["providers"])
    assert payload["deferred_boundaries"]["production_ingestion_enabled"] is False
