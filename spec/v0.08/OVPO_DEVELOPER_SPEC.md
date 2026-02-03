# OVPO — Open Video Pipeline Observatory
**Developer Specification v0.08**  
**Status:** Implementation-Ready Specification  
**Date:** February 3, 2026  
**Authors:** Core Team + Community Contributors  
**License:** Apache 2.0

---

## Document Control

| Version | Date | Status | Changes | Author |
|---------|------|--------|---------|--------|
| v0.05 | Dec 10, 2025 | Released | Initial canonical spec with JSON schemas | Core Team |
| v0.06 | Jan 15, 2026 | Released | Multi-tenancy, cost attribution, compliance | Core Team |
| v0.07 | Jan 28, 2026 | Released | Monitoring, alerting, DR, production patterns | Core Team |
| v0.08 | Feb 3, 2026 | **Current** | Fixed ID formats, queue semantics, threat model, complete schemas | Core Team |

**Planned Versions:**
- v0.09 (Q2 2026): Plugin architecture, custom metrics framework
- v1.0 (Q3 2026): Stabilized API, production GA

---

## 1. Purpose & Non-Goals

### 1.1 Purpose
OVPO is an open-source observability and debugging platform designed specifically for AI-driven video generation pipelines.

Its purpose is to make video generation systems:
- **Observable** — Fully traceable across the generation lifecycle (Prompt → Conditioning → Latent → Frame → Output).
- **Debuggable** — Explainable when quality degrades (artifacts, temporal drift, instability, desynchronization).
- **Measurable** — Quantified across latency, GPU cost, and quality signals.
- **Comparable** — Evaluated objectively across models, samplers, schedulers, and hyperparameters.
- **Collaborative** — Providing a shared, factual view for ML engineers, platform engineers, and product teams.
- **Auditable** — Ensuring compliance, cost attribution, and usage governance in multi-tenant environments.
- **Resilient** — Designed for high availability and disaster recovery in production environments.

**OVPO is not a video generator.**  
**OVPO is the infrastructure that explains video generation.**

### 1.2 Non-Goals
OVPO explicitly does **not**:
- Replace general-purpose APM platforms (Datadog, New Relic).
- Replace OpenTelemetry; OVPO aligns with OTel and defines video-specific semantics on top.
- Act as a model registry, feature store, or experiment tracker.
- Optimize or interfere with inference or rendering algorithms.
- Store production video payloads; it stores references only.
- Provide real-time inference serving or model hosting.
- Function as a content delivery network (CDN) for generated videos.

---

## 2. Specification Language

This document uses RFC 2119 terminology:

- **MUST** / **REQUIRED** / **SHALL**: Absolute requirement
- **MUST NOT** / **SHALL NOT**: Absolute prohibition
- **SHOULD** / **RECOMMENDED**: Strong recommendation (may ignore with justification)
- **SHOULD NOT** / **NOT RECOMMENDED**: Strong recommendation against
- **MAY** / **OPTIONAL**: Truly optional

---

## 3. Design Principles

### 3.1 Video-Native Observability
Traditional observability treats a **request** as the unit of work.  
OVPO treats a **generation job** as the unit of work and a **frame** as the unit of fidelity.

**Key Distinctions:**
- **Unit of Work:** Generation Job
- **Unit of Atomicity:** Frame or latent slice
- **Time Domains:**
  - Wall-clock time (latency, cost)
  - Media time (frame order, temporal stability)

### 3.2 Deterministic Traceability
Every generated artifact MUST be traceable via a globally unique `trace_id`.

Traceability MUST survive:
- Asynchronous execution (Celery, Kafka, Ray)
- Partial failures (OOM after N frames)
- Distributed inference (tensor/pipeline parallelism)
- Multi-region deployments

**Invariant:** A trace is immutable once status reaches terminal state (`COMPLETED`, `FAILED`, `CANCELLED`, `TIMEOUT`).

### 3.3 Low-Overhead Instrumentation
Video generation is compute- and memory-bound. Instrumentation MUST:

- **Non-blocking:** All instrumentation MUST be asynchronous.
- **Zero-Copy:** MUST NOT duplicate tensor data on the GPU.
- **Fail-Open:** Pipeline MUST continue if OVPO is down.
- **Budget:** <2% wall-clock impact, <50 MB resident memory per process.

### 3.4 Unopinionated Ingestion
OVPO MUST accept data from:
- UI tools (ComfyUI, A1111, InvokeAI)
- Python frameworks (Diffusers, AnimateDiff, ModelScope)
- Cloud wrappers (Runway, Pika, Luma)
- Custom inference code via SDKs

No execution model is assumed or enforced.

### 3.5 Privacy-First & Compliant
- No PII storage without explicit opt-in
- Prompt redaction via cryptographic hashing
- Immutable audit trails with cryptographic integrity
- GDPR/CCPA right-to-deletion support

### 3.6 Semantic Conventions (OpenTelemetry-Aligned)
**Mapping:**
- `VideoTrace` → OTel Trace
- `Span` → OTel Span
- `Frame Event` → OTel Span Event
- `Metrics` → OTel Metrics

**Attribute namespaces:**
- `ovpo.trace.*`
- `ovpo.span.*`
- `ovpo.frame.*`
- `ovpo.quality.*`
- `ovpo.gpu.*`
- `ovpo.artifact.*`

---

## 4. Core Domain Model

### 4.1 Identity & ID Format

**All IDs MUST be valid UUID v4 (RFC 4122) in canonical form:**

✅ **Correct:** `550e8400-e29b-41d4-a716-446655440000`  
❌ **Wrong:** `t-8888-9999`, `trace_12345`, `550e8400e29b41d4a716446655440000`

**ID Fields:**
- `trace_id`: UUID v4
- `span_id`: UUID v4
- `event_id`: UUID v4
- `batch_id`: UUID v4 (RECOMMENDED)

**ID Generation:**
- IDs MUST be generated client-side by SDK
- IDs MUST be stable across retries (same operation = same ID)
- UUIDs MUST be cryptographically random (not sequential)

**Storage:**
- IDs SHOULD be stored as native UUID type in databases
- IDs MUST be transmitted as canonical string format in JSON

### 4.2 VideoTrace (Root Entity)

A `VideoTrace` represents a single generation attempt.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trace_id` | UUID v4 | ✓ | Unique generation identifier |
| `parent_trace_id` | UUID | ○ | For multi-stage pipelines |
| `tenant_id` | String(128) | ✓ | Tenant/org identifier |
| `user_id_hash` | String(64) | ○ | SHA-256 hash of user identifier |
| `status` | Enum | ✓ | See Section 4.3 |
| `pipeline_config` | JSON | ✓ | Snapshot of configuration |
| `pipeline_config_ref` | URI | ○ | External reference (mutually exclusive with inline) |
| `input_context` | JSON | ✓ | Prompt, seed, conditioning |
| `output_manifest` | JSON | ○ | Output artifact references |
| `cost_attribution` | JSON | ○ | Cost center / chargeback tags |
| `failure` | JSON | ○ | Required if status=FAILED |
| `retry_count` | Integer | ○ | Number of retry attempts (default: 0) |
| `tags` | Map<String,String> | ○ | User-defined metadata |
| `created_at` | RFC3339 | ✓ | Submission time |
| `started_at` | RFC3339 | ○ | First GPU activity |
| `completed_at` | RFC3339 | ○ | Terminal state reached |
| `schema_version` | String | ✓ | `"0.08"` |

**Constraints:**
- If `pipeline_config_ref` is provided, `pipeline_config` MUST be empty `{}`
- `pipeline_config` MUST NOT exceed 64 KB when serialized
- `tags` keys MUST match `^[a-z0-9_-]+$` and values MUST NOT exceed 256 bytes

### 4.3 Trace Status Lifecycle

```
┌─────────┐
│ PENDING │ ← Trace created, not yet started
└────┬────┘
     │
     ▼
