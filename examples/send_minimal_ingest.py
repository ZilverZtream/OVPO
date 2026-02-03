from __future__ import annotations

import json
from pathlib import Path

import httpx


def main() -> None:
    payload = json.loads(
        Path("schemas/v0.08/examples/valid/ingest_batch_minimal.json").read_text(encoding="utf-8")
    )

    url = "http://localhost:8080/v0.08/ingest"
    with httpx.Client(timeout=10.0) as client:
        resp = client.post(url, json=payload)
        print(resp.status_code)
        print(resp.text)


if __name__ == "__main__":
    main()
