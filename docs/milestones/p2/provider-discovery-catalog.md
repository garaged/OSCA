# P2 Provider Discovery Catalog - No-Cost Candidates

- **Status:** In review
- **Milestone:** P2
- **Purpose:** Identify no-cost provider candidates and exclusions before implementation.
- **Review rule:** Discovery notes are not production promotion evidence. Later implementation or promotion work must revalidate exact account-plan, terms, quota, credential, retention, backup, and redistribution evidence under P1 gates.

## Disposition Model

| Disposition | Meaning |
|---|---|
| Preferred candidate | Good fit for future implementation planning, subject to fresh evidence and P1 gates. |
| Conditional candidate | Potentially useful but limited by quota, dataset-specific licensing, scope mismatch, or operational constraints. |
| Research-only | Useful for manual research or experiments, but not acceptable for default automated production use yet. |
| Excluded | Do not implement until a compliant official path is evidenced. |

## Candidate Catalog

| Provider | Cost profile | Account/key | OSCA capability fit | Disposition | Evidence and constraints |
|---|---|---|---|---|---|
| Alpha Vantage | Free tier plus paid plans | API key required | Low-volume stock/ETF/equity time series and indicators | Conditional candidate | Official support docs describe free stock API service for most datasets up to 25 requests/day; real-time and 15-minute delayed US market data are premium-only. Requires exact endpoint and redistribution evidence before implementation. Source: https://www.alphavantage.co/support/ |
| Nasdaq Data Link | Free and premium datasets | Account/key likely required for API use | Dataset-specific equities, macro, alternatives, and tables | Conditional candidate | Official docs state free and premium data are available through Data Link APIs. Dataset-level licenses vary, so OSCA must treat each dataset as separately gated evidence. Source: https://docs.data.nasdaq.com/docs/getting-started |
| FRED | No-cost public economic data API | API key required | Macroeconomic enrichment, rates, economic indicators | Preferred candidate for macro enrichment | Official API terms require a registered API key and make the API available under FRED terms. Not a market OHLCV substitute. Source: https://fred.stlouisfed.org/docs/api/terms_of_use.html |
| SEC EDGAR / data.sec.gov | Public access | No API key for public data APIs, declared user-agent required for automated access | Fundamentals, filings, company facts, disclosure events | Preferred candidate for fundamental/event enrichment | SEC developer docs provide EDGAR submissions and XBRL APIs; fair-access guidance limits automated access to 10 requests/second and asks for declared user-agent headers. Sources: https://www.sec.gov/search-filings/edgar-application-programming-interfaces and https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data |
| Stooq | Public website/downloads appear no-cost | No formal API key observed in discovery | Historical market data research | Research-only | Useful public data source, but official automation terms, API stability, and redistribution permissions are not clear enough for default automated production use. Requires legal/policy evidence before adapter work. Source: https://stooq.com/ |
| Yahoo Finance unofficial endpoints/libraries | Often presented as free by third parties | Unclear or unofficial | Market data | Excluded | OSCA must not depend on unofficial Yahoo Finance scraping or undocumented endpoints unless a compliant official public API/license path is evidenced. Yahoo API terms govern Yahoo APIs generally, but P2 does not identify an official public Yahoo Finance market-data API suitable for OSCA. Source: https://legal.yahoo.com/us/en/yahoo/terms/product-atos/apiforydn/index.html |

## Recommended Implementation Sequence

1. SEC EDGAR fundamentals/events because it is official, public, and strong for non-price enrichment.
2. FRED macro enrichment because it is official, API-oriented, and useful for market context.
3. Alpha Vantage as a low-volume equity fallback only if free-tier limitations are acceptable for the target workflow.
4. Nasdaq Data Link only per named dataset after dataset-specific terms are captured.
5. Stooq only after automation and redistribution policy evidence is resolved.
6. Yahoo Finance remains excluded unless an official compliant path is identified.

## Production Promotion Rule

No provider in this catalog is production-enabled by P2. Promotion remains controlled by P1 evidence gates.
