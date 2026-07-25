# M3 Validation

- **Status:** Hosted Quality passing for current M3.3 slice
- **Branch:** `agent/m3-temporal-correctness`
- **Latest validated head:** `85a8927c7222f594f64cfd371473ce480c75df11`
- **Hosted Quality run:** `30136299539`

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

Hosted Quality run `30136299539` passed OpenSpec doctor, strict OpenSpec validation, secret scanning, Ruff, strict mypy, pytest, contract checks, migration checks, documentation link checks, and architecture checks for the current M3.3 slice.