┌────────────┐
│ GENERATING │ ← Active generation in progress
└─────┬──────┘
      │
      ├──→ COMPLETED   (Success, all artifacts ready)
      ├──→ FAILED      (Error occurred, see failure object)
      ├──→ CANCELLED   (User or system cancelled)
      └──→ TIMEOUT     (Exceeded time limit)
      └──→ PARTIAL     (Completed with missing frames/data)
```

**Status Enum (Complete):**
- `PENDING`: Trace created, awaiting execution
- `GENERATING`: Active generation in progress
- `COMPLETED`: Successfully completed
- `FAILED`: Failed with error (MUST include `failure` object)
- `CANCELLED`: User-initiated or system-initiated cancellation
- `TIMEOUT`: Exceeded configured timeout
- `PARTIAL`: Completed but with incomplete data (e.g., missing frames)

**Terminal States:** `COMPLETED`, `FAILED`, `CANCELLED`, `TIMEOUT`, `PARTIAL`

**State Transitions (MUST):**
- `PENDING` → `GENERATING` → (terminal state)
- Direct transitions to terminal states are allowed (e.g., `PENDING` → `CANCELLED`)
- Transitions FROM terminal states MUST NOT occur (immutability)

### 4.4 Failure Object

**Required when `status = FAILED`:**

```json
{
  "kind": "oom | timeout | crash | cancelled | hardware_error | validation_error | unknown",
  "message": "Human-readable error description",
  "retryable": true,
  "stage": "SPAN_KIND_SAMPLING",
  "error_code": "CUDA_OUT_OF_MEMORY",
  "details": {
    "vram_requested_mb": 24576,
    "vram_available_mb": 16384,
    "stacktrace": "..."
  }
}
```

**Field Specifications:**
- `kind` (REQUIRED): Categorization for automated handling
- `message` (REQUIRED): MUST NOT exceed 2048 bytes
- `retryable` (REQUIRED): Boolean indicating if retry is recommended
- `stage` (OPTIONAL): Which span kind failed
- `error_code` (OPTIONAL): Machine-readable error identifier
- `details` (OPTIONAL): Structured additional context

### 4.5 Spans & Semantics

Standard span kinds for video generation (MUST be one of):

| Span Kind | Description | Key Attributes |
|-----------|-------------|----------------|
| `SPAN_KIND_LOAD` | Model loading / VRAM allocation | `vram_allocated_mb`, `model_name` |
| `SPAN_KIND_TEXT_ENCODE` | Text encoding (CLIP, T5) | `token_count`, `embedding_dimension` |
| `SPAN_KIND_SAMPLING` | Denoising loop (core generation) | `steps_completed`, `scheduler_type` |
| `SPAN_KIND_DECODE` | VAE Decode / Latent → RGB | `batch_size`, `decode_method` |
| `SPAN_KIND_POSTPROCESS` | Upscaling, interpolation | `operation_type`, `scale_factor` |
| `SPAN_KIND_OUTPUT_ENCODE` | FFmpeg encoding, codec conversion | `codec`, `bitrate_kbps` |
| `SPAN_KIND_GUARD` | Safety filters / NSFW detection | `filter_name`, `detected_flags` |
| `SPAN_KIND_QUEUE` | Time spent waiting | `queue_depth`, `queue_name` |

**Span Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `span_id` | UUID v4 | ✓ | Unique span identifier |
| `trace_id` | UUID v4 | ✓ | Parent trace |
| `parent_span_id` | UUID v4 | ○ | Parent span (for nesting) |
| `span_kind` | Enum | ✓ | One of the kinds above |
| `name` | String(128) | ✓ | Human-readable name |
| `start_time` | RFC3339 | ✓ | When span started |
| `end_time` | RFC3339 | ○ | When span ended (REQUIRED if status=OK) |
| `duration_ms` | Integer | ○ | Duration in milliseconds |
| `attributes` | JSON | ○ | Key-value metadata |
| `status` | Enum | ✓ | `OK` or `ERROR` |

**Attribute Constraints:**
- Attribute keys MUST start with a namespace (`ovpo.*`, `custom.*`)
- Attribute values MUST be one of: string (<1024 bytes), number, integer, boolean
- Total attributes size MUST NOT exceed 16 KB per span

### 4.6 Frame Events

Frame events are structured events emitted during sampling.

**Frame Event Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_id` | UUID v4 | ✓ | Unique event identifier |
| `trace_id` | UUID v4 | ✓ | Parent trace |
| `span_id` | UUID v4 | ✓ | Parent span |
| `event_type` | Enum | ✓ | `frame_generated`, `frame_error`, `frame_sampled` |
| `observed_at` | RFC3339 | ✓ | Wall-clock observation time |
| `frame_index` | Integer ≥0 | ✓ | Sequential frame number |
| `media_time_ms` | Integer ≥0 | ✓ | Position in video timeline |
| `step_index` | Integer ≥0 | ○ | Denoising step (if applicable) |
| `latent_stats` | JSON | ○ | Latent space statistics |
| `quality_metrics` | JSON | ○ | Quality measurements |
| `gpu_metrics` | JSON | ○ | GPU state snapshot |
| `artifact_refs` | Array | ○ | References to artifacts |
| `provenance` | JSON | ○ | Metric computation metadata |

**Sampling Strategy (RECOMMENDED):**
- Always record: first frame, last frame, frames where `event_type=frame_error`
- For short videos (<50 frames): Record every frame
- For long videos: Record every Nth frame (configurable, default N=10)

**Frame Ordering Invariants (MUST):**
- `frame_index` MUST be monotonically increasing within a trace
- `media_time_ms` MUST be monotonically increasing within a trace
- `observed_at` MAY be non-monotonic (clock skew tolerance: ±5 seconds)

### 4.7 Artifact Referencing

OVPO stores **references** to artifacts, not payload data.

**Identity Requirements (MUST):**
- Primary identity MUST be content-hash-based (SHA-256) OR immutable UUID
- URIs MUST follow standard schemes: `s3://`, `gs://`, `azure://`, `https://`, `ovpo://`
- Checksums MUST be provided for integrity verification

**Artifact Reference Schema:**

```json
{
  "kind": "thumbnail | latent_preview | primary_output | checkpoint",
  "uri": "s3://ovpo-ephemeral/traces/550e8400-.../thumb_042.jpg",
  "sha256": "a3f5b2e8c1d4f6a2b5c9e1f4d7a3b6c2e5f8a1d4b7c0e3f6a9b2c5e8f1d4a7b3",
  "content_type": "image/jpeg",
  "size_bytes": 45678,
  "ttl_hours": 168
}
```

**TTL Enforcement:**
- Artifacts with `ttl_hours` MUST be automatically deleted after expiry
- Deletion MUST be asynchronous (grace period: +24 hours)
- Deletion failures MUST be logged but MUST NOT block operations

---

## 5. Message Queue Semantics (REQUIRED)

### 5.1 Queue Requirements

The message queue between Collector and Processor MUST satisfy:

**Delivery Guarantee (MUST):**
- **At-least-once delivery** is REQUIRED
- Exactly-once is OPTIONAL (implementation-specific)
- Messages MUST NOT be silently dropped

