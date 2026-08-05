# D14 Intent — Alerts, Scheduling, and Optional Personal Server

## Outcome
Users can create reliable typed workflows and alerts, observe their execution, recover from interruption, and optionally run supported workflows on a securely configured personal server.

## Scope
Typed workflow definitions, market-calendar-aware schedules, alerts, desktop notifications, job history, retries, cancellation, checkpoints, recovery, optional email/Slack/webhook channels, backup, and personal-server health.

## Non-goals
Arbitrary command scheduling, unattended live trading, hidden background execution, or insecure internet exposure.

## Dependencies
D3 acquisition, D6 projects, D9 paper evaluation, and accepted personal-server contracts.

## Risks
Duplicate runs, missed market sessions, notification leakage, credential exposure, arbitrary-command inheritance, and unsafe remote access.

## Exit intent
General command tuples are replaced by typed workflows; execution is idempotent and observable; notification channels are separately configured; personal-server use requires authenticated encrypted connections, backup/recovery, and explicit network guidance; no schedule can reach live execution.
