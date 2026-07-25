# M3 Validation

- **Status:** Hosted Quality passing for current M3.2 slice
- **Branch:** `agent/m3-temporal-correctness`
- **Latest validated head:** `d31722cfa5cd50b95ed7fdf36386534790f90eaa`
- **Hosted Quality run:** `30136153629`

## Required commands

```bash
pytest -q
ruff check .
mypy src tests
npm run openspec:doctor
npm run openspec:validate
```

## Current note

Local validation could not be run in this workspace because the private repository could not be cloned with shell credentials and the GitHub CLI is unavailable. Hosted Quality is the validation authority for this connector-backed slice until a credentialed checkout is available.

Hosted Quality run `30136153629` passed OpenSpec doctor, strict OpenSpec validation, secret scanning, Ruff, strict mypy, pytest, contract checks, migration checks, documentation link checks, and architecture checks for the current M3.2 slice.
