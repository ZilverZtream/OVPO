from __future__ import annotations

from pathlib import Path

import pytest
from jsonschema import ValidationError

from ovpo.schemas import validate_file


def test_valid_ingest_batch_example() -> None:
    p = Path("schemas/v0.08/examples/valid/ingest_batch_minimal.json")
    validate_file(p, "ingest_batch.json")


def test_invalid_ingest_batch_example_fails() -> None:
    p = Path("schemas/v0.08/examples/invalid/ingest_batch_missing_batch_id.json")
    with pytest.raises(ValidationError):
        validate_file(p, "ingest_batch.json")