**Ordering (SHOULD):**
- **Best-effort ordering per `trace_id`** is RECOMMENDED
- Total ordering across traces is NOT REQUIRED
- Consumers MUST tolerate out-of-order delivery

**Duplicate Tolerance (MUST):**
- Consumers MUST handle duplicate messages idempotently
- Duplicate detection window: ≥24 hours (REQUIRED)
- Duplicates MUST NOT cause data corruption or double-counting

**Message Size Limits (MUST):**
- Maximum message size: 10 MB (REQUIRED)
- Batches exceeding limit MUST be rejected with `PAYLOAD_TOO_LARGE`
- SDKs SHOULD implement automatic batch splitting

**Partitioning (RECOMMENDED):**
- Messages SHOULD be partitioned by `tenant_id` for isolation
- Within a tenant, partition by `trace_id` for ordering

### 5.2 Supported Queue Implementations

All implementations MUST satisfy Section 5.1 requirements:

| Implementation | Delivery | Ordering | Persistence | Notes |
|----------------|----------|----------|-------------|-------|
| **Kafka / Redpanda** | At-least-once | Per-partition | Yes | RECOMMENDED for production |
| **NATS JetStream** | At-least-once | Per-stream | Optional | Good for low-latency |
| **RabbitMQ** | At-least-once | Per-queue | Optional | Simple deployments |

**Configuration Example (Kafka):**
```properties
# Producer (SDK/Collector)
acks=all
retries=3
max.in.flight.requests.per.connection=5
enable.idempotence=true

# Consumer (Processor)
enable.auto.commit=false
isolation.level=read_committed
```

---

## 6. Idempotency & Deduplication (REQUIRED)

### 6.1 Idempotency Key

**Ingestion Endpoints MUST support `Idempotency-Key` header:**

```http
POST /v1/ingest/batch HTTP/1.1
Idempotency-Key: batch-550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json
```

**Behavior (MUST):**
- Requests with same `Idempotency-Key` MUST return identical response
- Deduplication window: ≥24 hours (REQUIRED)
- After window expires, key MAY be reused
- `Idempotency-Key` format: Any string ≤128 bytes (UUID RECOMMENDED)

**Response on Duplicate:**
```json
{
  "status": "accepted",
  "duplicate": true,
  "original_request_time": "2026-02-03T10:00:00Z",
  "processed_items": 2
}
```

### 6.2 Item-Level Deduplication

**Stable IDs (MUST):**
- `trace_id`, `span_id`, `event_id` MUST be stable across retries
- Same operation MUST generate same ID
- IDs MUST be generated client-side before transmission

**Deduplication Scope:**
- Deduplication is per-item (trace, span, event)
- Duplicate items within a batch MUST be accepted once
- Duplicate items across batches MUST be deduplicated

**Example:**
```json
{
  "items": [
    {"trace_id": "550e8400-...", "status": "GENERATING"},
    {"trace_id": "550e8400-...", "status": "GENERATING"}  // Duplicate within batch
  ]
}
```

**Response:**
```json
{
  "status": "accepted",
  "processed_items": 1,
  "duplicate_items": 1,
  "errors": []
}
```

### 6.3 Partial Failure Handling

**Collector Behavior (MUST):**
- Valid items MUST be accepted even if some items are invalid
- Invalid items MUST be reported in `errors` array
- Response MUST include both accepted and rejected counts

**Example:**
```json
{
  "status": "partial_failure",
  "processed_items": 2,
  "failed_items": 1,
  "errors": [
    {
      "item_index": 1,
      "item_type": "span",
      "code": "MISSING_FIELD",
      "field": "end_time",
      "message": "Field 'end_time' is required for status=OK spans"
    }
  ]
}
```

---

## 7. Data Retention & Lifecycle Policy

### 7.1 Retention Tiers (Authoritative)

| Data Type | Hot (Active) | Warm (Query) | Cold (Archive) | Purge After |
|-----------|--------------|--------------|----------------|-------------|
| **Traces (Metadata)** | 7 days | 90 days | 1 year | 2 years |
| **Spans** | 7 days | 90 days | 1 year | 2 years |
| **Frame Metrics** | 7 days | 30 days | 90 days | 180 days |
| **Audit Logs** | 30 days | 6 months | 7 years | Never (append-only) |
| **Ephemeral Artifacts** | 7 days | N/A | N/A | 30 days |
| **Primary Outputs** | User-controlled | User-controlled | User-controlled | User-controlled |

**Tier Definitions:**
- **Hot:** In-memory cache (Redis), fastest queries
- **Warm:** Primary database (Postgres, ClickHouse), indexed
- **Cold:** Archive storage (S3 Glacier), slower retrieval
- **Purge:** Hard deletion, irrecoverable

### 7.2 Deletion Semantics

**Hard Delete vs Tombstone:**

**Hard Delete (MUST):**
- Physical removal of data from all storage tiers
- Applied to: Frame metrics, ephemeral artifacts
- Trigger: Retention period expired OR GDPR deletion request

**Tombstone (MUST):**
- Logical deletion with marker record
- Applied to: Traces, spans (after GDPR deletion)
- Tombstone MUST include: `deletion_id`, `deleted_at`, `deleted_by`, `reason`
- Tombstones MUST be retained for 7 years (compliance)

**Tombstone Schema:**
```json
{
  "deletion_id": "del-550e8400-e29b-41d4-a716-446655440000",
  "resource_type": "trace",
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "org-acme",
  "deleted_at": "2026-02-03T10:00:00Z",
  "deleted_by": "admin-user-12345",
  "reason": "GDPR_REQUEST",
  "metadata": {
    "request_id": "gdpr-req-789",
    "original_created_at": "2025-12-01T00:00:00Z"
  }
}
```

### 7.3 Legal Hold Support

**Requirements for Enterprise Deployments:**

**Legal Hold Flag (MUST):**
- Traces MAY have `legal_hold: true` flag
- Data under legal hold MUST NOT be deleted automatically
- Legal hold MUST override retention policies

**Implementation:**
```sql
ALTER TABLE traces ADD COLUMN legal_hold BOOLEAN DEFAULT FALSE;

-- Retention job MUST skip legal hold
DELETE FROM traces
WHERE completed_at < NOW() - INTERVAL '2 years'
  AND legal_hold = FALSE;
```

### 7.4 Artifact Lifecycle (S3)

**Lifecycle Configuration (REQUIRED):**

```json
{
  "Rules": [
    {
      "Id": "TransitionEphemeral",
      "Prefix": "ephemeral/",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 7,
          "StorageClass": "INTELLIGENT_TIERING"
        }
      ],
      "Expiration": {
        "Days": 30
      }
    },
    {
      "Id": "ArchiveOldTraces",
      "Prefix": "traces/",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ]
    }
  ]
}
```

**Encryption (MUST):**
- All artifacts MUST be encrypted at rest (AES-256)
- Encryption method: SSE-S3 (server-side) OR SSE-KMS (customer-managed keys)
- Keys MUST be rotated annually

---

## 8. Audit Trail & Cryptographic Integrity

### 8.1 Immutability Definition

**"Immutable audit log" means (MUST):**

**Implementation Option A: Append-Only Table (REQUIRED for Basic)**
```sql
CREATE TABLE audit_log (
  audit_id UUID PRIMARY KEY,
  event_type VARCHAR(64) NOT NULL,
  actor_id VARCHAR(128) NOT NULL,
  resource_id VARCHAR(128) NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  details JSONB,
  -- Immutability enforcement
  CONSTRAINT no_updates CHECK (false)  -- Prevents UPDATE
);

-- Revoke UPDATE and DELETE
REVOKE UPDATE, DELETE ON audit_log FROM ALL;
GRANT INSERT, SELECT ON audit_log TO ovpo_app;
```

