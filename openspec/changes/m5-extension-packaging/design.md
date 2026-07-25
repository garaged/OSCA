# Design - M5 Extension Packaging

M5 uses typed Pydantic contracts and application services before persistence or runtime execution. This preserves the package lifecycle semantics while keeping untrusted code inactive.

The design separates:
- package identity and manifest metadata;
- installation records;
- activation decisions;
- impact previews.

Trust tier and activation state are explicit fields. Unknown or untrusted states fail closed.
