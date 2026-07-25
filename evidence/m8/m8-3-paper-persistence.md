# M8.3 Paper Persistence Evidence

- **Status:** Pending hosted validation
- **Slice:** M8.3
- **Branch:** agent/m8-paper-evaluation-automation
- **Baseline:** M8.2 verified head 8326ab6db7ab2e2c29af4a740ea8fbc41aed1247

## Evidence retained

M8.3 adds SQLite metadata persistence for paper accounts, approved candidates, evaluation requests, health gates, control decisions, schedules, checkpoints, recovery decisions, and forward comparisons.

## Validation plan

Hosted Quality must validate persistence round trips, account/run scoped queries, OpenSpec, secret scanning, Ruff, strict mypy, migrations, links, and architecture checks.
