# OVPO - TODO
Status: Master work breakdown for implementing OVPO v0.08 end-to-end.
Conventions:
  - [ ] = not started
  - [~] = in progress
  - [x] = done
  - (P0/P1/P2) = priority
  - Owner tags are optional: [BE], [FE], [SDK], [SRE], [SEC], [DOC]

---

## 0) Program Setup & Repo Foundation

### 0.1 Repositories, structure, licensing
  - [ ] (P0) Create GitHub org + primary repo `ovpo`
  - [x] (P0) Add Apache 2.0 LICENSE file
  - [x] (P0) Add NOTICE file (if needed)
  - [x] (P0) Add CODEOWNERS
  - [x] (P0) Add SECURITY.md (vuln reporting, supported versions)
  - [x] (P0) Add CODE_OF_CONDUCT.md (Contributor Covenant)
  - [x] (P0) Add CONTRIBUTING.md (dev workflow, PR rules, style)
  - [x] (P0) Add GOVERNANCE.md (maintainers, RFC process)
  - [x] (P0) Add README.md (1-page value prop + quickstart)
  - [ ] (P0) Add docs site scaffolding (MkDocs/Docusaurus)
  - [x] (P0) Define monorepo layout:
        - /spec
        - /schemas
        - /server/collector
        - /server/processor
        - /server/query-api
        - /ui
        - /sdk/python
        - /sdk/js
        - /sdk/rust
        - /cli
        - /infra
        - /examples
        - /tests
        - /tools
  - [ ] (P0) Add editor configs: .editorconfig, .gitattributes
  - [ ] (P0) Add formatting rules:
        - Python: ruff + black
        - Go/Rust: standard fmt
        - TS: eslint + prettier
  - [ ] (P0) Add conventional commits config + changelog policy
  - [ ] (P1) Add PR templates (bug/feature/rfc)
  - [ ] (P1) Add issue templates (bug/feature/security/question)
  - [ ] (P1) Add labels taxonomy (area/*, prio/*, type/*)

### 0.2 CI/CD baseline
  - [ ] (P0) GitHub Actions: lint + test for each component
  - [ ] (P0) GitHub Actions: build docker images on main
  - [ ] (P0) GitHub Actions: schema validation check
  - [ ] (P0) GitHub Actions: license header / SPDX checks
  - [ ] (P0) GitHub Actions: dependency vulnerability scan
  - [ ] (P0) GitHub Actions: secret scanning
  - [ ] (P1) GitHub Actions: publish artifacts (PyPI/npm/crates) (later)
  - [ ] (P1) GitHub Actions: SBOM generation
  - [ ] (P1) GitHub Actions: container signing (cosign)

### 0.3 Local dev bootstrap
  - [ ] (P0) Devcontainer setup (optional)
  - [ ] (P0) Makefile with common targets:
        - make lint
        - make test
        - make build
        - make up (docker compose)
        - make down
        - make seed
  - [ ] (P0) Docker compose for local stack:
        - Postgres
        - Redis
        - ClickHouse
        - MinIO
        - Queue (Kafka OR NATS)
        - Collector
        - Processor
        - Query API
        - UI
  - [ ] (P0) `.env.example` with all variables
  - [ ] (P0) Local TLS (mkcert) optional path
  - [ ] (P1) One-command setup script (Linux/Windows friendly)
  - [ ] (P1) Seed script to create first tenant + API key

---

## 1) Canonical Spec Packaging (v0.08 as source of truth)

### 1.1 Spec repo hygiene
  - [x] (P0) Freeze v0.08 spec as canonical markdown under `/spec/v0.08/`
  - [ ] (P0) Provide “diff note” file only when v0.09 exists (avoid fake changelogs)
  - [ ] (P0) Add spec build/preview instructions
  - [ ] (P1) Add diagrams as ASCII + optional SVG exports
  - [ ] (P1) Add glossary + reserved namespace appendix in `/spec/common/`

### 1.2 Normative vs informative marking
  - [ ] (P0) Mark schema files as normative
  - [ ] (P0) Mark examples as informative
  - [ ] (P0) Ensure RFC2119 language consistent across all MUST/SHOULD statements
  - [ ] (P0) Ensure size limits and windows consistent:
        - batch max 5MB (API)
        - queue max 10MB (internal)
        - idempotency ≥24h
        - dedupe ≥24h
        - clock skew ±5s

---

## 2) JSON Schemas (v0.08) + Validation Tooling

### 2.1 Schema correctness
  - [x] (P0) Place schemas exactly as referenced:
        - schemas/v0.08/ingest_batch.json
        - schemas/v0.08/trace.json
        - schemas/v0.08/span.json
        - schemas/v0.08/frame_event.json
        - schemas/v0.08/artifact_manifest.json
  - [ ] (P0) Ensure `$ref` paths resolve correctly (relative ref integrity)
  - [x] (P0) Add top-level `schemas/v0.08/index.json` referencing all
  - [x] (P0) Add schema examples folder with valid JSON payloads
  - [x] (P0) Add invalid fixture payloads for negative tests
  - [ ] (P0) Ensure UUID format constraints align with server validators
  - [ ] (P0) Ensure tenant_id regex aligned across schema + server
  - [ ] (P0) Ensure prompt_hash and user_id_hash patterns consistent
  - [ ] (P0) Ensure `pipeline_config_ref` mutual exclusion enforced
  - [ ] (P0) Ensure status=FAILED implies failure object enforced

### 2.2 Schema validation CLI tooling
  - [x] (P0) Add a small `ovpo-schema` validator tool:
        - validate batch file
        - validate single item
        - validate folder recursively
  - [ ] (P0) CI job: run schema validation on all examples
  - [ ] (P0) CI job: run negative fixtures must fail
  - [ ] (P1) Add schema packaging for:
        - npm package @ovpo/schemas
        - python package ovpo-schemas
  - [ ] (P1) Add schema registry endpoint (optional, later)

---

## 3) Data Model & Storage Layer

### 3.1 Postgres schema (metadata)
  - [ ] (P0) Define DB migration framework (Flyway/Alembic/sqlx)
  - [ ] (P0) Create migrations:
        - [ ] traces table (UUID PK, tenant_id, status, timestamps, JSONB fields)
        - [ ] spans table (UUID PK, trace_id FK, tenant_id, span_kind, start/end, attributes)
        - [ ] audit_log table (append-only)
        - [ ] tombstones table
        - [ ] api_keys table (hashed)
        - [ ] tenants table
        - [ ] users table (optional; depends on auth)
        - [ ] rbac roles/permissions tables (or static config)
        - [ ] idempotency_keys table
        - [ ] dedupe_items table (optional)
        - [ ] retention_jobs tracking table
  - [ ] (P0) Add essential indexes:
        - traces(tenant_id, created_at desc, trace_id desc)
        - traces(status)
        - spans(trace_id)
        - spans(tenant_id, start_time)
        - audit_log(tenant_id, timestamp)
  - [ ] (P0) Add JSONB GIN indexes for tags (carefully)
  - [ ] (P0) Add constraints:
        - terminal state immutability enforcement (application + optional DB)
        - `tenant_id` not null
  - [ ] (P0) Add RLS policies (recommended mode):
        - [ ] Enable RLS on traces/spans
        - [ ] Create `current_setting('app.current_tenant_id')` policy
        - [ ] Ensure app sets tenant context per session/transaction
  - [ ] (P0) Add tests for tenant isolation:
        - [ ] positive access in same tenant
        - [ ] forbidden/empty in different tenant

### 3.2 ClickHouse schema (frame events + metrics)
  - [ ] (P0) Decide strategy:
        - (A) Store raw frame events table + derived metrics columns
        - (B) Flatten only known metrics columns + JSON blob for extras
  - [ ] (P0) Create ClickHouse tables:
        - [ ] frame_events (trace_id, tenant_id, span_id, frame_index, media_time_ms, observed_at, type, JSON for extras)
        - [ ] frame_metrics_flat (optional) (typed columns for common metrics)
  - [ ] (P0) Partition strategy:
        - partition by month (observed_at)
        - order by (tenant_id, trace_id, frame_index)
  - [ ] (P0) TTL rules for frame data:
        - hot/warm/cold/purge semantics via TTL moves/Deletes
  - [ ] (P0) Write ingestion writer for ClickHouse (batch insert)
  - [ ] (P0) Dedupe approach:
        - [ ] ReplacingMergeTree with version?
        - [ ] Or insert-only + dedupe in queries?
        - [ ] Document tradeoffs
  - [ ] (P0) Create query helpers for:
        - trace timeline retrieval (range by trace_id)
        - time-series aggregations by hour/day
        - p95/p99 metrics over ranges
  - [ ] (P1) Add materialized views for common dashboards:
        - avg clip similarity per hour per model
        - failure rates per hour
        - compute units per day

### 3.3 Redis (hot cache + rate limit + idempotency)
  - [ ] (P0) Define Redis key schema:
        - rate_limit:{tenant}:{minute_bucket}
        - idem:{key} -> response blob
        - live_trace:{tenant}:{trace_id} -> compact state
        - queue_depth gauges (optional)
  - [ ] (P0) Implement rate limiter using Redis (token bucket/leaky bucket)
  - [ ] (P0) Implement idempotency storage in Redis (fast path) + Postgres (durable)
  - [ ] (P0) Implement cache invalidation strategy
  - [ ] (P1) Implement Redis HA options (sentinel/cluster) guidelines

### 3.4 Object storage (MinIO/S3)
  - [ ] (P0) Define bucket structure:
        - /ephemeral/traces/{trace_id}/...
        - /archive/...
  - [ ] (P0) Implement signed URL generation (download)
  - [ ] (P0) Implement upload path for SDK helpers (optional)
  - [ ] (P0) Enforce encryption at rest:
        - SSE-S3 (MinIO equivalent)
        - SSE-KMS optional
  - [ ] (P0) Implement TTL deletion worker:
        - [ ] scan artifact refs with ttl_hours
        - [ ] asynchronous delete
        - [ ] +24h grace
        - [ ] log failures
  - [ ] (P0) Implement lifecycle rules for MinIO dev + document S3 prod
  - [ ] (P1) Cross-region replication guidance (docs)

---

## 4) Message Queue Layer (Collector → Processor)

### 4.1 Select queue baseline
  - [ ] (P0) Choose default queue for OSS distribution:
        - Kafka/Redpanda OR NATS JetStream
  - [ ] (P0) Provide alternate adapters (interface-based)
  - [ ] (P0) Define message envelope for internal queue:
        - tenant_id
        - received_at
        - message_type (trace/span/event)
        - payload (json bytes)
        - content_hash
        - attempt
  - [ ] (P0) Enforce max message size 10MB
  - [ ] (P0) Partitioning rules:
        - by tenant_id
        - optionally within tenant by trace_id

### 4.2 Delivery & dedupe invariants
  - [ ] (P0) Implement at-least-once semantics:
        - producer acks=all / durable publish
        - consumer manual commit/ack
  - [ ] (P0) Implement consumer idempotency:
        - dedupe by (tenant_id, item_id) for ≥24h
        - ignore duplicates without side effects
  - [ ] (P0) Implement out-of-order tolerance:
        - store spans/events even if trace metadata not yet persisted
        - backfill linking later (reconciliation step)
  - [ ] (P0) Implement dead-letter queue (DLQ):
        - poison messages
        - schema validation failure
        - storage write failure beyond retries
  - [ ] (P1) Metrics and monitoring for queue:
        - lag seconds
        - depth
        - DLQ rate

---

## 5) Collector Service (Ingestion Gateway)

### 5.1 Service skeleton
  - [ ] (P0) Choose implementation language (Go or Rust)
  - [ ] (P0) Create HTTP server with:
        - /health
        - /ready
        - /metrics
        - /v1/ingest/batch
  - [ ] (P0) Request parsing and size enforcement (5MB)
  - [ ] (P0) JSON schema validation (draft 2020-12)
  - [ ] (P0) Strict header handling:
        - Authorization
        - Idempotency-Key
        - X-OVPO-Schema-Version
  - [ ] (P0) Return error codes per spec

### 5.2 Auth & tenant extraction
  - [ ] (P0) API key format specification:
        - public prefix + secret portion
        - storage hashed SHA-256
  - [ ] (P0) API key verification middleware
  - [ ] (P0) Extract tenant_id from key mapping
  - [ ] (P0) Ensure tenant_id cannot be supplied by user in query endpoints
  - [ ] (P0) RBAC check for ingestion permission
  - [ ] (P1) JWT/OAuth login support for UI (later)

### 5.3 Rate limiting
  - [ ] (P0) Implement per-tenant rate limiting
  - [ ] (P0) Implement burst logic (200 in 10s)
  - [ ] (P0) Return headers:
        - X-RateLimit-Limit
        - X-RateLimit-Remaining
        - X-RateLimit-Reset
  - [ ] (P0) Return 429 with retry_after
  - [ ] (P1) Tier config (free/pro/enterprise) via config file

### 5.4 Idempotency (batch-level)
  - [ ] (P0) Store idempotency key result for ≥24h
  - [ ] (P0) On duplicate idempotency key:
        - return identical response
        - set duplicate=true
  - [ ] (P0) Handle concurrent duplicate requests safely (locking)
  - [ ] (P0) Expire idempotency keys after window
  - [ ] (P1) Persist idempotency responses to Postgres for durability

### 5.5 Partial failures
  - [ ] (P0) Validate each item independently
  - [ ] (P0) Accept valid items even if some invalid
  - [ ] (P0) Create structured errors list:
        - item_index
        - item_type
        - code
        - field
        - message
  - [ ] (P0) Ensure processed_items counts match reality
  - [ ] (P0) Ensure invalid items not published to queue

### 5.6 Queue publishing
  - [ ] (P0) Publish accepted items to queue
  - [ ] (P0) Ensure stable IDs used as item keys
  - [ ] (P0) Batch splitting if internal queue message size would exceed 10MB
  - [ ] (P0) Retry publishing with backoff (bounded)
  - [ ] (P0) Fail-open rule applies to SDK, NOT collector; collector must reject if cannot queue
  - [ ] (P1) Optional: synchronous fast-path write for tiny deployments (no queue mode)

### 5.7 Observability for collector itself
  - [ ] (P0) Prometheus metrics:
        - requests_total{code}
        - validation_failures_total
        - auth_failures_total
        - rate_limited_total
        - publish_failures_total
        - request_latency_seconds histogram
  - [ ] (P0) Structured logs (JSON) with request_id
  - [ ] (P0) Trace IDs in logs when present
  - [ ] (P1) OpenTelemetry exporter (optional)

---

## 6) Processor Service (Correlation, aggregation, storage, alert evaluation)

### 6.1 Processor skeleton
  - [ ] (P0) Choose implementation language (Rust for perf OR Python for speed + critical parts native)
  - [ ] (P0) Implement queue consumer group
  - [ ] (P0) Implement worker concurrency model
  - [ ] (P0) Implement retry policy:
        - transient storage failures retry
        - poison message to DLQ
  - [ ] (P0) Commit/ack only after successful writes

### 6.2 Item-level dedupe (≥24h)
  - [ ] (P0) Deduplicate traces by trace_id per tenant
  - [ ] (P0) Deduplicate spans by span_id per tenant
  - [ ] (P0) Deduplicate events by event_id per tenant
  - [ ] (P0) Store dedupe keys in:
        - Redis fast set with TTL
        - Optional Postgres durable table
  - [ ] (P0) Guarantee duplicates do not double-count metrics or compute units
  - [ ] (P0) Emit metric: duplicates_detected_total

### 6.3 Trace lifecycle enforcement
  - [ ] (P0) Enforce terminal immutability:
        - reject transition from terminal -> non-terminal
        - allow idempotent re-ingestion of same terminal state
  - [ ] (P0) Implement valid transitions table
  - [ ] (P0) Implement PARTIAL semantics:
        - conditions that cause PARTIAL set
        - missing frame detection marker
  - [ ] (P0) Persist failure object for FAILED traces

### 6.4 Correlation engine
  - [ ] (P0) Handle out-of-order arrival:
        - span arrives before trace
        - event arrives before span
  - [ ] (P0) Strategy:
        - temporarily store orphan spans/events in Redis (short TTL)
        - reconciliation worker to attach later
  - [ ] (P0) Ensure eventual consistency target (<5s p95) for normal load
  - [ ] (P0) Implement “trace assembly” routine for query API:
        - fetch trace metadata (PG)
        - fetch spans (PG)
        - fetch events (CH)
        - join and sort
  - [ ] (P1) Implement timeline reconstruction verification:
        - missing span end_time
        - negative durations
        - invalid nesting

### 6.5 Validation beyond schema
  - [ ] (P0) Enforce monotonic rules:
        - frame_index monotonic (within trace)
        - media_time_ms monotonic
        - observed_at skew tolerance ±5s
  - [ ] (P0) When violated:
        - mark trace PARTIAL
        - log validation error
        - optionally emit frame_error event
  - [ ] (P0) Enforce size constraints for attributes
  - [ ] (P0) Enforce tag key/value rules

### 6.6 Aggregations & derived metrics
  - [ ] (P0) Compute trace-level:
        - total_duration_ms
        - span breakdown %
        - peak vram (from events)
        - avg utilization (from events)
        - frame_count (observed)
        - sampling_rate observed
  - [ ] (P0) Compute compute units:
        - sum(duration_sec * hardware_factor) by span kind
  - [ ] (P0) Record compute unit breakdown per trace
  - [ ] (P0) Ensure hardware factor loaded from config and versioned
  - [ ] (P1) Create rollups:
        - hourly throughput
        - failure rate
        - cost units by project/center/campaign

### 6.7 Alert evaluation (v0.08 minimal)
  - [ ] (P0) Decide baseline alert strategy:
        - (A) native rule engine
        - (B) export metrics to Prometheus/Grafana and let Alertmanager handle
  - [ ] (P0) If native:
        - implement rule schema
        - rule evaluation windows
        - threshold comparisons
        - actions: webhook/email placeholder
  - [ ] (P0) Emit alerts to audit log
  - [ ] (P1) Integrations:
        - Slack
        - PagerDuty
        - OpsGenie

### 6.8 Processor observability
  - [ ] (P0) Prometheus metrics:
        - events_processed_total{type}
        - processing_lag_seconds
        - queue_depth (if available)
        - storage_write_errors_total{backend}
        - dedupe_hits_total
        - dlq_published_total
  - [ ] (P0) Structured logs with message_id + tenant_id + item_id
  - [ ] (P1) Tracing across collector→processor (OTel optional)

---

## 7) Query API Service (REST + optional GraphQL)

### 7.1 Service skeleton
  - [ ] (P0) Choose implementation language (Go/TS/Python)
  - [ ] (P0) Implement endpoints:
        - GET /v1/traces (cursor pagination)
        - GET /v1/traces/{trace_id}
        - GET /v1/analytics/bottlenecks
        - GET /v1/analytics/costs/calculate
        - GET /metrics
        - /health, /ready
  - [ ] (P0) Implement auth middleware shared with collector
  - [ ] (P0) Enforce tenant_id derived from auth only
  - [ ] (P0) Enforce RBAC permissions:
        - trace:read
        - metric:read
        - alert:read (later)
        - admin operations (later)

### 7.2 Cursor pagination (REQUIRED)
  - [ ] (P0) Implement stable ordering:
        - ORDER BY created_at DESC, trace_id DESC
  - [ ] (P0) Implement cursor format:
        - base64(json({"last_timestamp": "...", "last_id": "..."}))
  - [ ] (P0) Implement cursor validation + expiry protection
  - [ ] (P0) Implement has_more, next_cursor
  - [ ] (P0) Prohibit offset pagination

### 7.3 Trace detail endpoint
  - [ ] (P0) Fetch trace metadata from Postgres
  - [ ] (P0) Fetch spans from Postgres
  - [ ] (P0) Fetch events from ClickHouse
  - [ ] (P0) Apply final sorting:
        - spans by start_time
        - events by frame_index then observed_at
  - [ ] (P0) Provide computed summary metrics in response
  - [ ] (P0) Optional: include “data completeness” flags (missing ranges)

### 7.4 Analytics endpoints
  - [ ] (P0) Bottlenecks:
        - group spans by kind
        - compute avg + p95 + p99 durations
        - filter by date range + tags
  - [ ] (P0) Costs calculate:
        - accept trace_ids
        - compute units and span breakdown
        - return pricing_profile name (no currency)
  - [ ] (P1) Cost reporting aggregate endpoint (group_by)
  - [ ] (P1) Quality trend endpoint (avg clip similarity over time)

### 7.5 Conditional headers / caching
  - [ ] (P1) Implement If-Modified-Since / ETag where beneficial
  - [ ] (P1) Cache hot queries in Redis:
        - trace list pages
        - trace detail (short TTL)

### 7.6 Audit logging
  - [ ] (P0) Log TRACE_ACCESS for /traces/{id}
  - [ ] (P0) Log TRACE_QUERY for /traces list + analytics
  - [ ] (P0) Log ARTIFACT_DOWNLOAD when generating signed URL
  - [ ] (P0) Ensure audit events are append-only and include tenant_id
  - [ ] (P0) Add cryptographic chain option (enterprise)

### 7.7 Query API observability
  - [ ] (P0) Metrics:
        - query_latency_seconds
        - db_latency_seconds{pg|ch|redis}
        - request_count{code}
  - [ ] (P0) Structured logs include request_id and tenant_id
  - [ ] (P1) Rate limiting on queries:
        - 100/min default
        - burst rule

---

## 8) Auth, RBAC, Tenants, API Keys

### 8.1 Tenant management
  - [ ] (P0) Tenants table + CRUD (admin-only)
  - [ ] (P0) Tenant config fields:
        - retention policy overrides
        - rate limit tier
        - hardware factor profile
        - legal_hold default
  - [ ] (P0) Seed one tenant in dev environment
  - [ ] (P1) Tenant onboarding checklist automation (CLI)

### 8.2 API keys
  - [ ] (P0) API key creation tool (admin)
  - [ ] (P0) Store only hash of API key (SHA-256)
  - [ ] (P0) Key metadata:
        - tenant_id
        - role
        - created_at
        - expires_at
        - last_used_at
        - revoked_at
  - [ ] (P0) API_KEY_CREATED and API_KEY_REVOKED audit events
  - [ ] (P1) Key rotation reminders (docs + optional feature)

### 8.3 RBAC
  - [ ] (P0) Define permissions map:
        - trace:read
        - trace:write (ingest)
        - metric:read
        - admin:delete
        - admin:tenants
        - admin:keys
  - [ ] (P0) Implement roles:
        - viewer
        - developer
        - admin
        - super_admin
  - [ ] (P0) Enforce RBAC in collector + query API
  - [ ] (P0) Unit tests for permission boundaries
  - [ ] (P1) Optional: fine-grained policies (ABAC conditions)

### 8.4 Optional UI auth (later)
  - [ ] (P1) OAuth/OIDC login for UI
  - [ ] (P1) Session management
  - [ ] (P1) Map identity to tenant membership

---

## 9) Audit Trail & Integrity

### 9.1 Append-only audit log (minimum required)
  - [ ] (P0) Create audit_log table with insert-only permissions
  - [ ] (P0) Revoke UPDATE and DELETE at DB level
  - [ ] (P0) Ensure app DB user lacks update/delete grants
  - [ ] (P0) Add monthly partitioning
  - [ ] (P0) Add index on (tenant_id, timestamp desc)

### 9.2 Cryptographic chain (enterprise option)
  - [ ] (P1) Define canonical JSON hashing rules
  - [ ] (P1) Store previous_hash + record_hash columns
  - [ ] (P1) Implement signature support (optional)
  - [ ] (P1) Add chain verification tool
  - [ ] (P1) Add tamper detection alert

### 9.3 Audit event completeness
  - [ ] (P0) Ensure mandatory event types are generated:
        - TRACE_ACCESS
        - TRACE_QUERY
        - ARTIFACT_DOWNLOAD
        - TRACE_DELETE
        - CONFIG_CHANGE
        - USER_LOGIN (if UI auth exists)
        - API_KEY_CREATED
        - API_KEY_REVOKED
  - [ ] (P0) Ensure audit records include:
        - actor_id
        - actor_ip
        - tenant_id
        - timestamp
        - metadata.user_agent (where relevant)

---

## 10) Retention, Deletion, GDPR, Tombstones, Legal Hold

### 10.1 Retention engine
  - [ ] (P0) Implement retention job scheduler (cron in k8s / internal)
  - [ ] (P0) Apply retention tiers for:
        - traces/spans
        - frame metrics
        - audit logs
        - ephemeral artifacts
  - [ ] (P0) Ensure legal_hold overrides deletion
  - [ ] (P0) Implement purge for frame metrics at 180 days (default)
  - [ ] (P0) Implement traces/spans purge at 2 years (default)
  - [ ] (P0) Implement ephemeral artifact purge at 30 days (default)
  - [ ] (P0) Log deletions to audit log + tombstone where required
  - [ ] (P1) Tenant-specific retention overrides

### 10.2 GDPR delete (Right to be forgotten)
  - [ ] (P0) Define admin endpoint:
        - DELETE /v1/admin/tenants/{tenant_id}/users/{user_hash}
  - [ ] (P0) Hard delete:
        - Postgres trace metadata for that user
        - ClickHouse events/metrics for that user/trace set
        - Redis caches
        - S3 ephemeral artifacts
  - [ ] (P0) Create tombstone record:
        - deletion_id
        - deleted_at
        - deleted_by
        - reason
        - trace_count
  - [ ] (P0) Ensure tombstones retained 7 years
  - [ ] (P0) Ensure deletion completes within 30 days (SLA)
  - [ ] (P1) Async worker for large deletions with progress tracking

### 10.3 Legal hold
  - [ ] (P0) Add legal_hold boolean to traces
  - [ ] (P0) Ensure retention job skips legal_hold=true
  - [ ] (P0) Admin API to set/unset legal hold (with audit)
  - [ ] (P1) Per-tenant default legal hold policy (optional)

---

## 11) SDK — Python (v0.08)

### 11.1 SDK skeleton & packaging
  - [ ] (P0) Create package `ovpo-sdk` under /sdk/python
  - [ ] (P0) Define public API:
        - OvpoClient
        - TraceContext
        - SpanContext
        - SpanKind enums
  - [ ] (P0) Provide typing (py.typed)
  - [ ] (P0) Add build + publish workflow (later)
  - [ ] (P0) Add unit tests with pytest
  - [ ] (P0) Add docs + examples

### 11.2 Core behaviors (must match spec)
  - [ ] (P0) Client-side UUID v4 generation (crypto random)
  - [ ] (P0) Stable IDs across retries:
        - store generated IDs for span/event objects
        - never regenerate on resend
  - [ ] (P0) Asynchronous dispatch:
        - background worker thread OR asyncio task
        - non-blocking emit_frame
  - [ ] (P0) Ring buffer memory cap (50MB default):
        - overwrite oldest when full
        - expose counters: dropped_events_total (if overwrite policy)
  - [ ] (P0) Flush policy:
        - flush_interval_sec default 5
        - flush on trace close
        - flush on process exit best-effort
  - [ ] (P0) Batch splitting to keep request <= 5MB
  - [ ] (P0) Support Idempotency-Key header:
        - stable per batch send attempt
  - [ ] (P0) Fail-open:
        - if collector unreachable, continue pipeline
        - track failures locally, do not raise by default
        - allow strict mode to raise for tests
  - [ ] (P0) Clock skew tolerance doesn’t belong in SDK validation (server does), but SDK should:
        - record observed_at from system clock
        - avoid reordering user events

### 11.3 Data shaping utilities
  - [ ] (P0) Prompt hashing helper (SHA-256)
  - [ ] (P0) user_id hashing helper (SHA-256)
  - [ ] (P0) Attribute namespace validation:
        - ovpo.* or custom.*
        - reject non-namespaced keys
  - [ ] (P0) Tag validation helper (regex + value size)
  - [ ] (P0) Provide artifact ref helper object builder
  - [ ] (P0) Provide output_manifest builder

### 11.4 GPU metrics (optional but important)
  - [ ] (P1) NVML integration for:
        - vram_used_mb
        - gpu_utilization_pct
        - temperature_c
  - [ ] (P1) Sampling frequency config for GPU metrics
  - [ ] (P1) Ensure zero VRAM impact (CPU-only polling)

### 11.5 “Last gasp” reliability
  - [ ] (P1) atexit handler flush best-effort
  - [ ] (P1) signal handlers where safe (SIGTERM)
  - [ ] (P1) local spool-to-disk option (enterprise / advanced)
        - bounded disk usage
        - resend on next start

### 11.6 Integrations
  - [ ] (P1) Diffusers callback integration
  - [ ] (P1) ComfyUI node integration (separate repo or folder)
  - [ ] (P2) A1111 extension integration

---

## 12) SDK — JavaScript/TypeScript (v0.08)

### 12.1 Package setup
  - [ ] (P0) Create `@ovpo/sdk` package
  - [ ] (P0) TypeScript types for trace/span/event
  - [ ] (P0) Build pipeline (tsup/rollup)
  - [ ] (P0) Node + browser compatibility plan
  - [ ] (P0) Unit tests (vitest/jest)

### 12.2 Core behaviors
  - [ ] (P0) UUID v4 generation using crypto API
  - [ ] (P0) Async dispatch with internal queue
  - [ ] (P0) Ring buffer cap (50MB) approximated via byte sizing
  - [ ] (P0) Batch splitting to 5MB max
  - [ ] (P0) Fail-open semantics default
  - [ ] (P0) Support Idempotency-Key header
  - [ ] (P0) Attribute namespace validation
  - [ ] (P1) Websocket optional (not required in v0.08)

### 12.3 ComfyUI integration path
  - [ ] (P1) Provide minimal snippet for ComfyUI custom node
  - [ ] (P1) Ensure packaging works in ComfyUI environment

---

## 13) SDK — Rust (v0.08)

### 13.1 Crate setup
  - [ ] (P0) Create `ovpo-sdk` crate
  - [ ] (P0) Provide feature flags:
        - reqwest / hyper transport
        - tokio runtime
        - serde
  - [ ] (P0) Unit tests
  - [ ] (P0) Example binary in /examples

### 13.2 Core behaviors
  - [ ] (P0) UUID v4 generation
  - [ ] (P0) Async dispatch using tokio channel
  - [ ] (P0) Ring buffer cap (50MB) as bounded VecDeque with byte accounting
  - [ ] (P0) Batch splitting (5MB)
  - [ ] (P0) Fail-open semantics
  - [ ] (P0) Idempotency headers
  - [ ] (P1) Optional: local spool to disk

---

## 14) UI (React) — Trace Explorer & Dashboards

### 14.1 UI foundation
  - [ ] (P0) Create React app under /ui (Vite/Next)
  - [ ] (P0) Basic layout:
        - tenant selector (if multi-tenant UI)
        - trace list
        - trace detail
        - dashboards
  - [ ] (P0) API client + auth token handling
  - [ ] (P0) Error handling + loading states
  - [ ] (P0) Pagination UI using cursors (not offsets)

### 14.2 Trace list view
  - [ ] (P0) Filters:
        - status
        - time range
        - tags
  - [ ] (P0) Sorting
  - [ ] (P0) Show key fields:
        - trace_id
        - status
        - created_at
        - duration (computed)
        - model name (from pipeline_config)
  - [ ] (P0) Cursor pagination controls
  - [ ] (P1) Saved searches (optional)

### 14.3 Trace detail view
  - [ ] (P0) Timeline view (spans)
  - [ ] (P0) Frame scrubber list:
        - frame_index
        - media_time_ms
        - key quality metrics
  - [ ] (P0) Thumbnail hover/preview:
        - uses signed URLs
  - [ ] (P0) Failure panel for FAILED traces
  - [ ] (P0) Tags + cost attribution display
  - [ ] (P1) Compare traces (v0.09+ or later)

### 14.4 Dashboards (minimal v0.08)
  - [ ] (P0) Throughput traces/day chart
  - [ ] (P0) Failure rate chart
  - [ ] (P0) p95 latency chart
  - [ ] (P0) Compute units by project chart
  - [ ] (P1) Quality trends chart (clip similarity)
  - [ ] (P1) Bottlenecks dashboard view

### 14.5 UI observability + security
  - [ ] (P0) Avoid leaking secrets in logs
  - [ ] (P0) CSP headers guidance (if hosting)
  - [ ] (P1) UI audit events:
        - TRACE_ACCESS triggered client-side or server-side

---

## 15) CLI Tooling (`ovpo-cli`)

### 15.1 CLI foundation
  - [ ] (P0) Create /cli project (Go/Rust/Python)
  - [ ] (P0) Commands:
        - ovpo-cli ping
        - ovpo-cli validate <json>
        - ovpo-cli traces list
        - ovpo-cli traces get <trace_id>
        - ovpo-cli analytics bottlenecks
        - ovpo-cli costs calculate --trace-id ...
  - [ ] (P0) Output formats:
        - table
        - json
        - csv (where applicable)

### 15.2 Admin commands (optional v0.08, recommended)
  - [ ] (P1) tenants create/list
  - [ ] (P1) api-keys create/revoke
  - [ ] (P1) retention run-now
  - [ ] (P1) gdpr delete-user

---

## 16) Compliance Suite (Testing Framework)

### 16.1 Framework implementation
  - [ ] (P0) Implement `ComplianceSuite` in Python
  - [ ] (P0) Provide default tests from spec:
        - trace completeness
        - span parenting
        - frame monotonicity
        - media_time monotonicity
        - observed_at skew tolerance
        - overhead check harness
        - fail-open test
  - [ ] (P0) Output:
        - summary
        - failures list
        - json report for CI
  - [ ] (P0) Provide fixtures pipeline for tests
  - [ ] (P1) Add distributed invariants tests (orphan reconciliation)

### 16.2 CI integration
  - [ ] (P0) Add GitHub Actions job:
        - run compliance suite on example pipelines
  - [ ] (P0) Gate merges on compliance pass for critical components
  - [ ] (P1) Add performance budget regression check

---

## 17) Performance Engineering & Benchmarks

### 17.1 SDK overhead measurement
  - [ ] (P0) Benchmark baseline vs instrumented for:
        - Python sync pipeline
        - Python async pipeline
  - [ ] (P0) Confirm <2% overhead target
  - [ ] (P0) Confirm <50MB resident memory overhead
  - [ ] (P0) Document results and methodology
  - [ ] (P1) Add deep profile mode benchmark (warn 10-20%)

### 17.2 Collector performance
  - [ ] (P0) Load test ingestion p99 < 50ms (target)
  - [ ] (P0) Ensure schema validation is fast enough
  - [ ] (P0) Tune JSON parsing and allocations
  - [ ] (P1) Add HTTP/2 and keepalive tuning

### 17.3 Processor performance
  - [ ] (P0) Validate processor lag < 5s p95 under target load
  - [ ] (P0) Batch write tuning to Postgres/ClickHouse
  - [ ] (P0) Backpressure strategy when downstream slow
  - [ ] (P1) Hot path profiling and optimization

### 17.4 Query performance
  - [ ] (P0) Ensure trace list p95 < 1s with typical filters
  - [ ] (P0) Ensure trace detail p95 < 1s for moderate event volume
  - [ ] (P1) Add caching for hottest endpoints

---

## 18) Security Hardening (Beyond basics)

### 18.1 Transport security
  - [ ] (P0) TLS 1.3 for all public endpoints
  - [ ] (P0) Internal TLS between services (recommended)
  - [ ] (P0) HSTS + secure headers guidance
  - [ ] (P1) mTLS option for collector in enterprise mode

### 18.2 Input hardening
  - [ ] (P0) Strict request size limits
  - [ ] (P0) Strict schema validation
  - [ ] (P0) Defensive JSON parsing (timeouts, depth limits)
  - [ ] (P0) Reject non-namespaced attributes

### 18.3 Secret handling
  - [ ] (P0) Ensure API keys never logged
  - [ ] (P0) Mask secrets in config dumps
  - [ ] (P0) Support reading secrets from env
  - [ ] (P1) Vault integration example

### 18.4 DB security
  - [ ] (P0) Use least-privilege DB roles:
        - collector role (if any)
        - processor role
        - query role
        - migration role
  - [ ] (P0) Parameterized queries everywhere
  - [ ] (P0) RLS enabled by default (recommended mode)
  - [ ] (P1) Encrypt backups guidance

### 18.5 Threat model validation
  - [ ] (P0) Run table-top security review using threat model section
  - [ ] (P0) Add security tests:
        - tenant data leakage attempts
        - invalid auth tokens
        - payload fuzzing
  - [ ] (P1) External pen test checklist template

---

## 19) Disaster Recovery & High Availability

### 19.1 Backups
  - [ ] (P0) Postgres hourly backups + retention 30d
  - [ ] (P0) ClickHouse daily backups + retention 90d
  - [ ] (P0) MinIO/S3 versioning guidance for artifacts
  - [ ] (P0) Document RTO/RPO targets and realistic expectations
  - [ ] (P1) Automated restore test (monthly)

### 19.2 HA deployment
  - [ ] (P0) Kubernetes manifests:
        - collector deployment + HPA
        - processor deployment + HPA
        - query api deployment + HPA
        - ui deployment
  - [ ] (P0) Anti-affinity rules
  - [ ] (P0) Liveness/readiness probes
  - [ ] (P0) Rolling update strategies
  - [ ] (P1) Multi-region DR plan docs

### 19.3 Incident runbooks
  - [ ] (P0) Runbook: high API latency
  - [ ] (P0) Runbook: processor lag
  - [ ] (P0) Runbook: storage out of disk
  - [ ] (P0) Runbook: queue outage
  - [ ] (P0) Runbook: auth outage / key rotation failure
  - [ ] (P1) Runbook: data corruption / PITR restore

---

## 20) Observability of OVPO (meta-monitoring)

### 20.1 Prometheus metrics (all services)
  - [ ] (P0) Standardize metric names + labels
  - [ ] (P0) Collector metrics complete
  - [ ] (P0) Processor metrics complete
  - [ ] (P0) Query API metrics complete
  - [ ] (P0) Dashboard JSON for Grafana starter pack
  - [ ] (P0) Alert rules starter pack:
        - collector error rate
        - processor lag
        - DB write failures
        - queue depth high
  - [ ] (P1) Export OTel traces for OVPO itself

### 20.2 Logging standards
  - [ ] (P0) JSON structured logs
  - [ ] (P0) Correlation:
        - request_id
        - tenant_id
        - trace_id (when applicable)
  - [ ] (P0) Log level conventions
  - [ ] (P1) PII scrubber for logs (optional)

---

## 21) Artifact Handling & Signed URLs

### 21.1 Signed URL service
  - [ ] (P0) Implement endpoint:
        - POST /v1/artifacts/signed-url (or similar)
  - [ ] (P0) Validate user has permission to access the trace/artifact
  - [ ] (P0) Emit ARTIFACT_DOWNLOAD audit event
  - [ ] (P0) Signed URL TTL defaults (e.g., 10 minutes)
  - [ ] (P0) Support schemes:
        - s3://, ovpo:// mapped to actual storage
  - [ ] (P1) Support range requests for large videos (if served via https)

### 21.2 Artifact integrity verification
  - [ ] (P1) Optional: verify sha256 on upload
  - [ ] (P1) Provide CLI command to verify checksum

---

## 22) “Open Source Feel” Polish (the stuff that makes people say “Samn!”)

### 22.1 Developer experience
  - [ ] (P0) Quickstart in README that works in <10 minutes
  - [ ] (P0) `docker compose up` brings full stack online
  - [ ] (P0) One sample pipeline that emits:
        - trace
        - spans
        - ~20 frame events
        - artifact refs to MinIO
  - [ ] (P0) UI shows that sample trace immediately
  - [ ] (P0) `make demo` does everything from cold start
  - [ ] (P1) “Architecture tour” doc with diagrams

### 22.2 Docs completeness
  - [ ] (P0) API reference docs generated from OpenAPI spec
  - [ ] (P0) Schema reference docs generated from JSON schema
  - [ ] (P0) SDK docs:
        - Python
        - JS
        - Rust
  - [ ] (P0) Deployment docs:
        - Docker compose
        - Kubernetes
  - [ ] (P0) Security docs:
        - threat model
        - key handling
        - RBAC
  - [ ] (P0) Retention/GDPR docs:
        - how deletion works
        - how tombstones work
  - [ ] (P1) FAQ (common confusion points)

### 22.3 Quality gates
  - [ ] (P0) Code coverage thresholds set per module
  - [ ] (P0) Linting is enforced in CI
  - [ ] (P0) Static type checks where applicable
  - [ ] (P0) Dependency update automation (Dependabot/Renovate)
  - [ ] (P1) Release checklist doc

---

## 23) OpenAPI / Contract Generation

### 23.1 API contract
  - [ ] (P0) Write OpenAPI spec for:
        - ingest/batch
        - traces list
        - trace detail
        - analytics endpoints
        - artifact signed URL
  - [ ] (P0) Generate server stubs OR validate implementation against OpenAPI
  - [ ] (P0) Generate typed clients (TS) for UI
  - [ ] (P1) Add Postman collection

---

## 24) Example Pipelines (the “prove it works” suite)

### 24.1 Minimal smoke pipeline
  - [ ] (P0) Example: “fake video gen” that emits deterministic frames (no GPU needed)
  - [ ] (P0) Emits spans: LOAD, TEXT_ENCODE, SAMPLING, DECODE, OUTPUT_ENCODE
  - [ ] (P0) Emits frame events with quality_metrics filled
  - [ ] (P0) Uploads thumbnails to MinIO (optional)
  - [ ] (P0) Sets output_manifest

### 24.2 Real GPU pipeline integration (RTX 4090 friendly)
  - [ ] (P1) Provide example integration with a local text-to-video model
  - [ ] (P1) Document environment setup for local inference
  - [ ] (P1) Provide “instrumentation hooks” only (avoid bundling model weights)
  - [ ] (P1) Include performance knobs:
        - frame_sampling_rate
        - flush_interval_sec
        - profile_mode

### 24.3 Failure scenarios
  - [ ] (P0) Example: simulate OOM failure (forced)
  - [ ] (P0) Example: simulate timeout failure
  - [ ] (P0) Example: simulate missing frames leading to PARTIAL
  - [ ] (P0) Validate UI shows failure object correctly

---

## 25) Integration with External Monitoring (Prom/Grafana, etc.)

### 25.1 Grafana starter kit
  - [ ] (P0) Provide dashboards JSON
  - [ ] (P0) Provide datasource configs
  - [ ] (P0) Provide alert rules examples

### 25.2 Exporters
  - [ ] (P1) Prometheus exporter built-in (already planned)
  - [ ] (P2) OTel metrics exporter

---

## 26) Packaging & Releases

### 26.1 Server releases
  - [ ] (P0) Versioned docker images:
        - ovpo/collector:v0.08.x
        - ovpo/processor:v0.08.x
        - ovpo/query-api:v0.08.x
        - ovpo/ui:v0.08.x
  - [ ] (P0) Multi-arch builds (amd64/arm64 where possible)
  - [ ] (P0) Release notes template

### 26.2 SDK releases
  - [ ] (P1) Publish Python package to PyPI
  - [ ] (P1) Publish TS package to npm
  - [ ] (P1) Publish Rust crate to crates.io
  - [ ] (P1) Semantic versioning policy for SDKs

### 26.3 Backwards compatibility policy
  - [ ] (P0) Collector supports N-1 schema versions logic (future)
  - [ ] (P0) For now, strict 0.08 only (or document if supporting 0.07)
  - [ ] (P1) Add schema negotiation headers for N-1 support

---

## 27) Deep Cuts (Advanced, but you’ll want them)

### 27.1 Reconciliation worker
  - [ ] (P1) Periodically reconcile orphan spans/events
  - [ ] (P1) Promote trace to PARTIAL when missing critical segments
  - [ ] (P1) Emit audit event for reconciliation actions (optional)

### 27.2 Data quality scoring
  - [ ] (P2) Add “completeness score” for trace:
        - expected frames vs observed
        - missing spans
        - schema violations
  - [ ] (P2) UI badge for completeness

### 27.3 Anti-abuse protections
  - [ ] (P1) Tenant quotas on stored traces
  - [ ] (P1) Reject pathological tag cardinality
  - [ ] (P1) Reject extreme attribute key spam

### 27.4 Cost accuracy improvements
  - [ ] (P2) Measure GPU seconds directly via sampling and integrate
  - [ ] (P2) Calibrate hardware factors with benchmarks

---

## 28) Definition of Done (global)

### 28.1 Core platform DoD (v0.08 complete)
  - [ ] Collector enforces schema, rate limit, idempotency, partial failures
  - [ ] Processor handles at-least-once delivery and dedupes correctly
  - [ ] Storage is populated (PG + CH) and query endpoints return correct joins
  - [ ] UI can browse traces and view a full trace timeline + frames
  - [ ] Audit events are logged and immutable
  - [ ] Retention job works and respects legal_hold
  - [ ] SDK (Python) can instrument and does fail-open with bounded memory
  - [ ] Compliance suite passes on example pipelines
  - [ ] Load test meets basic SLOs:
        - ingest p99 < 200ms (spec)
        - query p95 < 1s
        - data loss < 0.01% under test harness assumptions

### 28.2 “Samn!” DoD (the vibe)
  - [ ] One-command demo works on a clean machine
  - [ ] Docs are crisp and match reality
  - [ ] Naming is consistent across spec/schemas/code
  - [ ] Every invariant has a test
  - [ ] Every service exports metrics + health endpoints
  - [ ] There are no “TODO: security later” holes in the critical path

---

## 29) First Build Order (suggested execution sequence)

### Foundations
  - [ ] (P0) Monorepo structure + docker compose + migrations scaffolding
  - [ ] (P0) Schemas validated + CI schema checks
  - [ ] (P0) Collector skeleton with validation + auth + rate limiting

### Data path
  - [ ] (P0) Queue adapter + collector publishes
  - [ ] (P0) Processor consumes + writes PG + CH with dedupe
  - [ ] (P0) Query API returns trace list + trace detail

### SDK + UI
  - [ ] (P0) Python SDK emit trace/spans/events
  - [ ] (P0) UI trace list + trace detail timeline
  - [ ] (P0) Demo pipeline end-to-end

### Hardening
  - [ ] (P0) Idempotency correctness under retries
  - [ ] (P0) Retention job + deletion semantics
  - [ ] (P0) Audit immutability enforcement
  - [ ] (P0) Load test + SLO validation
