from __future__ import annotations

from fastapi.testclient import TestClient

from server.collector.app import app


def test_health() -> None:
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "collector"


def test_ready() -> None:
    client = TestClient(app)
    resp = client.get("/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_metrics() -> None:
    client = TestClient(app)
    resp = client.get("/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "not_implemented"


def test_ingest_batch_valid() -> None:
    client = TestClient(app)
    # A minimal valid payload, assuming it will be updated as schemas evolve
    payload = {
        "schema_version": "0.08",
        "batch_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        "sent_at": "2024-01-01T00:00:00Z",
        "items": [
            {
                "type": "trace",
                "schema_version": "0.08",
                "trace_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12",
                "tenant_id": "my-tenant",
                "status": "COMPLETED",
                "pipeline_config": {"model": "test-model"},
                "input_context": {"prompt_hash": "a" * 64},
                "created_at": "2024-01-01T00:00:00Z",
            }
        ],
    }
    resp = client.post("/v1/ingest/batch", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "accepted"


def test_ingest_batch_invalid() -> None:
    client = TestClient(app)
    payload = {"batch_id": "invalid"}  # Missing required fields
    resp = client.post("/v1/ingest/batch", json=payload)
    assert resp.status_code == 422
