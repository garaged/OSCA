from __future__ import annotations

import json
from pathlib import Path

from osca.model_preview import (
    LLMAnalysisRequest,
    LocalTrendRequest,
    PreviewBudget,
    PreviewStatus,
    retain_preview_evidence,
    run_llm_analysis_preview,
    run_local_trend_preview,
)
from osca.model_preview.cli import main


def _budget(**overrides: object) -> PreviewBudget:
    values: dict[str, object] = {
        "max_input_records": 100,
        "max_output_characters": 1000,
        "max_cost_usd": 0,
        "max_latency_ms": 30_000,
    }
    values.update(overrides)
    return PreviewBudget.model_validate(values)


def test_local_trend_preview_is_deterministic_and_not_advice() -> None:
    request = LocalTrendRequest(values=(1.0, 2.0, 3.0, 4.0), budget=_budget())

    evidence = run_local_trend_preview(request)

    assert evidence.status is PreviewStatus.SUCCEEDED
    assert evidence.metrics["direction"] == "up"
    assert evidence.metrics["next_value"] == 5.0
    assert evidence.estimated_cost_usd == 0
    assert evidence.network_access_used is False
    assert evidence.recommendations_enabled is False
    assert "not a recommendation" in (evidence.output or "")


def test_local_trend_preview_fails_closed_on_input_budget() -> None:
    request = LocalTrendRequest(
        values=(1.0, 2.0, 3.0, 4.0),
        budget=_budget(max_input_records=3),
    )

    evidence = run_local_trend_preview(request)

    assert evidence.status is PreviewStatus.BUDGET_EXCEEDED
    assert evidence.output is None


def test_llm_fixture_preview_requires_human_review() -> None:
    evidence = run_llm_analysis_preview(
        LLMAnalysisRequest(
            input_text="Retained deterministic research evidence.",
            prompt_id="analyst-summary",
            prompt_version="1.0.0",
            provider_id="fixture",
            model_id="fixture-model",
            model_version="1.0.0",
            budget=_budget(),
            fixture_response="A cautious fixture-backed summary.",
        )
    )

    assert evidence.status is PreviewStatus.REVIEW_REQUIRED
    assert evidence.output == "A cautious fixture-backed summary."
    assert "human-review-required" in evidence.findings
    assert evidence.network_access_used is False


def test_llm_preview_without_fixture_is_policy_blocked() -> None:
    evidence = run_llm_analysis_preview(
        LLMAnalysisRequest(
            input_text="Evidence",
            prompt_id="analyst-summary",
            prompt_version="1.0.0",
            provider_id="local",
            model_id="none",
            model_version="1.0.0",
            budget=_budget(),
        )
    )

    assert evidence.status is PreviewStatus.POLICY_BLOCKED
    assert evidence.output is None


def test_live_llm_check_is_unavailable_without_executor() -> None:
    evidence = run_llm_analysis_preview(
        LLMAnalysisRequest(
            input_text="Evidence",
            prompt_id="analyst-summary",
            prompt_version="1.0.0",
            provider_id="example",
            model_id="example-model",
            model_version="1.0.0",
            budget=_budget(max_cost_usd=1),
            network_access_enabled=True,
        )
    )

    assert evidence.status is PreviewStatus.PROVIDER_UNAVAILABLE
    assert evidence.network_access_used is False
    assert "live-llm-executor-not-configured" in evidence.findings


def test_preview_evidence_is_retained_atomically(tmp_path: Path) -> None:
    evidence = run_local_trend_preview(
        LocalTrendRequest(values=(3.0, 2.0, 1.0), budget=_budget())
    )

    path = retain_preview_evidence(evidence, tmp_path)

    assert path.is_file()
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["preview_id"] == str(evidence.preview_id)
    assert not path.with_suffix(".json.tmp").exists()


def test_cli_emits_evidence_uri(tmp_path: Path, capsys: object) -> None:
    result = main(
        [
            "--storage-root",
            str(tmp_path),
            "local-trend",
            "1",
            "2",
            "3",
        ]
    )

    assert result == 0
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    document = json.loads(captured.out)
    assert document["status"] == "succeeded"
    assert document["evidence_uri"].startswith("file:")
