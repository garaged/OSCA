# M10 Risk Register

| Risk | Description | Treatment |
|---|---|---|
| M10-R-001 | LLM provider/model substitution could make retained output irreproducible. | Preserve exact provider and model version in request and route evidence. |
| M10-R-002 | LLM tools could bypass deterministic application rules. | Represent tools as bounded typed capabilities and fail closed for prohibited live-order actions. |
| M10-R-003 | Project context could silently mix unrelated histories. | Require explicit selected project and approved references in context policy. |
| M10-R-004 | Sensitive data could be disclosed to an unsuitable provider. | Enforce privacy classification and sensitive-disclosure approval before routing. |
| M10-R-005 | Cost or latency could become uncontrolled. | Require declared budgets and deterministic pre-execution checks. |
| M10-R-006 | Generated output could be treated as factual evidence. | Require evaluation evidence and defer generated-output behavior. |
