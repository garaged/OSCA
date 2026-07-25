# M3 Validation

- **Status:** Pending hosted Quality
- **Branch:** `agent/m3-temporal-correctness`

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