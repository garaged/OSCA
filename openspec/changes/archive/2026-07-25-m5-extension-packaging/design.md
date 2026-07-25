# Design - M5 Extension Packaging

M5 uses typed Pydantic contracts, application services, SQLite lifecycle persistence, and metadata-only CLI administration before runtime execution. This preserves the package lifecycle semantics while keeping untrusted code inactive.

The design separates:
- package identity and manifest metadata;
- installation records;
- activation decisions;
- impact previews;
- lifecycle persistence;
- operator administration.

Trust tier and activation state are explicit fields. Unknown or untrusted states fail closed. CLI administration persists metadata and activation decisions only; it does not load or execute third-party extension code.
