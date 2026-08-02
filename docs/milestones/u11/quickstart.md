# U11 Canonical First-Run Quickstart

This is the primary operator path for a local, evidence-only OSCA workflow. It keeps network access explicit and leaves recommendations, automatic promotion, brokers, autonomous execution, and real-capital orders disabled.

## 1. Initialize and diagnose

### zsh or Bash

```bash
PROFILE_ROOT=".osca/profile"

uv run osca init \
  --profile-root "$PROFILE_ROOT"

uv run osca doctor \
  --profile-root "$PROFILE_ROOT"
```

### PowerShell

```powershell
$ProfileRoot = ".osca/profile"

uv run osca init `
  --profile-root $ProfileRoot

uv run osca doctor `
  --profile-root $ProfileRoot
```

The generated configuration is versioned and local. The default workspace endpoint is `127.0.0.1:8765`, and the default data root is `<profile>/data`.

## 2A. Acquire no-cost Kraken history

Network access is never implicit.

### zsh or Bash

```bash
STORAGE_ROOT=".osca/profile/data"

uv run osca historical-data fetch \
  XBTUSD crypto kraken \
  --timeframe 1d \
  --expected-pair-key XXBTZUSD \
  --minimum-rows 250 \
  --network-access-enabled \
  --storage-root "$STORAGE_ROOT" \
  | tee .osca/u11-acquisition.json
```

### PowerShell

```powershell
$StorageRoot = ".osca/profile/data"

uv run osca historical-data fetch `
  XBTUSD crypto kraken `
  --timeframe 1d `
  --expected-pair-key XXBTZUSD `
  --minimum-rows 250 `
  --network-access-enabled `
  --storage-root $StorageRoot |
  Tee-Object -FilePath .osca/u11-acquisition.json
```

Use the returned `canonical_payload_uri` and `dataset_revision_id` in step 3.

## 2B. Offline CSV or Parquet fallback

```bash
uv run osca import-data \
  ./history.csv \
  AAPL \
  1d \
  --storage-root .osca/profile/data
```

The compatibility command `osca local-ohlcv-import` remains available through U13. New documentation and examples use `osca import-data`.

## 3. Run the retained research workflow

### zsh or Bash

```bash
PAYLOAD_PATH=".osca/profile/data/payloads/<REVISION>.parquet"
DATASET_REVISION_ID="<REVISION>"

uv run osca research-pipeline \
  "$PAYLOAD_PATH" \
  "$DATASET_REVISION_ID" \
  XBTUSD \
  1d \
  --storage-root .osca/profile/data \
  --reviewer "$USER" \
  --rationale "Approved for local evidence-only U11 acceptance." \
  --approve-local-validation
```

### PowerShell

```powershell
$PayloadPath = ".osca/profile/data/payloads/<REVISION>.parquet"
$DatasetRevisionId = "<REVISION>"

uv run osca research-pipeline `
  $PayloadPath `
  $DatasetRevisionId `
  XBTUSD `
  1d `
  --storage-root .osca/profile/data `
  --reviewer $env:USERNAME `
  --rationale "Approved for local evidence-only U11 acceptance." `
  --approve-local-validation
```

A diagnostic-ineligible result is valid when experiment and diagnostic evidence is retained and the pipeline stops before validation.

## 4. Snapshot or start the workspace

```bash
uv run osca workspace \
  --profile-root .osca/profile \
  --snapshot \
  | tee .osca/u11-workspace-snapshot.json
```

Start the local server by omitting `--snapshot`:

```bash
uv run osca workspace --profile-root .osca/profile
```

The primary command rejects non-loopback hosts. The workspace remains read-only and network-disabled.

## Canonical commands and compatibility window

| Canonical U11 command | Compatibility entry point | Planned compatibility window |
|---|---|---|
| `osca import-data` | `osca local-ohlcv-import` | Through U13 release-candidate acceptance |
| `osca analyze` | `osca demo-research-report` | Through U13 release-candidate acceptance |
| `osca backtest` | `osca backtest-paper-run` | Through U13 release-candidate acceptance |
| `osca research-pipeline` | `osca-research-pipeline` and `python -m osca.research_pipeline` | Through U13 release-candidate acceptance |
| `osca workspace` | `python -m osca.analyst_workspace` | Through U13 release-candidate acceptance |

Compatibility entry points must remain behaviorally equivalent during the window. Removal requires a later documented decision and release note.