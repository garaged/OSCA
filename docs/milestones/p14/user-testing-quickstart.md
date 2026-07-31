# P14 Personal-Server Operations Quickstart

## Security validation

Loopback-only operation:

```bash
uv run python -m osca.personal_server security-check --host 127.0.0.1
```

A non-loopback host fails unless both TLS and authentication are declared:

```bash
uv run python -m osca.personal_server security-check --host 0.0.0.0 --tls --auth
```

## Governed command execution

Disabled-by-default check:

```bash
uv run python -m osca.personal_server run-job \
  --job-id workspace-health \
  --evidence-root .osca/p14 \
  -- uv run python -m osca.analyst_workspace --storage-root .osca --snapshot
```

Execute explicitly:

```bash
uv run python -m osca.personal_server run-job \
  --job-id workspace-health \
  --evidence-root .osca/p14 \
  --enable \
  -- uv run python -m osca.analyst_workspace --storage-root .osca --snapshot
```

## File alert

```bash
uv run python -m osca.personal_server alert-file \
  --destination .osca/p14/alerts.jsonl \
  --subject workspace-warning \
  --message "Workspace health requires review." \
  --enable
```

Webhook alerts are supported through the Python API and require HTTPS. Endpoint values are redacted from retained evidence.

## Backup

Create an off-source-tree backup:

```bash
uv run python -m osca.personal_server backup \
  --source-root .osca \
  --destination-root ../osca-off-device-backups \
  --enable
```

The destination must not be the source directory or one of its descendants.

## Restore

Restore into an empty directory:

```bash
uv run python -m osca.personal_server restore \
  --archive ../osca-off-device-backups/osca-backup-YYYYMMDDTHHMMSSZ.tar.gz \
  --destination-root .osca-restored \
  --enable
```

Use `--overwrite` only after reviewing the destination. Restore completion still requires an operator functional check.

## systemd templates

Review and adapt:

- `deploy/systemd/osca-operations.service`
- `deploy/systemd/osca-operations.timer`

The templates assume a dedicated `osca` user, `/opt/osca` installation, `/var/lib/osca` state, and `/var/backups/osca` backup storage. TLS termination, authentication identities, firewall rules, filesystem ownership, and OS patching remain operator-owned.
