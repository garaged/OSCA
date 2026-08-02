# U9 Governed No-Cost Historical Data Acquisition

- **Status:** Implementation candidate, first slice
- **Predecessor:** U8 real-world workflow reconciliation
- **Roadmap:** [U9-U14 usable release roadmap](../usable-release-roadmap.md)
- **Provider review:** [U9 provider evidence review](provider-evidence-review.md)

## Intent

Allow a new local OSCA user to acquire sufficient historical equity and cryptocurrency data for the principal research demonstration without a paid account or an external preparation script, while preserving licensing, provenance, canonical identity, quality, revision, and safety controls.

## Governing requirements

- REQ-0021 canonical instrument identity
- REQ-0023 explicit provider mapping
- REQ-0024 ambiguity protection
- REQ-0025 provider capability contract
- REQ-0026 capability routing
- REQ-0027 visible provider transitions
- REQ-0028 licensing enforcement
- REQ-0029 named provider credentials
- REQ-0030 versioned daily bar contract
- REQ-0031 source immutability and retention evidence
- REQ-0032 canonical revisioning
- REQ-0033 typed dataset metadata
- REQ-0034 explicit retrieval requirements
- REQ-0035 structured resolution status
- REQ-0036 idempotent durable retrieval
- REQ-0037 gap detection and targeted repair
- REQ-0038 initial quality rules
- REQ-0041 approved interval set
- REQ-0042 UTC interval windows
- Universal evidence-based milestone exit gate

## First implementation slice

This branch adds the primary `osca historical-data fetch` surface and a versioned historical-acquisition request/evidence contract.

Implemented behavior:

- Kraken public spot OHLC uses the already admitted P13 endpoint and resource policy.
- Network use remains explicit and disabled by default.
- Successful or blocked outcomes retain source attribution, admission state, payload lineage, policy findings, and disabled safety boundaries under `<storage-root>/historical-acquisition/`.
- Equity requests fail closed with `provider_unavailable` and direct the operator to governed CSV import.
- Twelve Data, Alpha Vantage, and other equity providers remain unallowlisted pending exact display, retention, export, backup, redistribution, and termination evidence.

This slice intentionally does not claim complete canonical OHLCV normalization or U8 pipeline handoff. Those remain required before U9 exit.

## Required command surface

```bash
uv run osca historical-data fetch XBTUSD crypto kraken \
  --timeframe 1d \
  --network-access-enabled \
  --storage-root .osca/manual-test
```

Blocked equity evidence can be inspected with:

```bash
uv run osca historical-data fetch AAPL equity twelve_data \
  --timeframe 1d \
  --storage-root .osca/manual-test
```

The existing governed CSV import remains the equity fallback.

## Provider admission gate

A provider path is not implementation-ready until the repository records:

- provider and endpoint identity;
- supported asset classes, venues, symbols, intervals, and history limits;
- authentication and credential requirements;
- free-tier or public-use limits;
- attribution requirements;
- retrieval, retention, transformation, export, backup, and redistribution policy;
- timestamp, adjustment, completion, and quality semantics;
- quota and retry behavior;
- raw-payload retention or explicit non-retention evidence;
- health and capability failure behavior;
- golden fixtures and conformance tests.

Licensing or terms uncertainty blocks admission. Convenience alone is not sufficient.

## Remaining U9 implementation

1. Parse and validate Kraken OHLC response semantics.
2. Normalize admitted responses through the canonical OHLCV import/storage path.
3. Return a dataset revision ID directly from acquisition.
4. Add durable idempotency and concurrent-request sharing.
5. Add quota/rate-limit classification and retry guidance.
6. Add correction/parser revision behavior.
7. Prove CSV fallback equivalence.
8. Prove U8 pipeline compatibility and workspace discovery.
9. Complete the clean-profile manual acceptance exercise.

## Security and safety

- Credentials use named secret references and never enter logs, URLs, manifests, payload exports, or portable configuration.
- Network access is limited to admitted provider endpoints.
- No recommendation, model promotion, broker, exchange-order, autonomous-execution, or real-capital capability is introduced.
- Acquisition output is research data, not investment advice.

## Exit criteria

U9 is complete only when:

- at least one no-cost cryptocurrency acquisition path passes;
- one no-cost equity path passes, or is explicitly blocked with retained terms evidence and the provider-neutral/CSV workflow remains complete;
- primary CLI discovery and documentation match behavior;
- canonical provenance, policy, revision, integrity, and quality evidence is retained;
- failure paths are actionable and non-corrupting;
- U8 accepts the resulting revision;
- automated and manual evidence is retained;
- all hosted quality gates pass.
