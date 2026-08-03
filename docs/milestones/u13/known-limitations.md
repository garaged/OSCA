# U13 Known Limitations

## Provider availability

- No no-cost equity provider currently satisfies the complete licensing, capability, provenance, and reliability admission gate.
- Equity workflows use governed CSV or Parquet import.
- Kraken public spot OHLC remains internal-use evidence with redistribution disabled.

## Research interpretation

- Experiment eligibility is not evidence of predictive quality or investment suitability.
- Human-gated validation is local evidence comparison only.
- Results may materially underperform buy-and-hold.

## Runtime and platform support

- Supported release-candidate platforms are macOS Apple Silicon and Linux x86-64 with Python 3.13.
- Windows, macOS Intel, and Linux ARM are not U13 supported targets.
- The workspace is loopback-only and read-only by default.

## Extensions

- Only built-in, verified, or independently accepted trusted-local extensions may execute.
- Subprocess isolation is not a complete hostile-code sandbox.
- A public untrusted extension marketplace remains unavailable.

## Release operations

- Artifact signing and package-index publication are not performed automatically.
- Release-candidate tag creation requires an explicit action after eligibility.
- Compatibility aliases remain available through U13 and may be deprecated in a later milestone under a documented policy.

## Explicitly unavailable capabilities

Recommendations, automatic model promotion, live model serving, broker or exchange order connectivity, autonomous execution, real-capital orders, remote writes, and public evidence publication remain disabled.
