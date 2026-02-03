# Contributing to OVPO

Thanks for contributing. OVPO is a spec-driven system. The v0.08 specification is the source of truth.

## Ground Rules (Strict)

1) **Spec-first**
   - If code and spec disagree, fix the code.
   - If you believe the spec should change, propose it via an RFC (see GOVERNANCE.md).

2) **No backwards compatibility (pre-1.0)**
   - This project is in development; avoid compatibility layers that add clutter.
   - If you must change behavior, update the spec/docs and migrate the codebase cleanly.

3) **ALWAYS WIRE**
   - No “partial features” merged.
   - Any new endpoint, field, or behavior must be end-to-end wired:
     - schema (if applicable)
     - server implementation
     - tests (unit + integration where relevant)
     - docs (README or docs site)
     - UI/SDK updates if the change affects them

4) **No lose code**
   - Do not delete working behavior and replace it with stubs.
   - If you remove functionality, the PR must:
     - remove all references cleanly
     - update docs/tests/spec accordingly
     - demonstrate the replacement path or rationale

5) **Comments policy**
   - Comments may explain **why** and describe **intent** of a function/class/module.
   - **No** comments containing: “TODO”, “FIXME”, “BUG”, “HACK”, “RISK”, “ISSUE”, “LATER”.
   - Track work via issues, not code comments.

6) **Determinism and safety**
   - Don’t log secrets.
   - Don’t break tenant isolation.
   - Don’t bypass schema validation.

## How to Work

### 1) Pick an issue
- Check existing issues and milestones.
- If proposing a new feature, open an issue with:
  - rationale
  - impact on spec/schemas
  - migration plan (if changing existing behavior)

### 2) Create a branch
- Branch name: `feat/<topic>`, `fix/<topic>`, `docs/<topic>`

### 3) Keep PRs small
- Prefer narrow, reviewable PRs.
- Large refactors need explicit justification and must keep tests green.

## Development Setup (Local)

Minimum expectation is a working local stack via Docker Compose.

- `make up` starts dependencies and services
- `make test` runs tests
- `make lint` runs linters/formatters
- `make seed` sets up a dev tenant + API key (if provided)

If Make targets aren’t available yet, use the repo’s documented equivalent commands.

## Testing Requirements

- Unit tests for new logic
- Integration tests for:
  - ingestion (schema + partial failure)
  - idempotency (same key returns identical response)
  - dedupe (duplicate items do not double-count)
  - tenant isolation (cannot access other tenant data)
- Regression tests for fixed bugs

No PR is considered complete without tests unless it is docs-only.

## Coding Standards

- Follow repo formatters and linters.
- Prefer explicit types and clear error handling.
- Avoid hidden side effects.
- Validate input at boundaries.
- Use structured logging (JSON) with request_id/tenant_id where applicable.

## Commit Messages

Use conventional commits:
- `feat: ...`
- `fix: ...`
- `docs: ...`
- `refactor: ...`
- `test: ...`
- `chore: ...`

## Pull Request Checklist

- [ ] End-to-end wired (schemas/tests/docs/services as needed)
- [ ] Tests added/updated and passing
- [ ] No compatibility scaffolding added
- [ ] No forbidden comment keywords
- [ ] No secrets in logs or configs
- [ ] Tenant isolation preserved
- [ ] Spec and schemas updated if behavior changed
