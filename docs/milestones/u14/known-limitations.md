# U14 Known Limitations

## Trust and isolation

- Manifest conformance is not proof that extension code is safe.
- Validation does not import or execute extension code.
- Existing subprocess isolation is not a hostile-code sandbox.
- Only independently reviewed trusted-local extensions are eligible for execution.

## Distribution

- There is no public extension marketplace.
- Remote installation and automatic updates are prohibited.
- Extension signing and public distribution are not introduced by U14.

## Compatibility

- Extension API `1.x` is supported.
- API `0.9` is temporarily deprecated through the `0.1.x` release family.
- Unknown API versions fail closed.
- U14 does not provide automated manifest migration.

## Capabilities

- Supported capabilities are intentionally narrow and local.
- Network access, remote writes, recommendations, live model serving, broker or exchange orders, and real-capital execution remain unavailable.

## Contributor environments

- Supported contributor rehearsals cover macOS Apple Silicon and Linux x86-64.
- Windows, macOS Intel, and Linux ARM are not U14 supported contributor targets.
