# Engineering Decision Matrix

Use this as a navigation aid. It does not replace the governing ADR.

| Design question | Default answer | Authority |
|---|---|---|
| Need information without mutation? | Query | ADR-0006 |
| Need another capability to change state? | Command to its public application interface | ADR-0006 |
| Need to communicate a committed fact? | Integration event | ADR-0006, ADR-0007 |
| Is the fact internal to one domain model? | Private domain event | ADR-0006 |
| Is work long-running, retryable, scheduled, or compensating? | Durable workflow | ADR-0006 |
| Need another capability's data? | Public query or governed projection | ADR-0009 |
| Need cross-capability reporting? | Owned projection or composed read model | ADR-0009 |
| Can an event be redelivered? | Yes; make the consumer idempotent | ADR-0007 |
| Need event ordering? | Declare the narrow ordering scope explicitly | ADR-0007 |
| Can code access another module's schema? | No | ADR-0009 |
| Is an extension third-party or independently released? | Isolate according to trust tier | ADR-0008 |
| Can an extension access network, files, secrets, or models implicitly? | No; require explicit grants | ADR-0008 |
| Does a feature need logs added later? | No; telemetry is part of its design | ADR-0010 |
| Is an operational log sufficient for security evidence? | No; use a distinct audit record when required | ADR-0010 |
| Does a public contract change? | Apply contract-family compatibility governance | ADR-0004 |
| Which tests and gates apply? | Classify risk and apply the corresponding evidence profile | ADR-0005 |
| Can a foundational decision be edited after freeze? | Supersede it through a new ADR | Architecture evolution policy |
