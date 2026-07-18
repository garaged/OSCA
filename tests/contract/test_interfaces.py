import json

from fastapi.testclient import TestClient
from typer.testing import CliRunner

from osca.bootstrap.cli import app as cli_app
from osca.bootstrap.web import app as web_app


def test_api_cli_and_web_expose_equivalent_readiness() -> None:
    api_response = TestClient(web_app).get("/api/v1/readiness")
    cli_response = CliRunner().invoke(cli_app, ["readiness"])
    web_response = TestClient(web_app).get("/health")

    assert api_response.status_code == 200
    assert cli_response.exit_code == 0
    assert web_response.status_code == 200

    api_payload = api_response.json()
    cli_payload = json.loads(cli_response.stdout)

    for field in ("contract_family", "contract_version", "product_version", "state"):
        assert cli_payload[field] == api_payload[field]

    assert cli_payload["components"] == api_payload["components"]
    assert f"State: {api_payload['state']}" in web_response.text


def test_openapi_declares_versioned_readiness_contract() -> None:
    document = TestClient(web_app).get("/openapi.json").json()
    operation = document["paths"]["/api/v1/readiness"]["get"]
    assert operation["responses"]["200"]["content"]["application/json"]
    assert "ReadinessSnapshot" in document["components"]["schemas"]

