from __future__ import annotations

import time
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from ovpo.schemas import validate_json

app = FastAPI(
    title="OVPO Collector (dev scaffold)",
    version="0.0.0-dev",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "collector", "ts": int(time.time())}


@app.get("/ready")
def ready() -> dict[str, Any]:
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> dict[str, Any]:
    return {"status": "not_implemented"}


@app.post("/v1/ingest/batch")
async def ingest_batch(request: Request) -> JSONResponse:
    """
    Ingests a batch of observability data, validates it, and queues it for processing.
    - Enforces 5MB payload limit
    - Validates headers
    - Validates payload against schemas/v0.08/ingest_batch.json
    - Returns acknowledgement
    """
    # Header validation (strict)
    auth_header = request.headers.get("Authorization")
    idempotency_key = request.headers.get("Idempotency-Key")
    schema_version_header = request.headers.get("X-OVPO-Schema-Version")

    if not all([auth_header, idempotency_key, schema_version_header]):
        raise HTTPException(
            status_code=400,
            detail="Missing one or more required headers: Authorization, Idempotency-Key, X-OVPO-Schema-Version",
        )

    if not auth_header.startswith("Bearer ovpo_sk_"):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key format. Key must start with 'ovpo_sk_'.",
        )

    if schema_version_header != "0.08":
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported schema version '{schema_version_header}'. Server supports '0.08'.",
        )

    # Payload size enforcement
    content_length = request.headers.get("content-length")
    if not content_length:
        raise HTTPException(status_code=411, detail="Content-Length required")

    MAX_PAYLOAD_BYTES = 5 * 1024 * 1024  # 5MB
    if int(content_length) > MAX_PAYLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Payload exceeds 5MB limit. Received: {content_length} bytes.",
        )

    # JSON validation
    payload = await request.json()
    try:
        validate_json(payload, "ingest_batch.json")
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    # TODO: Queueing logic
    # TODO: Idempotency check with Redis

    return JSONResponse(
        {
            "status": "accepted",
            "batch_id": payload.get("batch_id"),
            "processed_items": len(payload.get("items", [])),
            "duplicate_items": 0,  # Placeholder
            "failed_items": 0,  # Placeholder
            "errors": [],  # Placeholder
        },
        status_code=202,  # Use 202 Accepted for async processing
    )
