from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from uuid import UUID

from osca.model_preview.contracts import (
    LLMAnalysisRequest,
    LocalTrendRequest,
    ModelPreviewEvidence,
    PreviewKind,
    PreviewStatus,
)


def run_local_trend_preview(request: LocalTrendRequest) -> ModelPreviewEvidence:
    started = time.perf_counter()
    input_digest = _digest(request.values)
    if len(request.values) > request.budget.max_input_records:
        return _evidence(
            request_id=request.request_id,
            kind=PreviewKind.LOCAL_TREND,
            status=PreviewStatus.BUDGET_EXCEEDED,
            provider_id="local",
            model_id="ordinary-least-squares-trend",
            model_version="1.0.0",
            input_digest=input_digest,
            findings=("input-record-budget-exceeded",),
            started=started,
        )

    count = len(request.values)
    x_mean = (count - 1) / 2
    y_mean = sum(request.values) / count
    denominator = sum((index - x_mean) ** 2 for index in range(count))
    slope = sum(
        (index - x_mean) * (value - y_mean)
        for index, value in enumerate(request.values)
    ) / denominator
    intercept = y_mean - slope * x_mean
    prediction = intercept + slope * count
    residuals = tuple(
        value - (intercept + slope * index)
        for index, value in enumerate(request.values)
    )
    mse = sum(value**2 for value in residuals) / count
    direction = "up" if slope > 0 else "down" if slope < 0 else "flat"
    output = (
        f"Deterministic local trend preview: direction={direction}; "
        f"next_value={prediction:.6f}. This is evidence, not a recommendation."
    )
    status = (
        PreviewStatus.SUCCEEDED
        if len(output) <= request.budget.max_output_characters
        else PreviewStatus.BUDGET_EXCEEDED
    )
    findings = () if status is PreviewStatus.SUCCEEDED else ("output-budget-exceeded",)
    return _evidence(
        request_id=request.request_id,
        kind=PreviewKind.LOCAL_TREND,
        status=status,
        provider_id="local",
        model_id="ordinary-least-squares-trend",
        model_version="1.0.0",
        input_digest=input_digest,
        output=output if status is PreviewStatus.SUCCEEDED else None,
        metrics={
            "record_count": count,
            "slope": slope,
            "intercept": intercept,
            "next_value": prediction,
            "mean_squared_error": mse,
            "direction": direction,
        },
        findings=findings,
        started=started,
    )


def run_llm_analysis_preview(request: LLMAnalysisRequest) -> ModelPreviewEvidence:
    started = time.perf_counter()
    input_digest = _digest(request.input_text)
    common = {
        "request_id": request.request_id,
        "kind": PreviewKind.LLM_ANALYSIS,
        "provider_id": request.provider_id,
        "model_id": request.model_id,
        "model_version": request.model_version,
        "input_digest": input_digest,
        "prompt_id": request.prompt_id,
        "prompt_version": request.prompt_version,
        "started": started,
    }
    if len(request.input_text) > request.budget.max_input_records:
        return _evidence(
            **common,
            status=PreviewStatus.BUDGET_EXCEEDED,
            findings=("input-budget-exceeded",),
        )
    if request.network_access_enabled:
        return _evidence(
            **common,
            status=PreviewStatus.PROVIDER_UNAVAILABLE,
            findings=("live-llm-executor-not-configured",),
        )
    if request.fixture_response is None:
        return _evidence(
            **common,
            status=PreviewStatus.POLICY_BLOCKED,
            findings=("network-disabled-and-no-fixture-response",),
        )
    if len(request.fixture_response) > request.budget.max_output_characters:
        return _evidence(
            **common,
            status=PreviewStatus.BUDGET_EXCEEDED,
            findings=("output-budget-exceeded",),
        )
    return _evidence(
        **common,
        status=PreviewStatus.REVIEW_REQUIRED,
        output=request.fixture_response,
        metrics={
            "input_characters": len(request.input_text),
            "output_characters": len(request.fixture_response),
        },
        findings=(
            "fixture-backed-output",
            "human-review-required",
            "not-financial-advice",
        ),
    )


def retain_preview_evidence(evidence: ModelPreviewEvidence, storage_root: Path) -> Path:
    directory = storage_root / "model-preview" / evidence.kind.value
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{evidence.preview_id}.json"
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(evidence.model_dump_json(indent=2), encoding="utf-8")
    temporary.replace(target)
    return target


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _evidence(
    *,
    request_id: UUID,
    kind: PreviewKind,
    status: PreviewStatus,
    provider_id: str,
    model_id: str,
    model_version: str,
    input_digest: str,
    started: float,
    prompt_id: str | None = None,
    prompt_version: str | None = None,
    output: str | None = None,
    metrics: dict[str, float | int | str | bool] | None = None,
    findings: tuple[str, ...] = (),
) -> ModelPreviewEvidence:
    return ModelPreviewEvidence(
        request_id=request_id,
        kind=kind,
        status=status,
        provider_id=provider_id,
        model_id=model_id,
        model_version=model_version,
        input_digest=input_digest,
        prompt_id=prompt_id,
        prompt_version=prompt_version,
        output=output,
        metrics=metrics or {},
        findings=findings,
        estimated_cost_usd=0,
        latency_ms=max(0, round((time.perf_counter() - started) * 1000)),
    )
