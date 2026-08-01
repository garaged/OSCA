# U7 - Model-to-Research Validation

- **Status:** Implementation candidate
- **Depends on:** U5-U6 and existing M6-M9 foundations
- **Baseline:** U6 merge `517a39e900c16ad7ae7f7f369a9664f08bb1fbdd`

## Objective

Connect explicitly approved ML experiment evidence to deterministic event-driven research validation and local paper-challenger evidence without creating a live execution path.

## Implemented scope

- Requires a retained U5 experiment and matching U6 diagnostic.
- Requires `eligible_for_f2_validation` diagnostic status.
- Requires an explicit named human promotion decision before validation.
- Initially supports classification experiments only.
- Converts retained test probabilities or predictions into versioned long-only research signals.
- Executes signals after configurable whole-bar latency at the eligible bar open.
- Exits each research period at the same bar close.
- Applies explicit transaction-cost and slippage assumptions on position changes.
- Treats missing or unalignable predictions as cash/skipped evidence rather than synthetic signals.
- Compares model-derived performance against buy-and-hold over the aligned execution window.
- Records prediction, signal, execution, cost, return, drawdown, baseline, and provenance evidence.
- Requires a second named human decision for local paper-challenger designation.
- Exposes JSON execution through `python -m osca.model_validation`.
- Exposes `POST /api/model-validation/run` in the loopback analyst workspace.

## Validation status

- `completed`: the approved experiment completed local research validation.
- `paper_challenger_approved`: a named human separately approved local evidence-only challenger designation.
- Rejected requests fail closed before result creation.

Paper challenger approval does not schedule a model, connect a broker, or authorize any order.

## Explicit assumptions

- Signals use only retained out-of-sample test predictions.
- Signal rule version, threshold, latency, costs, slippage, and missing-prediction policy are retained.
- Buy-and-hold is descriptive baseline evidence, not a recommendation.
- U7 performs local evidence validation only.

## Non-scope

- Regression-to-position translation.
- Live model serving or scheduled inference.
- Automatic model, strategy, or paper-challenger promotion.
- Broker connectivity, order APIs, autonomous execution, or real orders.
- Investment recommendations or authoritative forecasts.

## Acceptance

- Unapproved, noneligible, mismatched, and unsupported experiments fail closed.
- Approved classification evidence produces traceable prediction-to-signal-to-event results.
- Transaction cost, slippage, latency, missing prediction, baseline, and drawdown evidence remain inspectable.
- Paper-challenger designation requires separate named human approval.
- CLI and loopback workspace API return the same immutable result contract.
- Hosted Quality and manual clean-machine review pass before merge.

## Manual review

See [U7 manual acceptance](manual-testing.md).
