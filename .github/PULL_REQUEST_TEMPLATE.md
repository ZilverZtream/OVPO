# OVPO Pull Request

⚠️ **READ BEFORE SUBMITTING**
This repository enforces **strict, automated policy gates**.
If any item below is not satisfied, your PR **will not be merged**.

---

## 1. Purpose of This PR

Describe **exactly** what this change does and **why it exists**.

- What problem does this solve?
- Which part of the OVPO spec or implementation roadmap does it advance?
- Is this foundational, corrective, or additive?

Be precise. This is a technical system, not a blog post.

---

## 2. Scope & Impact

Check all that apply:

- [ ] Spec-only change (documentation / schemas)
- [ ] Backend (Python)
- [ ] Frontend / SDK (JS / TS)
- [ ] CI / tooling
- [ ] Security / policy
- [ ] Other (explain below)

If this PR affects **schemas, ingestion, or storage semantics**, explicitly state so.

---

## 3. Policy Compliance Checklist (MANDATORY)

All items below are **hard requirements**.

### Code Quality
- [ ] No forbidden comment markers present
  *(NO TODO, FIXME, BUG, ISSUE, RISK, HACK, XXX, etc.)*
- [ ] Comments explain **what / why**, not future work
- [ ] No dead code, commented-out blocks, or placeholder logic

### CI Gates
- [ ] `lint` workflow passes
- [ ] `schema-validate` workflow passes
- [ ] `no-forbidden-comment-marker` workflow passes

### Design Discipline
- [ ] No backward compatibility added
- [ ] No unused abstractions
- [ ] No speculative features
- [ ] No partial implementations

If something is not ready, **do not submit it**.

---

## 4. Schema & Spec Changes (if applicable)

If this PR modifies schemas or the spec:

- Schema version affected: `v0.XX`
- Files changed:
  - `schemas/...`
  - `spec/...`

Confirm:
- [ ] JSON schemas validate cleanly
- [ ] `$ref` targets exist and resolve
- [ ] Changes align with the canonical OVPO spec

---

## 5. Testing & Validation

Explain **how this was validated**:

- Unit tests:
  - [ ] Added
  - [ ] Updated
  - [ ] Not applicable (explain why)
- Manual validation steps (if any):
  - Describe briefly

“CI passed” alone is **not** sufficient if logic is non-trivial.

---

## 6. Security & Operational Considerations

Answer explicitly:

- Does this change affect:
  - [ ] Ingestion
  - [ ] Multi-tenancy
  - [ ] Data retention
  - [ ] Audit logs
  - [ ] Access control
- If yes, explain the impact and why it is safe.

---

## 7. Final Acknowledgement

By submitting this PR, you confirm:

- [ ] I have read and followed the OVPO contribution rules
- [ ] This change is intentional, complete, and production-minded
- [ ] I understand that policy violations will block merge without exception

---

**Incomplete PRs will be closed, not fixed.**
**Quality is enforced by design.**
