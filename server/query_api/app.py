from __future__ import annotations

import time
from typing import Any, Dict, Optional

from fastapi import FastAPI


app = FastAPI(
    title="OVPO Query API (dev scaffold)",
    version="0.0.0-dev",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "service": "query-api", "ts": int(time.time())}


@app.get("/v0.08/traces/{trace_id}")
def get_trace(trace_id: str) -> Dict[str, Any]:
    """
    Placeholder response.

    In the full system this will query storage (clickhouse/postgres) and return
    the trace plus denormalized spans/events.
    """
    return {"trace_id": trace_id, "found": False, "note": "storage not wired yet"}