**Implementation Option B: Cryptographic Chain (RECOMMENDED for Enterprise)**
```json
{
  "audit_id": "aud-550e8400-e29b-41d4-a716-446655440000",
  "event_type": "TRACE_ACCESS",
  "timestamp": "2026-02-03T10:00:00Z",
  "previous_hash": "a3f5b2e8c1d4f6a2b5c9e1f4d7a3b6c2e5f8a1d4b7c0e3f6a9b2c5e8f1d4a7b3",
  "record_hash": "b6c8d1e4f7a0b3c6d9e2f5a8b1c4d7e0f3a6b9c2d5e8f1a4b7c0d3e6f9a2b5c8",
  "signature": "..."
}
```

**Hash Calculation (MUST):**
```python
import hashlib
import json

def calculate_record_hash(record: dict) -> str:
    # Canonical JSON (sorted keys, no whitespace)
    canonical = json.dumps(record, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode()).hexdigest()

def verify_chain(records: list) -> bool:
    for i in range(1, len(records)):
        expected_prev = calculate_record_hash(records[i-1])
        if records[i]['previous_hash'] != expected_prev:
            return False
    return True
```

### 8.2 Audit Event Types

**Required Events (MUST be logged):**

| Event Type | Description | Required Fields |
|------------|-------------|-----------------|
| `TRACE_ACCESS` | User viewed trace details | `trace_id`, `actor_id` |
| `TRACE_QUERY` | User executed query | `query_hash`, `result_count` |
| `ARTIFACT_DOWNLOAD` | User downloaded artifact | `artifact_uri`, `actor_id` |
| `TRACE_DELETE` | Admin deleted trace | `trace_id`, `reason` |
| `CONFIG_CHANGE` | System configuration modified | `config_key`, `old_value`, `new_value` |
| `USER_LOGIN` | User authenticated | `actor_id`, `auth_method` |
| `API_KEY_CREATED` | API key generated | `key_id`, `permissions` |
| `API_KEY_REVOKED` | API key revoked | `key_id`, `reason` |

**Audit Record Schema:**
```json
{
  "audit_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "TRACE_ACCESS",
  "actor_id": "user-abc-123",
  "actor_ip": "192.168.1.100",
  "resource_type": "trace",
  "resource_id": "550e8400-e29b-41d4-a716-446655440001",
  "tenant_id": "org-acme",
  "timestamp": "2026-02-03T10:00:00Z",
  "metadata": {
    "user_agent": "Mozilla/5.0...",
    "session_id": "sess-xyz-789"
  },
  "previous_hash": "...",
  "record_hash": "..."
}
```

---

## 9. Security & Threat Model

### 9.1 Trust Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│                         Trust Boundary Map                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Untrusted Zone]                                               │
│  ┌──────────────┐                                              │
│  │ SDK (Client) │  ← User code, potentially malicious          │
│  └──────┬───────┘                                              │
│         │ HTTPS/TLS 1.3 (Mutual Auth Optional)                 │
│  ───────┼────────────────────────── Trust Boundary 1           │
│         │                                                       │
│  [DMZ - Ingestion]                                              │
│  ┌──────▼───────┐                                              │
│  │  Collector   │  ← Rate limit, auth, validation             │
│  └──────┬───────┘                                              │
│         │ Internal Network (TLS)                               │
│  ───────┼────────────────────────── Trust Boundary 2           │
│         │                                                       │
│  [Trusted Zone - Processing]                                    │
│  ┌──────▼───────┐        ┌──────────┐                         │
│  │  Processor   │ ←────→ │   DB     │                         │
│  └──────────────┘        └──────────┘                         │
│         │                                                       │
│  ───────┼────────────────────────── Trust Boundary 3           │
│         │                                                       │
│  [Privileged Zone - Storage]                                    │
│  ┌──────▼───────┐                                              │
│  │  S3/Storage  │  ← Encryption keys, backups                 │
│  └──────────────┘                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 Attack Surfaces & Mitigations

| Attack Surface | Threat | Mitigation (MUST) |
|----------------|--------|-------------------|
| **Ingestion Endpoint** | Malicious payload, DDoS | Rate limiting (per tenant), schema validation, size limits |
| **Query Endpoint** | Unauthorized access, injection | Authentication, RBAC, parameterized queries |
| **Artifact URLs** | Unauthorized download | Signed URLs with expiration, access logs |
| **Database** | SQL injection, tenant leakage | Parameterized queries, RLS (see 9.3) |
| **Message Queue** | Message tampering | TLS in transit, consumer validation |
| **Audit Log** | Tampering, deletion | Immutability enforcement (see 8.1) |

### 9.3 Multi-Tenant Isolation (REQUIRED)

**Database Row-Level Security (MUST):**

**Option A: Application-Level Filtering (Minimum Required)**
```python
# Every query MUST include tenant filter
def get_traces(tenant_id: str, filters: dict):
    query = "SELECT * FROM traces WHERE tenant_id = %s"
    params = [tenant_id]
    # Add additional filters...
    return db.execute(query, params)

# Middleware enforcement
@require_tenant_context
def query_handler(request):
    tenant_id = extract_tenant_from_auth(request)
    # tenant_id MUST be injected into all queries
    return get_traces(tenant_id, request.filters)
```

**Option B: Database-Enforced RLS (RECOMMENDED)**
```sql
-- Enable RLS on all multi-tenant tables
ALTER TABLE traces ENABLE ROW LEVEL SECURITY;
ALTER TABLE spans ENABLE ROW LEVEL SECURITY;
ALTER TABLE frame_metrics ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY tenant_isolation_traces ON traces
  USING (tenant_id = current_setting('app.current_tenant_id'));

-- Application sets tenant context per session
SET app.current_tenant_id = 'org-acme';
```

**Testing Requirements (MUST):**
```python
# Automated test suite MUST verify
def test_tenant_isolation():
    # Create trace for tenant A
    trace_a = create_trace(tenant_id="org-a")
    
    # Try to access from tenant B context
    with tenant_context("org-b"):
        result = get_trace(trace_a.id)
        assert result is None or result == Forbidden
```

### 9.4 Prompt Handling & PII Protection

**Default Behavior (MUST):**
- Prompts MUST be stored as SHA-256 hash by default
- Plain text prompts MUST require explicit opt-in: `store_prompts_plaintext: true`
- SDKs MUST warn when plaintext storage is enabled

**Hashing Implementation:**
```python
import hashlib

def hash_prompt(prompt: str) -> str:
    """Hash prompt for deduplication without storing plaintext."""
    return hashlib.sha256(prompt.encode('utf-8')).hexdigest()

# Storage
trace_record = {
    "input_context": {
        "prompt_hash": hash_prompt(prompt),
        "prompt_length": len(prompt),
        # Optional: Store plaintext if opted-in
        "prompt_plaintext": prompt if config.store_prompts else None
    }
}
```

**PII Detection (SHOULD):**
- SDKs SHOULD implement optional PII detection
- Common patterns: email, phone, SSN, credit card
- If PII detected, SDK SHOULD redact or warn user

**Example:**
```python
import re

def detect_pii(text: str) -> list:
    patterns = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b'
    }
    detected = []
    for pii_type, pattern in patterns.items():
        if re.search(pattern, text):
            detected.append(pii_type)
    return detected

# SDK usage
if detect_pii(prompt):
    warnings.warn("Potential PII detected in prompt. Consider redacting.")
```

