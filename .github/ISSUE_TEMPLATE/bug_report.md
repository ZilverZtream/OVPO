## What

- [ ] Bug fix
- [ ] Feature
- [ ] Refactor
- [ ] Docs
- [ ] CI / tooling

## Why

Describe the user/system impact.

## Spec alignment

- Spec file: `spec/v0.08/OVPO_DEVELOPER_SPEC.md`
- Relevant sections:
  - [ ] 4.x Domain model
  - [ ] 5 Queue semantics
  - [ ] 6 Idempotency & dedup
  - [ ] 7 Retention & deletion
  - [ ] 8 Audit integrity
  - [ ] 9 Security & multi-tenant
  - [ ] 10 APIs
  - [ ] 11 Schemas

## Schema changes (if any)

- [ ] Updated `schemas/v0.08/*`
- [ ] Added/updated schema validation tests
- [ ] Added/updated fixtures
- [ ] Migration notes included (pre-v1.0 allowed, but must be documented)

## Always-wire / No-dead-code checklist

- [ ] Feature is reachable from runtime entrypoint (API route / worker / CLI)
- [ ] Tests execute the new code path
- [ ] No unused modules, unused code paths, or unreachable branches
- [ ] No forbidden comment markers in code (TODO/FIXME/BUG/ISSUE/RISK)

## Security / tenancy

- [ ] Tenant derived from auth context only
- [ ] Queries are tenant-filtered
- [ ] Artifact access uses signed URLs (if relevant)
- [ ] Audit events emitted (if relevant)

## Tests

Paste commands and evidence:
- [ ] Unit tests:
- [ ] Integration tests:
- [ ] Schema validation:

## Notes

Anything reviewers should know.
