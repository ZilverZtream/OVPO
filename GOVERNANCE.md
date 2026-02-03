# OVPO Governance

OVPO is community-driven with maintainers responsible for quality, security, and spec compliance.

## Roles

### Maintainers
Maintainers:
- Review and merge PRs
- Manage releases
- Enforce security and quality standards
- Own the canonical spec and schemas

### Contributors
Contributors:
- Submit issues and PRs
- Participate in discussions and RFCs
- Help improve docs, tests, integrations

## Decision Making

- **Default:** Lazy consensus
  - If no objections are raised after reasonable review time, a maintainer may merge.
- **If contested:** Maintainer vote
  - Simple majority among active maintainers decides.
- **Tie-break:** Project lead (or designated maintainer) decides.

## RFC Process (Required for Significant Changes)

An RFC is required for:
- Breaking changes to schemas or API behavior
- Changes to retention/deletion semantics
- Tenant isolation/auth model changes
- New core components (plugins, metrics frameworks, etc.)

RFC steps:
1) Create `rfcs/<YYYY-MM-DD>-<title>.md`
2) Include:
   - Summary
   - Motivation
   - Proposed design
   - Alternatives considered
   - Security implications
   - Operational implications
   - Migration plan (if applicable)
3) Open PR and discuss
4) Maintainers approve/merge RFC
5) Implement behind the RFC’s accepted design

## Versioning

- Pre-1.0: breaking changes allowed with minor bumps (0.x → 0.y)
- No backwards compatibility layers. Migrate cleanly.

## Release Process

A release requires:
- CI green
- Spec and schemas consistent
- Migration notes if needed
- Security checklist pass
- Tagged release and changelog entry

## Code of Conduct

All participation is governed by CODE_OF_CONDUCT.md.

## Security

Security disclosure is governed by SECURITY.md.