---

## 10. API Specifications (Complete)

### 10.1 Ingestion API

**POST /v1/ingest/batch**

**Request Limits (MUST):**
- Max request size: 5 MB
- Max items per batch: 5,000
- Max spans per trace per batch: 1,000
- Max events per span per batch: 10,000
- Max attributes per item: 100
- Max attribute size: 16 KB

**Headers:**
```http
POST /v1/ingest/batch HTTP/1.1
Host: api.ovpo.dev
Authorization: Bearer ovpo_sk_abc123...
Content-Type: application/json
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
X-OVPO-Schema-Version: 0.08
```

**Request Body:**
```json
{
  "schema_version": "0.08",
  "batch_id": "550e8400-e29b-41d4-a716-446655440001",
  "sent_at": "2026-02-03T10:00:00Z",
  "items": [
    {
      "type": "trace",
      "trace_id": "550e8400-e29b-41d4-a716-446655440002",
      "tenant_id": "org-acme",
      "status": "GENERATING",
      "pipeline_config": {"model": "wan-2.1"},
      "input_context": {"prompt_hash": "a3f5..."},
      "created_at": "2026-02-03T09:59:55Z",
      "schema_version": "0.08"
    }
  ]
}
```

**Success Response (200 OK):**
```json
{
  "status": "accepted",
  "batch_id": "550e8400-e29b-41d4-a716-446655440001",
  "processed_items": 1,
  "duplicate_items": 0,
  "failed_items": 0,
  "errors": [],
  "processing_time_ms": 45
}
```

**Error Responses:**

| Status | Code | Description | Retry |
|--------|------|-------------|-------|
| 400 | `INVALID_SCHEMA` | Schema validation failed | No |
| 401 | `UNAUTHORIZED` | Invalid/missing API key | No |
| 403 | `FORBIDDEN` | Tenant access denied | No |
| 413 | `PAYLOAD_TOO_LARGE` | Request exceeds size limit | Split batch |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests | Yes (after delay) |
| 500 | `INTERNAL_ERROR` | Server error | Yes (exponential backoff) |
| 503 | `SERVICE_UNAVAILABLE` | Temporary unavailability | Yes (exponential backoff) |

### 10.2 Query API

**GET /v1/traces**

**Query Parameters:**
- `tenant_id`: Auto-applied from auth token (MUST NOT be user-supplied)
- `status`: Filter by status (comma-separated)
- `start_date`: ISO 8601 (inclusive)
- `end_date`: ISO 8601 (exclusive)
- `tags`: Key-value filters (e.g., `env=prod,model=wan-2.1`)
- `limit`: Max results (default: 100, max: 1000)
- `cursor`: Pagination cursor (opaque string)
- `order_by`: Sort field (default: `created_at`)
- `order_dir`: `asc` or `desc` (default: `desc`)

**Pagination (REQUIRED):**
- MUST use cursor-based pagination (NOT offset)
- Cursor format: Base64-encoded JSON: `{"last_id": "...", "last_timestamp": "..."}`
- Stable ordering MUST be guaranteed (e.g., `ORDER BY created_at DESC, trace_id DESC`)

**Example Request:**
```bash
curl -G "https://api.ovpo.dev/v1/traces" \
  -H "Authorization: Bearer ovpo_sk_abc123" \
  -d "status=FAILED,TIMEOUT" \
  -d "start_date=2026-02-01T00:00:00Z" \
  -d "limit=50" \
  -d "cursor=eyJsYXN0X2lkIjoi..."
```

**Response:**
```json
{
  "traces": [
    {
      "trace_id": "550e8400-e29b-41d4-a716-446655440002",
      "status": "FAILED",
      "created_at": "2026-02-03T10:00:00Z",
      "failure": {
        "kind": "oom",
        "message": "CUDA out of memory"
      }
    }
  ],
  "pagination": {
    "limit": 50,
    "next_cursor": "eyJsYXN0X2lkIjoi...",
    "has_more": true
  },
  "query_time_ms": 125
}
```

**Rate Limiting (Query Endpoints):**
- Default: 100 requests/minute per tenant
- Burst: 200 requests in 10 seconds
- Heavy queries (large result sets): Count as multiple requests

**Consistency Model:**
- **Eventual consistency** between ingestion and query
- Typical lag: <5 seconds (p95)
- Queries MAY return stale data during processor lag
- Fresh data guarantee: Poll with `If-Modified-Since` header

### 10.3 Error Code Reference (Complete)

| Code | HTTP | Description | Retry | Fix |
|------|------|-------------|-------|-----|
| `MISSING_FIELD` | 400 | Required field not provided | No | Add field |
| `INVALID_FORMAT` | 400 | Field format invalid | No | Correct format |
| `INVALID_UUID` | 400 | Malformed UUID | No | Use valid UUID v4 |
| `SCHEMA_MISMATCH` | 400 | Unsupported schema version | No | Update SDK |
| `FIELD_TOO_LARGE` | 400 | Field exceeds size limit | No | Reduce size |
| `TOO_MANY_ITEMS` | 400 | Batch exceeds item limit | No | Split batch |
| `INVALID_TRANSITION` | 400 | Invalid status transition | No | Check state machine |
| `UNAUTHORIZED` | 401 | Invalid/missing API key | No | Verify API key |
| `FORBIDDEN` | 403 | Insufficient permissions | No | Check RBAC |
| `NOT_FOUND` | 404 | Resource not found | No | Verify ID |
| `CONFLICT` | 409 | Resource already exists | No | Check for duplicates |
| `PAYLOAD_TOO_LARGE` | 413 | Request too large | No | Reduce payload |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests | Yes | Wait `retry_after` seconds |
| `INTERNAL_ERROR` | 500 | Server error | Yes | Retry with backoff |
| `SERVICE_UNAVAILABLE` | 503 | Temporary unavailability | Yes | Retry with backoff |

---

## 11. Complete JSON Schemas

### 11.1 Ingest Batch Envelope

**File: `schemas/v0.08/ingest_batch.json`**

```json
{
  "$id": "https://ovpo.dev/schemas/v0.08/ingest_batch.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "OVPO Ingest Batch v0.08",
  "type": "object",
  "required": ["schema_version", "batch_id", "sent_at", "items"],
  "properties": {
    "schema_version": {
      "const": "0.08",
      "description": "Schema version for this batch"
    },
    "batch_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique batch identifier (UUID v4 recommended)"
    },
    "sent_at": {
      "type": "string",
      "format": "date-time",
      "description": "Timestamp when batch was sent (RFC3339)"
    },
    "idempotency_key": {
      "type": "string",
      "maxLength": 128,
      "description": "Optional idempotency key for deduplication"
    },
    "items": {
      "type": "array",
      "minItems": 1,
      "maxItems": 5000,
      "items": {
        "oneOf": [
          {"$ref": "trace.json"},
          {"$ref": "span.json"},
          {"$ref": "frame_event.json"}
        ]
      }
    }
  },
  "additionalProperties": false
}
```

### 11.2 Trace Schema

**File: `schemas/v0.08/trace.json`**

