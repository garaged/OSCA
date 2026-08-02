# U8 Real-World Governed Research Quickstart

## Purpose

Run the implemented U5-U7 research path as one local, human-gated workflow and retain every artifact under the same storage root used by the analyst workspace.

This workflow is evidence-only. It does not enable investment recommendations, live model serving, automatic promotion, broker connectivity, autonomous execution, or real-capital orders.

## Prerequisites

- Python 3.13 and the locked OSCA environment
- a governed Parquet OHLCV payload created by `osca local-ohlcv-import`
- its dataset revision ID
- enough history for point-in-time train, validation, and test splits
- a named human reviewer and written local-validation rationale

## Inspect the command

```bash
uv run osca-research-pipeline --help
```

The command intentionally exposes the accepted classification model through the workflow rather than requiring operators to discover the internal enum value `logistic_classification`.

## Run the workflow

```bash
uv run osca-research-pipeline \
  .osca/real-world-test/real-storage/payloads/<revision>.parquet \
  <revision> \
  AAPL \
  1d \
  --storage-root .osca/real-world-test/real-storage \
  --reviewer maxvaldez \
  --rationale "Approved for local evidence-only validation after reviewing the governed dataset and diagnostic boundaries." \
  --approve-local-validation
```

The approval flag is mandatory. Omitting it fails before any research-evidence directory is created.

## Retained evidence

Each run creates a unique directory:

```text
<storage-root>/research-evidence/<run-id>/
├── experiment.json
├── diagnostic.json
├── manifest.json
├── validation-request.json   # only when U6 is eligible
└── validation-result.json    # only when U6 is eligible
```

A diagnostic that is not `eligible_for_f2_validation` is a valid fail-closed result. The experiment, diagnostic, and manifest remain available for review, but U7 is not run.

## Analyst workspace

Start the workspace with the same storage root:

```bash
uv run python -m osca.analyst_workspace \
  --storage-root .osca/real-world-test/real-storage \
  --host 127.0.0.1 \
  --port 8765
```

Open `http://127.0.0.1:8765/`. Because research evidence now lives under the configured root, the recursive workspace artifact discovery includes the retained experiment, diagnostic, request, result, and manifest instead of showing only the imported dataset.

Use a different port when `8765` is already occupied.

## Expected safety fields

Every completed manifest and validation result must retain these values:

```text
event_driven_validation_enabled: true
live_model_serving_enabled: false
automatic_promotion_enabled: false
recommendations_enabled: false
broker_execution_enabled: false
real_capital_execution_enabled: false
```

Any contrary result is release-blocking.

## Real-world baseline established on August 1, 2026

The first end-to-end AAPL run used 1,255 daily bars from August 2, 2021 through July 31, 2026. The classification experiment and U6 diagnostic completed, U6 returned `eligible_for_f2_validation`, and human-gated U7 validation completed with latency, transaction-cost, and slippage assumptions.

The model-derived strategy returned approximately 14.08% versus approximately 31.98% for buy-and-hold over the aligned test window. This underperformance is retained research evidence, not a failed application test and not an investment recommendation.
