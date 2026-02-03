from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Optional

import typer

from ovpo.schemas import SCHEMA_VERSION, load_schema, validate_file


app = typer.Typer(add_completion=False, no_args_is_help=True)


def _iter_json_files(path: Path) -> Iterable[Path]:
    if path.is_file():
        yield path
        return

    for p in sorted(path.rglob("*.json")):
        if p.is_file():
            yield p


@app.command()
def version() -> None:
    """Print the OVPO version and schema version."""
    from ovpo import __version__

    typer.echo(f"ovpo {__version__} (schemas {SCHEMA_VERSION})")


@app.command("validate-json")
def validate_json_cmd(
    json_file: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    schema: str = typer.Option(
        ...,
        "--schema",
        help="Schema filename under schemas/v0.08 (e.g. ingest_batch.json).",
    ),
) -> None:
    """Validate a JSON file against a schema."""
    validate_file(json_file, schema)
    typer.echo("OK")


@app.command("validate-folder")
def validate_folder_cmd(
    folder: Path = typer.Argument(..., exists=True, file_okay=False, readable=True),
    schema: str = typer.Option(
        ...,
        "--schema",
        help="Schema filename under schemas/v0.08 (e.g. ingest_batch.json).",
    ),
    fail_fast: bool = typer.Option(False, "--fail-fast", help="Stop at first failure."),
) -> None:
    """Validate all *.json files in a folder recursively."""
    failures: List[str] = []
    for p in _iter_json_files(folder):
        try:
            validate_file(p, schema)
        except Exception as e:  # noqa: BLE001 - CLI wants a clean message
            failures.append(f"{p}: {e}")
            if fail_fast:
                break

    if failures:
        for line in failures:
            typer.echo(line)
        raise typer.Exit(code=1)

    typer.echo("OK")


@app.command("print-schema")
def print_schema(
    schema: str = typer.Argument(..., help="Schema filename under schemas/v0.08"),
) -> None:
    """Print a schema to stdout."""
    typer.echo(json.dumps(load_schema(schema), indent=2, sort_keys=True))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
