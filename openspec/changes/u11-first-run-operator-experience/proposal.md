# Proposal: U11 First-Run and Unified Operator Experience

## Why

OSCA's operator capabilities exist, but a new user still needs internal Python module commands, prior repository knowledge, or hand-authored configuration to initialize a profile, diagnose readiness, and start the read-only workspace. This prevents the U9/U10 workflow from being a coherent first-run product experience.

## What changes

- Add primary `osca init`, `osca doctor`, and `osca workspace` commands.
- Add safe versioned local operator configuration with explicit disabled safety boundaries.
- Add structured corrective diagnostics for runtime, storage, SQLite, Parquet, ports, and retained evidence.
- Promote remaining operator-visible workflow stages or provide documented compatibility aliases.
- Add shell-safe quickstarts for zsh, Bash, and PowerShell.
- Preserve loopback-only workspace access and explicit network opt-in for provider acquisition.

## Non-goals

U11 does not enable recommendations, automatic model promotion, live model serving, broker or exchange connectivity, autonomous execution, real-capital orders, remote writes, or public evidence sharing.

## Exit outcome

A new user can initialize OSCA, diagnose readiness, acquire or import data, run the retained research workflow, and start the read-only workspace through the primary `osca` CLI without `python -m osca.*` commands or hand-authored JSON.