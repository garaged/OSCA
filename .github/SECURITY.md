# Security Policy

## Supported versions

OSCA is pre-1.0 research software. Security fixes target the current `main` branch and the latest published release candidate unless a release note states otherwise.

## Reporting a vulnerability

Do not report suspected vulnerabilities, exposed credentials, or sensitive operational details in a public issue, discussion, or pull request.

Use GitHub private vulnerability reporting for this repository. Include:

- affected version or commit;
- affected component and platform;
- reproduction steps or a minimal proof of concept;
- expected and observed behavior;
- potential confidentiality, integrity, availability, financial-safety, or supply-chain impact;
- any known mitigations.

If private vulnerability reporting is unavailable, contact the repository owner privately through their GitHub profile and ask for a secure reporting channel without including exploit details in the initial message.

## Scope

Security reports may include, among other issues:

- credential or secret exposure;
- unsafe archive, path, or file handling;
- extension trust or execution boundary bypass;
- provider-policy or network opt-in bypass;
- evidence tampering or provenance loss;
- sidecar, IPC, desktop-host, or local-server vulnerabilities;
- dependency or build-pipeline compromise;
- activation of prohibited broker, autonomous, or real-capital behavior.

OSCA does not currently authorize live-order execution, autonomous trading, or real-capital operations. A report showing such a path is security-critical.

## Disclosure

Please allow time for validation and remediation before public disclosure. The project will retain security-relevant fixes and release notes without publishing secrets or unnecessary exploit detail.
