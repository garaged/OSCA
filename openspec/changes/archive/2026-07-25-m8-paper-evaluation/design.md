# Design

M8 introduces `osca.paper` as the F3 paper-evaluation package. It consumes M7 promotion-gate evidence from `osca.backtesting.eventing` and defines forward paper state separately from F2 historical simulation.

The boundary is contract-first. Later slices can add persistence, scheduling, recovery, and notification adapters without redefining paper account or run identity.
