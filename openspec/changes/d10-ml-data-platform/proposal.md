# D10 Proposal — ML Data Platform, Feature Catalog, and Experiment UX

## Why

OSCA already has governed dataset revisions and a deterministic local experiment engine, but the desktop cannot construct immutable ML datasets, inspect feature/label definitions, retain bounded runs, or compare results with simple baselines. D10 closes that product gap while keeping model approval in D11.

## Authority

- D10 accepted intent and desktop roadmap
- REQ-0415 through REQ-0421
- ADR-0035 governed ML lifecycle boundary
- ADR-0005 elevated public-contract/persistence gates
- ADR-0009 capability persistence ownership

## What changes

- add a versioned built-in feature and label catalog;
- build experiment definitions from server-resolved governed dataset revisions;
- retain dataset digest, policies, features, label, chronological split, purge/embargo, parameters, resource budget, and lineage;
- add planned/running/completed/review-required/failed/cancelled lifecycle and restart recovery;
- run bounded local baseline, linear, ridge, and logistic experiments;
- expose baseline comparison, partition ranges, findings, and digests in ML Lab;
- allow D6 projects to pin ML experiment identities;
- prove the renderer has no path, network, credential, promotion, recommendation, broker, or real-capital authority.

## Non-goals

Model approval or promotion, model artifact deployment, explainability/drift governance, remote/distributed training, arbitrary feature code, sequence models, recommendations, or any live-order path.
