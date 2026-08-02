# U9 Provider Evidence Review

- **Reviewed:** 2026-08-02
- **Scope:** No-cost historical OHLCV acquisition for the U9 implementation candidate
- **Decision:** Admit Kraken public spot OHLC; do not promote a no-cost equity provider yet

## Kraken

Kraken remains approved for public spot OHLC under the bounded P13 personal/internal-use policy.

U9 uses only:

- official `https://api.kraken.com/0/public/OHLC`
- explicit network opt-in
- the approved `spot_ohlc` resource
- bounded timeout, response size, and retry behavior
- retained payload digest, provider attribution, request identity, and policy evidence

External redistribution, recommendations, broker connectivity, and real-capital execution remain disabled.

## Twelve Data Basic

Official material reviewed on 2026-08-02 states:

- Basic is free and provides 8 API credits per minute and 800 requests per day.
- Basic is described as internal non-display usage.
- Individual plans are limited to personal/internal use and do not permit redistribution or commercial display to third parties.
- `/time_series` provides historical OHLCV and costs one API credit per symbol.
- the terms restrict storage beyond plan/documentation permissions and require deletion after subscription termination as applicable.

OSCA's analyst workspace and portable evidence/export behavior can display and retain acquired data. The Basic-plan evidence therefore does not establish that the complete OSCA U9 workflow is permitted. Twelve Data remains `needs_evidence` and is not allowlisted for acquisition.

Authoritative references:

- https://twelvedata.com/pricing
- https://twelvedata.com/terms
- https://support.twelvedata.com/en/articles/5332349-commercial-and-personal-usage
- https://support.twelvedata.com/en/articles/5656039-how-to-get-historical-prices

## Alpha Vantage

Official material confirms a free API key and a standard limit of 25 requests per day, but the reviewed public material does not provide sufficient exact evidence for OSCA's intended retained workspace display, export, backup, and redistribution boundaries. Alpha Vantage remains `needs_evidence`.

Authoritative references:

- https://www.alphavantage.co/support/
- https://www.alphavantage.co/documentation/

## Equity outcome

No no-cost equity provider is promoted in this slice. Equity requests retain a structured `provider_unavailable` decision and direct the operator to the governed CSV import path.

This is an intentional fail-closed outcome, not an implementation omission. A future promotion requires accepted evidence for the exact account plan, dataset, historical depth, adjustment semantics, display rights, retention, export, backup, redistribution, attribution, quota, and termination behavior.
