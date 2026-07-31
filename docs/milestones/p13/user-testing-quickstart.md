# P13 User Testing Quickstart

## 1. Inspect admission policy without network access

```bash
uv run python -m osca.production_ingestion policy
```

Confirm:

- SEC EDGAR and Kraken are `approved` only for their listed resources.
- Twelve Data, Alpha Vantage, and Nasdaq Data Link are `needs_evidence`.
- FRED is `policy_blocked`.

## 2. Confirm explicit network opt-in

```bash
uv run python -m osca.production_ingestion \
  kraken-ohlc \
  --pair XBTUSD \
  --interval 1440 \
  --storage-root .osca/p13-manual
```

Expected: `policy_blocked` with `network-access-not-enabled`.

## 3. Run approved Kraken public OHLC ingestion

```bash
uv run python -m osca.production_ingestion \
  kraken-ohlc \
  --pair XBTUSD \
  --interval 1440 \
  --storage-root .osca/p13-manual \
  --enable-network
```

Expected: retained JSON payload and `.metadata.json` evidence under `production-ingestion/kraken/spot_ohlc/`.

## 4. Run approved SEC company-facts ingestion

Use a real organization/contact user agent:

```bash
uv run python -m osca.production_ingestion \
  sec-company-facts \
  --cik 320193 \
  --user-agent "Your Organization contact@example.com" \
  --storage-root .osca/p13-manual \
  --enable-network
```

Expected: retained payload and metadata under `production-ingestion/sec_edgar/company_facts/`.

## Evidence checks

Verify metadata records provider/resource identity, endpoint, admission state, network use, attempt count, response size, SHA-256, payload URI, and internal-use/redistribution-disabled findings.

Do not publish or redistribute retained provider payloads. P13 does not enable recommendations, brokers, autonomous execution, or real-capital orders.
