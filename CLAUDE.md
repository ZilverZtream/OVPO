# Agentic Coder Guide — OVPO (Read First)

This repository is spec-driven. Your job is to implement OVPO v0.08 exactly, with strict quality and safety rules.

## Canonical Source of Truth

- Spec: `/spec/v0.08/`
- Schemas: `/schemas/v0.08/`
If code disagrees with spec, fix the code.

## Non-Negotiable Build Rules

1) ALWAYS WIRE
- No partial merges.
- Anything you add must be end-to-end:
  - schema (if applicable)
  - API (OpenAPI if relevant)
  - implementation
  - tests
  - docs
  - UI/SDK updates if behavior changes

2) No backwards compatibility (pre-1.0)
- Don’t add compatibility shims, dual behavior flags, or legacy handlers.
- Make the clean change and update tests/docs/spec as needed.

3) No lose code
- Do not replace working logic with placeholders.
- If removing functionality:
  - remove all references
  - update docs/tests/spec
  - ensure a coherent replacement exists or a justified removal

4) Comments policy
- Comments only explain intent of a function/method/class/module.
- Do not write comments containing:
  TODO, FIXME, BUG, HACK, RISK, ISSUE, LATER
- Track work via GitHub issues and PRs.

5) Multi-tenant isolation is sacred
- Never allow tenant_id to be user-supplied in query endpoints.
- Prefer DB-enforced RLS; if not available, enforce tenant filters in all queries.
- Add tests for tenant isolation whenever touching storage/query layers.

6) Safety and secrecy
- Never log secrets or API keys.
- Treat prompts and user identifiers as sensitive; default is hashing, not plaintext.

## What You Should Do Before Coding

- Search the repo for existing patterns and utilities.
- Identify the exact spec section(s) impacted.
- List concrete acceptance criteria as tests.

## How To Implement Changes

- Keep PRs small and reviewable.
- Update:
  - schemas if data contract changes
  - OpenAPI if endpoints change
  - integration tests to cover invariants
- Prefer explicit types, strict validation at boundaries, and structured errors.

## Testing Expectations

At minimum:
- Unit tests for new logic
- Integration tests for:
  - ingestion validation + partial failures
  - idempotency key duplicates return identical responses
  - dedupe prevents double-counting
  - tenant isolation prevents cross-tenant reads

Run:
- `make lint`
- `make test`
- `make up` + smoke test demo pipeline (when available)

## Common Pitfalls To Avoid

- Adding a new field but not updating schemas and validation
- Implementing behavior that violates terminal-state immutability
- Writing offset pagination instead of cursor pagination
- Assuming ordering guarantees from the queue
- Treating dedupe as “nice to have” instead of mandatory

## Definition of Done (per change)

A change is done only when:
- It is fully wired end-to-end
- It has tests proving invariants
- Docs/spec reflect reality
- CI passes
