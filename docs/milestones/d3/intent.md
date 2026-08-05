# D3 Intent — Data Sources, Credentials, Import, and Acquisition UX

## Outcome
Users can understand available data capabilities, configure credentials safely, import local evidence, run governed acquisition, inspect jobs, and understand why a capability is unavailable.

## Scope
Provider catalog, capability status, OS keychain integration, import wizard, Kraken public historical acquisition, job progress and cancellation, validation, provenance, retry, and provider-promotion evidence display.

## Non-goals
Automatic promotion of providers, embedded credentials, paid-provider dependence, charting workbench, or live exchange trading.

## Dependencies
D2 shell and onboarding; existing provider governance and acquisition services.

## Risks
Licensing ambiguity, secret exposure, quota surprises, symbol/timeframe ambiguity, partial imports, and network failures.

## Exit intent
Offline import and sample paths remain fully usable; credentials never enter ordinary logs or databases; acquisition is capability-gated and auditable; cancellation/retry/recovery are tested; provider warnings cannot silently become production authorization.
