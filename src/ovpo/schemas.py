from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Mapping

import jsonschema


SCHEMA_VERSION = "v0.08"


def _repo_root() -> Path:
    # src/ovpo/schemas.py -> repo root is two parents up from src/
    return Path(__file__).resolve().parents[2]


def schemas_dir() -> Path:
    return _repo_root() / "schemas" / SCHEMA_VERSION


def schema_path(name: str) -> Path:
    p = schemas_dir() / name
    if not p.exists():
        raise FileNotFoundError(f"Schema not found: {p}")
    return p


@lru_cache(maxsize=1)
def _schema_store() -> Mapping[str, Dict[str, Any]]:
    """
    Preload all schemas in schemas/v0.08 into a store for $ref resolution.

    jsonschema will fetch referenced schemas by their `$id` or by URL-like
    paths. We provide both keys:
      - `$id` values
      - file://... URIs for local paths
      - bare filenames (best effort for relative refs)
    """
    store: Dict[str, Dict[str, Any]] = {}
    for p in schemas_dir().glob("*.json"):
        doc = json.loads(p.read_text(encoding="utf-8"))
        doc_id = doc.get("$id")
        if isinstance(doc_id, str) and doc_id:
            store[doc_id] = doc
        store[p.as_uri()] = doc
        store[p.name] = doc
    return store


def load_schema(name: str) -> Dict[str, Any]:
    return json.loads(schema_path(name).read_text(encoding="utf-8"))


def validate_json(instance: Any, schema_name: str) -> None:
    schema_file = schema_path(schema_name)
    schema = json.loads(schema_file.read_text(encoding="utf-8"))

    resolver = jsonschema.RefResolver(
        base_uri=schema_file.as_uri(),
        referrer=schema,
        store=dict(_schema_store()),
    )

    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls.check_schema(schema)
    validator = validator_cls(schema, resolver=resolver)
    validator.validate(instance)


def validate_file(json_path: Path, schema_name: str) -> None:
    instance = json.loads(json_path.read_text(encoding="utf-8"))
    validate_json(instance, schema_name)
