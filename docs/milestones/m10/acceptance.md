# M10 Acceptance Criteria

| ID | Requirement | Acceptance criterion |
|---|---|---|
| M10-AC-001 | REQ-0125 | Route decisions retain exact provider/model identity and fail when no provider supports the requested capability and privacy class. |
| M10-AC-002 | REQ-0126 | Tool definitions distinguish read and state-changing tools and reject live-order capabilities. |
| M10-AC-003 | REQ-0127 | Prompt, tool, context, and structured-output contracts carry stable version identities. |
| M10-AC-004 | REQ-0128 | Context policies require explicit selected project identity and approved references. |
| M10-AC-005 | REQ-0129 | Sensitive disclosure and untrusted content handling fail closed when approval is missing. |
| M10-AC-006 | REQ-0130 | Budget evaluation rejects requests whose estimated cost exceeds declared budget. |
| M10-AC-007 | REQ-0131 | LLM evaluation reports retain quality findings and reject passed status with error findings. |
| M10-AC-008 | REQ-0132 | Manual testing and usage includes M10-specific smoke checks. |
| M10-AC-009 | REQ-0133 | LLM lifecycle records round trip through SQLite metadata persistence and can be queried by request identity. |
