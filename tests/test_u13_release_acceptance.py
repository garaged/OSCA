from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from osca.release_acceptance import (
    ACCEPTANCE_AREAS,
    AcceptanceInput,
    evaluate_release_candidate,
)
from osca.release_acceptance_cli import app

runner = CliRunner()


def _document(*, status: str = "pass", defects: list[dict[str, object]] | None = None) -> dict[str, object]:
    return {
        "version": "1.0.0",
        "candidate_version": "0.1.0rc1",
        "source_commit": "a" * 40,
        "artifacts": ["dist/osca-0.1.0rc1-py3-none-any.whl"],
        "areas": [
            {
                "area_id": area,
                "status": status,
                "summary": f"{area} evidence passed",
                "evidence": [f"evidence/{area}.json"],
                **({"remediation": "Correct the acceptance defect."} if status != "pass" else {}),
            }
            for area in ACCEPTANCE_AREAS
        ],
        "defects": defects or [],
    }


def test_complete_matrix_is_eligible_without_side_effects() -> None:
    document = AcceptanceInput.model_validate(_document())

    result = evaluate_release_candidate(document)

    assert result["status"] == "eligible"
    assert result["tag_recommended"] is True
    assert result["recommended_tag"] == "v0.1.0rc1"
    assert result["tag_created"] is False
    assert result["publication_performed"] is False
    assert result["summary"]["passed"] == 16
    assert result["recommendations_enabled"] is False
    assert result["broker_connections_enabled"] is False
    assert result["real_capital_orders_enabled"] is False
    assert len(str(result["acceptance_sha256"])) == 64


def test_missing_acceptance_area_is_rejected() -> None:
    payload = _document()
    payload["areas"] = list(payload["areas"])[:-1]

    with pytest.raises(ValidationError, match="acceptance matrix mismatch"):
        AcceptanceInput.model_validate(payload)


def test_failed_area_denies_eligibility() -> None:
    payload = _document()
    payload["areas"][0]["status"] = "fail"
    payload["areas"][0]["remediation"] = "Fix installation acceptance."

    result = evaluate_release_candidate(AcceptanceInput.model_validate(payload))

    assert result["status"] == "ineligible"
    assert result["tag_recommended"] is False
    assert result["failed_areas"] == [ACCEPTANCE_AREAS[0]]


def test_open_high_defect_denies_eligibility() -> None:
    defects = [
        {
            "defect_id": "U13-001",
            "severity": "high",
            "status": "open",
            "summary": "Evidence mismatch",
        }
    ]

    result = evaluate_release_candidate(
        AcceptanceInput.model_validate(_document(defects=defects))
    )

    assert result["status"] == "ineligible"
    assert result["blocking_defects"] == ["U13-001"]


def test_open_medium_defect_requires_complete_disposition() -> None:
    defects = [
        {
            "defect_id": "U13-002",
            "severity": "medium",
            "status": "open",
            "summary": "Nonblocking documentation issue",
        }
    ]

    with pytest.raises(ValidationError, match="workaround, owner, and target milestone"):
        AcceptanceInput.model_validate(_document(defects=defects))


def test_cli_writes_machine_readable_result(tmp_path: Path) -> None:
    input_path = tmp_path / "matrix.json"
    output_path = tmp_path / "result.json"
    input_path.write_text(json.dumps(_document()), encoding="utf-8")

    result = runner.invoke(
        app,
        ["evaluate", "--input", str(input_path), "--output", str(output_path)],
    )

    assert result.exit_code == 0
    retained = json.loads(output_path.read_text(encoding="utf-8"))
    assert retained["status"] == "eligible"
    assert retained["tag_created"] is False
