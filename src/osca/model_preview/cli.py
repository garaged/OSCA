from __future__ import annotations

import argparse
import json
from pathlib import Path

from osca.model_preview import (
    LLMAnalysisRequest,
    LocalTrendRequest,
    PreviewBudget,
    retain_preview_evidence,
    run_llm_analysis_preview,
    run_local_trend_preview,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="OSCA opt-in model-assisted previews")
    parser.add_argument("--storage-root", type=Path, default=Path(".osca"))
    subparsers = parser.add_subparsers(dest="command", required=True)

    trend = subparsers.add_parser("local-trend")
    trend.add_argument("values", nargs="+", type=float)
    _add_budget_arguments(trend)

    llm = subparsers.add_parser("llm-fixture")
    llm.add_argument("--input", required=True)
    llm.add_argument("--fixture-response", required=True)
    llm.add_argument("--prompt-id", default="analyst-summary")
    llm.add_argument("--prompt-version", default="1.0.0")
    llm.add_argument("--provider-id", default="fixture")
    llm.add_argument("--model-id", default="fixture-model")
    llm.add_argument("--model-version", default="1.0.0")
    _add_budget_arguments(llm)

    live = subparsers.add_parser("llm-live-check")
    live.add_argument("--input", required=True)
    live.add_argument("--prompt-id", default="analyst-summary")
    live.add_argument("--prompt-version", default="1.0.0")
    live.add_argument("--provider-id", required=True)
    live.add_argument("--model-id", required=True)
    live.add_argument("--model-version", required=True)
    _add_budget_arguments(live)

    args = parser.parse_args(argv)
    budget = _budget(args)
    if args.command == "local-trend":
        evidence = run_local_trend_preview(
            LocalTrendRequest(values=tuple(args.values), budget=budget)
        )
    else:
        evidence = run_llm_analysis_preview(
            LLMAnalysisRequest(
                input_text=args.input,
                prompt_id=args.prompt_id,
                prompt_version=args.prompt_version,
                provider_id=args.provider_id,
                model_id=args.model_id,
                model_version=args.model_version,
                budget=budget,
                fixture_response=(
                    args.fixture_response if args.command == "llm-fixture" else None
                ),
                network_access_enabled=args.command == "llm-live-check",
            )
        )
    path = retain_preview_evidence(evidence, args.storage_root)
    document = evidence.model_dump(mode="json")
    document["evidence_uri"] = path.resolve().as_uri()
    print(json.dumps(document, indent=2, sort_keys=True))
    return 0


def _add_budget_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--max-input-records", type=int, default=10_000)
    parser.add_argument("--max-output-characters", type=int, default=8_000)
    parser.add_argument("--max-cost-usd", type=float, default=0)
    parser.add_argument("--max-latency-ms", type=int, default=30_000)


def _budget(args: argparse.Namespace) -> PreviewBudget:
    return PreviewBudget(
        max_input_records=args.max_input_records,
        max_output_characters=args.max_output_characters,
        max_cost_usd=args.max_cost_usd,
        max_latency_ms=args.max_latency_ms,
    )


if __name__ == "__main__":
    raise SystemExit(main())