```json
{
  "$id": "https://ovpo.dev/schemas/v0.08/trace.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "OVPO VideoTrace v0.08",
  "type": "object",
  "required": [
    "type",
    "schema_version",
    "trace_id",
    "tenant_id",
    "status",
    "pipeline_config",
    "input_context",
    "created_at"
  ],
  "properties": {
    "type": {"const": "trace"},
    "schema_version": {"const": "0.08"},
    
    "trace_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique trace identifier (UUID v4)"
    },
    "parent_trace_id": {
      "type": "string",
      "format": "uuid",
      "description": "Parent trace for multi-stage pipelines"
    },
    "tenant_id": {
      "type": "string",
      "maxLength": 128,
      "pattern": "^[a-z0-9-]+$",
      "description": "Tenant/organization identifier"
    },
    "user_id_hash": {
      "type": "string",
      "pattern": "^[a-f0-9]{64}$",
      "description": "SHA-256 hash of user identifier"
    },
    
    "status": {
      "type": "string",
      "enum": ["PENDING", "GENERATING", "COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "PARTIAL"],
      "description": "Current trace status"
    },
    
    "pipeline_config": {
      "type": "object",
      "description": "Generation configuration snapshot"
    },
    "pipeline_config_ref": {
      "type": "string",
      "format": "uri",
      "maxLength": 2048,
      "description": "External reference to large config"
    },
    
    "input_context": {
      "type": "object",
      "required": ["prompt_hash"],
      "properties": {
        "prompt_hash": {
          "type": "string",
          "pattern": "^[a-f0-9]{64}$",
          "description": "SHA-256 hash of prompt"
        },
        "prompt_plaintext": {
          "type": "string",
          "maxLength": 10000,
          "description": "Optional plaintext prompt (requires opt-in)"
        },
        "negative_prompt_hash": {
          "type": "string",
          "pattern": "^[a-f0-9]{64}$"
        },
        "seed": {
          "type": "integer",
          "minimum": 0
        }
      },
      "additionalProperties": true
    },
    
    "output_manifest": {
      "$ref": "artifact_manifest.json"
    },
    
    "cost_attribution": {
      "type": "object",
      "properties": {
        "project": {"type": "string", "maxLength": 128},
        "center": {"type": "string", "maxLength": 128},
        "campaign": {"type": "string", "maxLength": 128},
        "tags": {
          "type": "object",
          "additionalProperties": {"type": "string", "maxLength": 256}
        }
      },
      "additionalProperties": false
    },
    
    "failure": {
      "type": "object",
      "required": ["kind", "message", "retryable"],
      "properties": {
        "kind": {
          "type": "string",
          "enum": ["oom", "timeout", "crash", "cancelled", "hardware_error", "validation_error", "unknown"]
        },
        "message": {"type": "string", "maxLength": 2048},
        "retryable": {"type": "boolean"},
        "stage": {"type": "string", "maxLength": 64},
        "error_code": {"type": "string", "maxLength": 64},
        "details": {"type": "object"}
      },
      "additionalProperties": false
    },
    
    "retry_count": {
      "type": "integer",
      "minimum": 0,
      "default": 0
    },
    
    "tags": {
      "type": "object",
      "additionalProperties": {"type": "string", "maxLength": 256},
      "maxProperties": 50
    },
    
    "created_at": {"type": "string", "format": "date-time"},
    "started_at": {"type": "string", "format": "date-time"},
    "completed_at": {"type": "string", "format": "date-time"}
  },
  
  "allOf": [
    {
      "if": {
        "properties": {"status": {"const": "FAILED"}},
        "required": ["status"]
      },
      "then": {
        "required": ["failure"]
      }
    },
    {
      "if": {
        "properties": {"pipeline_config_ref": {"type": "string"}},
        "required": ["pipeline_config_ref"]
      },
      "then": {
        "properties": {
          "pipeline_config": {"type": "object", "maxProperties": 0}
        }
      }
    }
  ],
  
  "additionalProperties": false
}
```

### 11.3 Span Schema

**File: `schemas/v0.08/span.json`**

```json
{
  "$id": "https://ovpo.dev/schemas/v0.08/span.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "OVPO Span v0.08",
  "type": "object",
  "required": [
    "type",
    "schema_version",
    "span_id",
    "trace_id",
    "span_kind",
    "name",
    "start_time",
    "status"
  ],
  "properties": {
    "type": {"const": "span"},
    "schema_version": {"const": "0.08"},
    
    "span_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique span identifier (UUID v4)"
    },
    "trace_id": {
      "type": "string",
      "format": "uuid",
      "description": "Parent trace ID"
    },
    "parent_span_id": {
      "type": "string",
      "format": "uuid",
      "description": "Parent span for nesting"
    },
    
    "span_kind": {
      "type": "string",
      "enum": [
        "SPAN_KIND_LOAD",
        "SPAN_KIND_TEXT_ENCODE",
        "SPAN_KIND_SAMPLING",
        "SPAN_KIND_DECODE",
        "SPAN_KIND_POSTPROCESS",
        "SPAN_KIND_OUTPUT_ENCODE",
        "SPAN_KIND_GUARD",
        "SPAN_KIND_QUEUE"
      ]
    },
    
    "name": {
      "type": "string",
      "maxLength": 128,
      "description": "Human-readable span name"
    },
    
    "start_time": {
      "type": "string",
      "format": "date-time",
      "description": "When span started (RFC3339)"
    },
    "end_time": {
      "type": "string",
      "format": "date-time",
      "description": "When span ended (required if status=OK)"
    },
    "duration_ms": {
      "type": "integer",
      "minimum": 0,
      "description": "Duration in milliseconds"
    },
    
    "attributes": {
      "type": "object",
      "maxProperties": 100,
      "patternProperties": {
        "^(ovpo|custom)\\.[a-z0-9_.]+$": {
          "oneOf": [
            {"type": "string", "maxLength": 1024},
            {"type": "number"},
            {"type": "integer"},
            {"type": "boolean"}
          ]
        }
      },
      "additionalProperties": false
    },
    
    "status": {
      "type": "string",
      "enum": ["OK", "ERROR"]
    }
  },
  
  "allOf": [
    {
      "if": {
        "properties": {"status": {"const": "OK"}},
        "required": ["status"]
      },
      "then": {
        "required": ["end_time"]
      }
    }
  ],
  
  "additionalProperties": false
}
```

### 11.4 Frame Event Schema

**File: `schemas/v0.08/frame_event.json`**

