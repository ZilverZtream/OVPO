# Security Policy — OVPO

OVPO is an observability platform for AI video generation pipelines. Security matters because OVPO may handle tenant identifiers, hashed user identifiers, prompt hashes, audit logs, and signed artifact URLs.

## Supported Versions

OVPO is in active development. Only the latest `main` branch and the most recent tagged pre-release are supported for security fixes.

- `main`: Supported
- Latest tagged release: Supported
- Older tags: Not supported

## Reporting a Vulnerability

Please report security issues privately.

1) **Preferred:** Open a GitHub Security Advisory (Private Vulnerability Reporting) in this repository.
2) **Fallback:** Create a GitHub issue **without sensitive details**, and state you want to disclose privately. A maintainer will respond with a private channel.

When reporting, include:
- A clear description of the vulnerability and impact
- Steps to reproduce (PoC if possible)
- Affected components and versions/commit hash
- Any suggested mitigations or fixes

## What Not to Report Publicly

Do **not** publicly disclose:
- Credential leakage
- Tenant isolation bypass
- Signed URL bypass
- Audit log tampering
- RCE/SSRF/path traversal
- Schema/validation bypass leading to data corruption

## Our Security Commitments

We aim to:
- Acknowledge reports quickly
- Triage and confirm impact
- Provide a fix or mitigation
- Coordinate disclosure timing with the reporter when feasible

## Security Design Notes (High-Level)

- Tenant isolation is mandatory. Production deployments should enable DB-enforced RLS where supported.
- Ingestion must enforce request size limits, schema validation, and rate limiting.
- API keys must be stored hashed; secrets must never be logged.
- Signed artifact URLs must be short-lived and audited.
- Audit log must be append-only (minimum requirement) with optional cryptographic chaining.

## Disclosure Policy

We follow coordinated disclosure. If a vulnerability is confirmed, we will:
- Prepare a fix
- Add regression tests
- Publish release notes describing the issue at a safe level of detail
