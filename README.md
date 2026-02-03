# OVPO — Open Video Pipeline Observatory

OVPO is an open-source observability and debugging platform designed specifically for AI-driven video generation pipelines.

It makes video generation systems:
- Observable (traceable end-to-end)
- Debuggable (explainable failure + quality regressions)
- Measurable (latency, GPU cost, quality signals)
- Comparable (models, samplers, schedulers, hyperparameters)
- Auditable (multi-tenant governance + compliance)
- Resilient (HA + DR patterns)

OVPO is not a video generator.
OVPO is the infrastructure that explains video generation.

## Specification

The canonical spec is:
- `spec/v0.08/OVPO_DEVELOPER_SPEC.md`

Schemas:
- `schemas/v0.08/*`

## Project Components (target)

- Collector (ingestion API, auth, validation, rate limiting)
- Queue (Kafka / NATS JetStream / RabbitMQ)
- Processor (dedup, persistence, enrichment, retention jobs)
- Query API (cursor pagination, RBAC, tenant isolation)
- UI (trace explorer + debug tooling) [optional but expected]
- SDKs:
  - Python SDK (pipeline instrumentation)
  - TypeScript/JavaScript SDK (web + node + tool integrations)

## Core Requirements

- UUID v4 canonical IDs for trace/span/event/batch
- At-least-once ingestion semantics + idempotency (>= 24h)
- Fail-open instrumentation (pipelines continue if OVPO is down)
- Prompt hashed by default; plaintext requires explicit opt-in
- Multi-tenant isolation (RLS recommended)
- Immutable audit trail (append-only or hash chain)
- Retention tiering + GDPR deletion semantics + legal hold

## Development Rules (hard)

- No backward compatibility until v1.0
- No dead code: every merged line must be reachable by a tested code path
- No “TODO/FIXME/BUG/ISSUE/RISK” comments in code
  - Comments are allowed only to explain purpose of a public function/method/class
- Always wire: endpoints, flags, configs, and modules must be connected to runtime
- Fail-open where required by spec; never silently drop data
- All data constraints must be enforced at boundaries (schema + runtime checks)

## Quick Start (placeholder)

This repository is being bootstrapped. See:
- `TODO.md` for the implementation plan
- `.github/PULL_REQUEST_TEMPLATE.md` for change requirements
- `CONTRIBUTING.md` for process and coding rules

## License

Apache 2.0