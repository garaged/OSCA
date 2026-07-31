# P7 Exit Review

- **Status:** Complete
- **Scope reviewed:** First demo research workflow, P6 payload consumption, deterministic metrics, CLI JSON output, static report output, documentation, and deferred boundaries
- **Decision:** Complete after PR #43 merge and hosted Quality

## Implementation evidence

P7 adds:

- `src/osca/demo_research/contracts.py`
- `src/osca/demo_research/services.py`
- `osca demo-research-report`
- `tests/test_p7_demo_research_workflow.py`

The workflow consumes canonical P6 OHLCV Parquet payloads and produces deterministic research reports with project/watchlist identity, return metrics, volatility, drawdown, simple moving averages, quality summary, and evidence-only observations.

## Deferred boundaries

P7 does not implement:

- Live provider calls.
- Credential materialization.
- Runtime provider routing.
- Production ingestion.
- ML execution.
- LLM execution.
- Recommendations or financial advice.
- Scheduler execution.
- Trading execution or real-capital orders.

## Validation

Hosted Quality passed for PR #43 before merge. Local validation was not executed in the connector-only implementation environment because no authenticated local checkout was available and `gh` is not installed.

Required hosted/local gates for acceptance:

- `ruff`
- `mypy`
- `pytest`
- architecture validation
- OpenSpec validation
- secret scanning
- hosted Quality

## Outcome

P7 is complete and P8 may consume its local demo workflow output.
