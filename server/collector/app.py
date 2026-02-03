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
    Dev scaffolding endpoint.

    Validates payload against schemas/v0.08/ingest_batch.json and returns a
    minimal acknowledgement. Queue/storage integration is added later.
    """
    payload = await request.json()
    try:
        validate_json(payload, "ingest_batch.json")
    except Exception as e:  # noqa: BLE001 - want structured API error here
        raise HTTPException(status_code=422, detail=str(e)) from e

    return JSONResponse(
        {
            "status": "accepted",
            "schema": "v0.08",
            "received_bytes": request.headers.get("content-length"),
        }
    )
