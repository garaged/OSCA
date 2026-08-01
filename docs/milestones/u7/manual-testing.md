# U7 Manual Acceptance

## Purpose

Verify the local model-to-research validation path on a clean machine without enabling network access, model serving, broker connectivity, or orders.

## Preconditions

- Python 3.13 and `uv` are installed.
- The repository is checked out at the U7 candidate commit.
- `uv sync --locked` completes.
- A governed OHLCV Parquet payload is available.
- A retained U5 classification experiment JSON and matching U6 diagnostic JSON are available.
- A named human has explicitly approved local F2 validation.

## CLI review

1. Assemble a `ModelValidationRequest` JSON containing the retained experiment, matching diagnostic, promotion decision, payload path, and explicit signal assumptions.
2. Run:

   ```bash
   uv run python -m osca.model_validation request.json > validation-result.json
   ```

3. Confirm the result records:
   - matching experiment and diagnostic evidence;
   - promotion decision identifier;
   - signal-rule version, threshold, latency, transaction cost, slippage, and missing-prediction policy;
   - aligned and skipped predictions;
   - prediction and execution timestamps;
   - gross, cost, and net return for every event;
   - final equity, drawdown, buy-and-hold comparison, and evidence digest;
   - disabled serving, automatic promotion, recommendation, broker, and real-capital flags.

## Negative review

Repeat with each of the following and confirm the command fails before producing a validation result:

- promotion decision changed to `approved: false`;
- diagnostic status changed from `eligible_for_f2_validation`;
- diagnostic experiment identifier changed;
- regression experiment supplied;
- payload removed or changed so no prediction aligns to an executable bar.

## Paper challenger review

Set `request_paper_challenger` to true and provide a second named reviewer and rationale. Confirm the result becomes `paper_challenger_approved`, remains `local-evidence-only`, and still reports broker and real-capital execution as false.

## Workspace review

Start the existing loopback-only analyst workspace and submit the same request to:

```text
POST /api/model-validation/run
```

Confirm the API result matches the CLI evidence and `/health` reports model research validation enabled while automatic promotion and broker execution remain disabled.
