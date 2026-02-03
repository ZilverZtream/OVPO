# AGENTS.md — OVPO Agent Operating Rules

This file is written for automated coding agents and humans who want strict, repeatable contribution behavior.

## Agent Mission

Implement OVPO v0.08 as specified, preserving strict correctness, safety, and maintainability.

## Repository Map

- Spec: `/spec/v0.08/`
- Schemas: `/schemas/v0.08/`
- Services:
  - Collector: `/server/collector/`
  - Processor: `/server/processor/`
  - Query API: `/server/query-api/`
- UI: `/ui/`
- SDKs: `/sdk/`
- CLI: `/cli/`
- Infra: `/infra/`
- Tests: `/tests/`

## Hard Constraints (Must Follow)

1) Spec-first
- The spec is authoritative.

2) ALWAYS WIRE
- No stubs. No “we’ll hook it later”.
- If you create a new interface, provide the default implementation and tests.

3) No backward compatibility (pre-1.0)
- Do not add compatibility layers. Prefer clean migrations.

4) No lose code
- Do not delete behavior and replace with placeholders.
- If you must remove something, remove it completely and update everything that references it.

5) No forbidden comment keywords
- Do not write comments containing:
  TODO, FIXME, BUG, HACK, RISK, ISSUE, LATER
- Track tasks via issues/PRs.

6) Avoid “wide refactors”
- Prefer incremental changes with a clear diff.
- If refactoring, keep behavior identical and prove with tests.

7) Security invariants
- Tenant isolation cannot be weakened.
- Do not log secrets.
- Validate at boundaries.
- Signed artifact URLs must be short-lived and audited.

## Required Workflow

For any non-trivial change:
1) Identify impacted spec sections and schemas
2) Update schemas/OpenAPI first (if contract changes)
3) Implement with strict validation
4) Add tests proving invariants
5) Update docs to match implementation
6) Run lint/tests locally

## Error Handling Rules

- Prefer explicit error codes matching the spec.
- Partial failure behavior must accept valid items and report invalid items.
- Idempotency-Key duplicates must return identical responses.

## Data Handling Rules

- Prompts: default to SHA-256 hash storage; plaintext only with explicit opt-in.
- IDs: UUID v4 canonical string format in JSON.
- Queue: at-least-once delivery assumed; consumers must be idempotent.

## Definition of Done (Agent Standard)

A task is complete only when:
- End-to-end wiring is present
- Tests cover success + failure modes
- CI would pass
- Docs/spec match reality
