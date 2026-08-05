# D17 Intent — Windows x86-64 Support

## Outcome
Windows users can install, launch, update, diagnose, and use the supported OSCA desktop workflows with behavior and safety boundaries equivalent to macOS and Linux.

## Scope
Windows sidecar packaging, WebView2 integration, credential storage, notifications, filesystem and Unicode handling, installer, signing, updater, CI, clean-VM acceptance, antivirus false-positive review, and platform documentation.

## Non-goals
Windows ARM, Microsoft Store distribution, or platform-specific feature divergence without an accepted decision.

## Dependencies
D1-D16 desktop surfaces that must be supported before the polished release.

## Risks
Native dependency packaging, installer reputation, updater failure, path and locale bugs, WebView differences, credential-store behavior, and antivirus detection.

## Exit intent
Signed installation and update succeed on clean supported Windows VMs; sidecar and profile recovery are tested; accessibility and core journeys pass; platform-specific limitations are documented; Windows becomes a first-class release target before D19.
