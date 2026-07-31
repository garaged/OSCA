# P12 User Testing Quickstart

## Install

```bash
uv sync --locked
```

Use a disposable local evidence root:

```bash
export OSCA_P12_ROOT=.osca/p12-manual
rm -rf "$OSCA_P12_ROOT"
```

## Deterministic local trend preview

```bash
uv run python -m osca.model_preview \
  --storage-root "$OSCA_P12_ROOT" \
  local-trend 100 101 103 104 106
```

Confirm:

- `status` is `succeeded`
- `provider_id` is `local`
- `model_id` is `ordinary-least-squares-trend`
- `estimated_cost_usd` is `0`
- `network_access_used`, `recommendations_enabled`, and `real_capital_orders_enabled` are `false`
- an `evidence_uri` is emitted

## Fixture-backed LLM analysis

```bash
uv run python -m osca.model_preview \
  --storage-root "$OSCA_P12_ROOT" \
  llm-fixture \
  --input "AAPL local evidence shows a positive fitted trend." \
  --fixture-response "The retained evidence has a positive historical trend; review limitations before use."
```

Confirm `status` is `review_required` and findings include:

- `fixture-backed-output`
- `human-review-required`
- `not-financial-advice`

## Fail-closed checks

A live-mode check must not call a provider:

```bash
uv run python -m osca.model_preview \
  --storage-root "$OSCA_P12_ROOT" \
  llm-live-check \
  --input "Evidence" \
  --provider-id example \
  --model-id example-model \
  --model-version 1.0.0
```

Confirm `status` is `provider_unavailable`, `network_access_used` is `false`, and the finding is `live-llm-executor-not-configured`.

To verify budget enforcement:

```bash
uv run python -m osca.model_preview \
  --storage-root "$OSCA_P12_ROOT" \
  local-trend --max-input-records 3 1 2 3 4
```

Confirm `status` is `budget_exceeded` and no output is emitted.

## Retained evidence

```bash
find "$OSCA_P12_ROOT/model-preview" -type f -name '*.json' -print
```

Review the files and confirm exact model identity, input digest, budget outcome, output or blocked state, findings, cost, latency, review status, and disabled recommendation/order boundaries are retained.
