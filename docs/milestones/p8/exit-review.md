# P8 Exit Review

- **Status:** Complete
- **Scope reviewed:** Built-in transparent strategy, local payload backtest execution, paper-evaluation evidence record, CLI JSON output, static report output, documentation, compatibility, manual workflow, and deferred boundaries
- **Decision:** Accepted after hosted Quality, merge follow-ups, and successful manual validation
- **Reviewed:** 2026-07-31

## Implementation evidence

P8 adds:

- `src/osca/backtest_paper/contracts.py`
- `src/osca/backtest_paper/services.py`
- `osca backtest-paper-run`
- `tests/test_p8_backtest_paper_happy_path.py`

The workflow consumes canonical P6 OHLCV Parquet payloads and produces deterministic evidence for a transparent long-only SMA trend strategy. It records strategy return, buy-and-hold comparison, max drawdown, exposure, evidence trades, and a linked paper-evaluation record.

## Hosted validation evidence

- PR #44 implemented P8 and passed hosted Quality.
- PR #45 strict-mypy regression follow-up passed Quality run `30594286817`.
- PR #46 Python 3.13 boundary passed Quality run `30594598842`.
- PR #47 macOS ARM64 lock coverage passed Quality run `30595013370`.
- PR #48 strict-mypy coverage passed Quality run `30595313371`.
- PR #49 manual quickstart correction passed Quality run `30595759235`.
- PR #50 ten-bar backtest fixture correction passed Quality run `30596825840`.
- PR #51 fixture guard clarification passed Quality run `30600239512`.

The hosted gates covered Ruff, strict mypy, pytest/contracts/migrations/links/architecture, OpenSpec validation, and secret scanning as applicable to each follow-up.

## Manual validation evidence

The final macOS Apple Silicon/Python 3.13 workflow:

1. Recreated the environment with `uv sync`.
2. Passed `uv run ruff check .`, `uv run mypy src tests`, and `uv run pytest`.
3. Imported `tests/fixtures/local_ohlcv/aapl_backtest_daily.csv` and confirmed `row_count: 10`.
4. Ran the P7 research report and P8 backtest-to-paper report from the emitted `payload_uri`.
5. Processed 10 AAPL daily bars and produced 3 simulated evidence trades.
6. Retained paper run `aaad0f77-aebd-455b-832a-9df9feafb680` in `local-evidence-only` mode.

The retained report is [P8 manual backtest-to-paper evidence](../../../evidence/p8/manual-backtest-paper-report.md).

## Documentation corrections verified

- `local-ohlcv-import` positional arguments are documented correctly.
- `--storage-root` is the supported storage option.
- The full P8 workflow uses the ten-row `aapl_backtest_daily.csv` fixture.
- Shell-safe extraction of `payload_uri` replaces unsafe placeholder text.
- The five-bar backtest minimum and `row_count: 10` precondition are explicit.

## Deferred boundaries

P8 does not implement:

- Live paper broker integration.
- Autonomous execution.
- Live provider calls or runtime provider routing.
- Credential materialization.
- Production ingestion.
- Recommendations or financial advice.
- Trading execution or real-capital orders.

## Outcome

REQ-0212 through REQ-0218 are verified for the approved P8 scope. P8 is complete, and P9 is the next governed implementation milestone.