```json
{
  "$id": "https://ovpo.dev/schemas/v0.08/frame_event.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "OVPO Frame Event v0.08",
  "type": "object",
  "required": [
    "type",
    "schema_version",
    "event_id",
    "trace_id",
    "span_id",
    "event_type",
    "observed_at",
    "frame_index",
    "media_time_ms"
  ],
  "properties": {
    "type": {"const": "event"},
    "schema_version": {"const": "0.08"},
    
    "event_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique event identifier (UUID v4)"
    },
    "trace_id": {
      "type": "string",
      "format": "uuid"
    },
    "span_id": {
      "type": "string",
      "format": "uuid"
    },
    
    "event_type": {
      "type": "string",
      "enum": ["frame_generated", "frame_error", "frame_sampled"]
    },
    
    "observed_at": {
      "type": "string",
      "format": "date-time",
      "description": "Wall-clock observation time"
    },
    
    "frame_index": {
      "type": "integer",
      "minimum": 0,
      "description": "Sequential frame number (MUST be monotonic)"
    },
    "media_time_ms": {
      "type": "integer",
      "minimum": 0,
      "description": "Position in video timeline (MUST be monotonic)"
    },
    
    "step_index": {
      "type": "integer",
      "minimum": 0,
      "description": "Denoising step index"
    },
    
    "latent_stats": {
      "type": "object",
      "properties": {
        "mean": {"type": "number"},
        "std_dev": {"type": "number", "minimum": 0},
        "min_val": {"type": "number"},
        "max_val": {"type": "number"},
        "nan_count": {"type": "integer", "minimum": 0},
        "inf_count": {"type": "integer", "minimum": 0}
      },
      "additionalProperties": false
    },
    
    "quality_metrics": {
      "type": "object",
      "properties": {
        "motion_score": {"type": "number", "minimum": 0},
        "temporal_consistency": {"type": "number", "minimum": 0, "maximum": 1},
        "contrast_ratio": {"type": "number", "minimum": 0},
        "brightness_avg": {"type": "number", "minimum": 0, "maximum": 255},
        "edge_density": {"type": "number", "minimum": 0, "maximum": 1},
        "noise_estimate": {"type": "number", "minimum": 0},
        "clip_text_similarity": {"type": "number", "minimum": -1, "maximum": 1},
        "clip_image_similarity": {"type": "number", "minimum": -1, "maximum": 1},
        "aesthetic_score": {"type": "number", "minimum": 0, "maximum": 10},
        "artifact_score": {"type": "number", "minimum": 0, "maximum": 1},
        "nsfw_score": {"type": "number", "minimum": 0, "maximum": 1}
      },
      "additionalProperties": true
    },
    
    "gpu_metrics": {
      "type": "object",
      "properties": {
        "vram_used_mb": {"type": "integer", "minimum": 0},
        "gpu_utilization_pct": {"type": "integer", "minimum": 0, "maximum": 100},
        "temperature_c": {"type": "integer", "minimum": 0, "maximum": 120}
      },
      "additionalProperties": false
    },
    
    "artifact_refs": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["kind", "uri"],
        "properties": {
          "kind": {"type": "string", "maxLength": 64},
          "uri": {"type": "string", "format": "uri", "maxLength": 2048},
          "sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
          "content_type": {"type": "string", "maxLength": 128},
          "size_bytes": {"type": "integer", "minimum": 0},
          "ttl_hours": {"type": "integer", "minimum": 1}
        },
        "additionalProperties": false
      }
    },
    
    "provenance": {
      "type": "object",
      "required": ["source", "source_version"],
      "properties": {
        "source": {
          "type": "string",
          "enum": ["sdk", "processor"]
        },
        "source_version": {"type": "string", "maxLength": 64},
        "algorithm_id": {"type": "string", "maxLength": 128},
        "computed_at": {"type": "string", "format": "date-time"}
      },
      "additionalProperties": false
    }
  },
  
  "additionalProperties": false
}
```

### 11.5 Artifact Manifest Schema

**File: `schemas/v0.08/artifact_manifest.json`**

```json
{
  "$id": "https://ovpo.dev/schemas/v0.08/artifact_manifest.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "OVPO Artifact Manifest v0.08",
  "type": "object",
  "properties": {
    "primary_output": {
      "type": "object",
      "required": ["url", "format", "checksum"],
      "properties": {
        "url": {"type": "string", "format": "uri", "maxLength": 2048},
        "format": {"type": "string", "maxLength": 32},
        "codec": {"type": "string", "maxLength": 64},
        "resolution": {"type": "string", "pattern": "^\\d+x\\d+$"},
        "duration_sec": {"type": "number", "minimum": 0},
        "file_size_bytes": {"type": "integer", "minimum": 0},
        "checksum": {
          "type": "string",
          "pattern": "^(sha256|md5):[a-f0-9]{32,64}$",
          "description": "Format: algorithm:hash"
        }
      },
      "additionalProperties": false
    },
    "intermediate_artifacts": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["type", "url", "checksum"],
        "properties": {
          "type": {"type": "string", "maxLength": 64},
          "url": {"type": "string", "format": "uri", "maxLength": 2048},
          "ttl_hours": {"type": "integer", "minimum": 1},
          "checksum": {
            "type": "string",
            "pattern": "^(sha256|md5):[a-f0-9]{32,64}$"
          }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

---

## 12. Cost Model & Compute Units

### 12.1 Compute Unit Definition

**Compute units are dimensionless and implementation-agnostic.**

$$\text{Compute Units} = \sum_{i} (\text{Duration}_i \times \text{Hardware Factor}_i)$$

Where:
- $\text{Duration}_i$ = Span duration in seconds
- $\text{Hardware Factor}_i$ = Normalization factor from configuration

### 12.2 Hardware Factor Configuration

**Hardware factors are CONFIGURABLE per deployment:**

**Example Default Configuration:**
```json
{
  "hardware_factors": {
    "rtx_4090": 1.0,
    "a100_40gb": 2.5,
    "h100": 4.0,
    "v100": 0.8,
    "custom_gpu": 1.5
  },
  "storage_rates_per_gb_month": {
    "hot": 0.50,
    "warm": 0.10,
    "cold": 0.023
  }
}
```

**Deployment-Specific Override:**
```bash
# Set via environment variable
export OVPO_HARDWARE_FACTORS='{"custom_accelerator": 3.0}'

# Or via configuration file
ovpo-server --config hardware_factors.json
```

### 12.3 Cost Calculation API

**GET /v1/analytics/costs/calculate**

**Request:**
```json
{
  "trace_ids": ["550e8400-..."],
  "pricing_profile": "default"
}
```

**Response:**
```json
{
  "total_compute_units": 125.5,
  "total_storage_gb_hours": 50.2,
  "breakdown": [
    {
      "trace_id": "550e8400-...",
      "compute_units": 125.5,
      "storage_gb_hours": 50.2,
      "spans": [
        {
          "span_kind": "SPAN_KIND_SAMPLING",
          "duration_sec": 150.0,
          "hardware_factor": 1.0,
          "compute_units": 150.0
        }
      ]
    }
  ],
  "pricing_profile": "default",
  "currency": null
}
```

**Note:** Currency and actual costs are NOT part of the core spec. Billing systems should query compute units and apply their own pricing.

---

## 13. Testing & Validation Framework (Enhanced)

### 13.1 Observability Compliance Suite

**Test Cases (MUST pass before production):**

```python
from ovpo.testing import ComplianceSuite

suite = ComplianceSuite()

# Test 1: Trace Completeness
@suite.test
def test_trace_completeness(trace):
    """All spans must be linked to parent."""
    for span in trace.spans:
        assert span.trace_id == trace.trace_id
        if span.parent_span_id:
            parent_exists = any(s.span_id == span.parent_span_id for s in trace.spans)
            assert parent_exists, f"Orphaned span: {span.span_id}"

# Test 2: Frame Index Monotonicity
@suite.test
def test_frame_monotonicity(trace):
    """Frame indices must be monotonically increasing."""
    events = sorted(trace.events, key=lambda e: e.frame_index)
    for i in range(len(events) - 1):
        assert events[i+1].frame_index >= events[i].frame_index

# Test 3: Media Time Monotonicity
@suite.test
def test_media_time_monotonicity(trace):
    """Media time must be monotonically increasing."""
    events = sorted(trace.events, key=lambda e: e.frame_index)
    for i in range(len(events) - 1):
        assert events[i+1].media_time_ms >= events[i].media_time_ms

# Test 4: Timestamp Skew Tolerance
@suite.test
def test_timestamp_skew_tolerance(trace):
    """observed_at allowed to be non-monotonic within 5 second tolerance."""
    events = sorted(trace.events, key=lambda e: e.frame_index)
    MAX_SKEW_SEC = 5
    for i in range(len(events) - 1):
        delta = (events[i+1].observed_at - events[i].observed_at).total_seconds()
        # Allow negative delta up to MAX_SKEW_SEC
        if delta < 0:
            assert abs(delta) <= MAX_SKEW_SEC, \
                f"Clock skew exceeds tolerance: {delta}s"

# Test 5: Overhead Check
@suite.test
def test_overhead(baseline_duration_sec, instrumented_duration_sec):
    """Instrumentation overhead must be <2%."""
    overhead_pct = ((instrumented_duration_sec - baseline_duration_sec) / 
                    baseline_duration_sec) * 100
    assert overhead_pct < 2.0, f"Overhead {overhead_pct:.2f}% exceeds 2% limit"

# Test 6: Fail-Open Behavior
@suite.test
def test_fail_open(pipeline, ovpo_client):
    """Pipeline must continue if OVPO is unavailable."""
    # Simulate OVPO down
    ovpo_client.endpoint = "http://unreachable:9999"
    
    # Pipeline should complete successfully
    result = pipeline.run()
    assert result.success, "Pipeline failed when OVPO was down"

# Run suite
results = suite.run(my_pipeline)
print(results.summary())
```

### 13.2 Distributed System Invariants

**Clock Skew Handling:**

```python
def validate_frame_ordering(events: List[FrameEvent]) -> ValidationResult:
    """
    Validate frame ordering with distributed system considerations.
    
    Invariants:
    1. frame_index MUST be strictly monotonic
    2. media_time_ms MUST be monotonic
    3. observed_at MAY be non-monotonic within tolerance
    """
    errors = []
    
    sorted_by_index = sorted(events, key=lambda e: e.frame_index)
    
    # Check frame_index monotonicity (strict)
    for i in range(len(sorted_by_index) - 1):
        curr = sorted_by_index[i]
        next = sorted_by_index[i + 1]
        
        if next.frame_index <= curr.frame_index:
            errors.append(f"Non-monotonic frame_index: {curr.frame_index} -> {next.frame_index}")
    
    # Check media_time_ms monotonicity
    for i in range(len(sorted_by_index) - 1):
        curr = sorted_by_index[i]
        next = sorted_by_index[i + 1]
        
        if next.media_time_ms < curr.media_time_ms:
            errors.append(f"Non-monotonic media_time_ms at frame {next.frame_index}")
    
    # Check observed_at with skew tolerance
    MAX_SKEW_SEC = 5
    for i in range(len(sorted_by_index) - 1):
        curr = sorted_by_index[i]
        next = sorted_by_index[i + 1]
        
        delta_sec = (next.observed_at - curr.observed_at).total_seconds()
        if delta_sec < -MAX_SKEW_SEC:
            errors.append(
                f"Clock skew exceeds {MAX_SKEW_SEC}s tolerance: "
                f"{delta_sec:.2f}s between frames {curr.frame_index} and {next.frame_index}"
            )
    
    return ValidationResult(
        passed=len(errors) == 0,
        errors=errors
    )
```

---

## 14. Implementation Roadmap

### 14.1 Release Plan

| Phase | Target | Deliverables | Status |
|-------|--------|--------------|--------|
| **v0.05** | Dec 2025 | Core domain model, basic schemas | ✅ Released |
| **v0.06** | Jan 2026 | Multi-tenancy, cost attribution | ✅ Released |
| **v0.07** | Jan 2026 | Monitoring, alerting, DR | ✅ Released |
| **v0.08** | Feb 2026 | Fixed IDs, queue semantics, complete schemas | ✅ **Current** |
| **v0.09** | Q2 2026 | Plugin architecture, custom metrics | 🚧 Planning |
| **v1.0** | Q3 2026 | Stabilized API, production GA | 📅 Scheduled |

### 14.2 Breaking Changes Policy

**Before v1.0:**
- Breaking changes allowed with minor version bump (0.x → 0.y)
- Deprecation notice: 1 version minimum
- Migration guide required

**After v1.0:**
- Breaking changes require major version bump (1.x → 2.0)
- Deprecation notice: 6 months minimum
- Automated migration tooling required

---

## 15. Success Criteria & Metrics

OVPO is successful when:

**Technical Metrics:**
- [ ] Debugging time: <5 minutes to root cause (was: >30 minutes)
- [ ] Instrumentation overhead: <2% wall-clock, <50 MB memory
- [ ] Uptime: 99.9% (measured monthly)
- [ ] Data loss: <0.01% (measured monthly)
- [ ] Query latency: <1s p95

**Adoption Metrics:**
- [ ] >1,000 active traces/day across all tenants
- [ ] >50% of production pipelines instrumented
- [ ] >10 external contributors
- [ ] >500 GitHub stars

**Quality Metrics:**
- [ ] Documentation coverage: 100% of public APIs
- [ ] Test coverage: >80% code, 100% critical paths
- [ ] Security audit: Passed external pen test
- [ ] Compliance: SOC 2 Type II certified (enterprise)

---

## Appendix A — Reserved Attribute Namespaces

**Core Namespaces (Reserved):**

| Namespace | Description | Examples |
|-----------|-------------|----------|
| `ovpo.*` | Core OVPO attributes | `ovpo.trace.version`, `ovpo.sdk.language` |
| `otel.*` | OpenTelemetry compatibility | `otel.span.kind` |
| `gpu.*` | GPU-specific metrics | `gpu.cuda.version`, `gpu.driver.version` |
| `model.*` | Model metadata | `model.name`, `model.checkpoint` |

**Custom Namespaces:**

Users MUST use `custom.*` prefix for custom attributes:
- ✅ `custom.my_metric`
- ✅ `custom.company.experiment_id`
- ❌ `my_metric` (rejected)
- ❌ `ovpo.my_metric` (collision)

**Collision Prevention:**
- Attributes without namespace prefix MUST be rejected
- Validators MUST enforce namespace rules

---

## Appendix B — Glossary

| Term | Definition |
|------|------------|
| **Trace** | A single video generation attempt from start to finish |
| **Span** | A contiguous segment of work within a trace |
| **Frame Event** | Metadata about a single frame in the generation |
| **Artifact** | An output file (video, thumbnail, latent) |
| **Tenant** | An organization or user account in multi-tenant mode |
| **Cost Attribution** | Tags for chargeback and billing |
| **Provenance** | Metadata about how a metric was computed |
| **Schema Version** | Version of the data format (e.g., "0.08") |
| **Idempotency Key** | Unique key to prevent duplicate ingestion |
| **Tombstone** | Record proving data was deleted (GDPR compliance) |
| **Compute Units** | Dimensionless measure of computational work |
| **Terminal State** | Final immutable trace status |
| **Fail-Open** | System continues operating despite dependency failure |

---

## Appendix C — Implementation Checklist

**Before Production Deployment:**

- [ ] UUID v4 IDs implemented correctly
- [ ] Status enum includes all states (PENDING, GENERATING, COMPLETED, FAILED, CANCELLED, TIMEOUT, PARTIAL)
- [ ] Queue semantics documented and tested (at-least-once, ordering, duplicates)
- [ ] Idempotency implemented with ≥24h window
- [ ] JSON schemas validated against canonical definitions
- [ ] Data retention policies configured
- [ ] Audit trail immutability enforced (append-only OR hash chain)
- [ ] Multi-tenant isolation tested (RLS or application-level)
- [ ] Threat model reviewed
- [ ] API rate limits configured
- [ ] Pagination uses cursors (not offsets)
- [ ] Clock skew tolerance implemented (±5 seconds)
- [ ] Compliance suite passing (all tests)
- [ ] Documentation complete
- [ ] Security audit completed

---

**Document Status:** Implementation-Ready  
**Next Review:** After 10,000 production traces analyzed  
**Feedback:** https://github.com/ovpo-project/ovpo/issues

---

**End of Specification v0.08**