from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from altcpa.codebook import generate_codebook
from altcpa.config import CLEAN_PARQUET_PATH, CODEBOOK_DIR, RAW_CSV_PATH
from altcpa.pipeline.clean import build_clean_frame, build_multiselect_long
from altcpa.pipeline.ingest import read_raw_csv
from altcpa.pipeline.validate import validate_clean

app = typer.Typer(help="AltCPA decision-first survey workflow CLI")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


@app.command("codebook")
def codebook(raw_csv: Path = RAW_CSV_PATH, output_dir: Path = CODEBOOK_DIR) -> None:
    """Generate structure-only codebook artifacts."""
    raw_df = read_raw_csv(raw_csv)
    clean_df, column_map = build_clean_frame(raw_df)
    generate_codebook(clean_df, column_map, output_dir=output_dir)
    typer.echo(f"Wrote codebook artifacts to {output_dir}")


@app.command("build-clean")
def build_clean(raw_csv: Path = RAW_CSV_PATH, output_path: Path = CLEAN_PARQUET_PATH) -> None:
    """Build cleaned dataset and supporting mapping artifacts."""
    raw_df = read_raw_csv(raw_csv)
    clean_df, column_map = build_clean_frame(raw_df)

    _ensure_parent(output_path)
    clean_df.to_parquet(output_path, index=False)

    generate_codebook(clean_df, column_map, output_dir=CODEBOOK_DIR)
    build_multiselect_long(clean_df, column_map)
    typer.echo(f"Wrote clean data to {output_path}")


@app.command("validate")
def validate(clean_path: Path = CLEAN_PARQUET_PATH) -> None:
    """Validate cleaned data schema and rule checks."""
    df = pd.read_parquet(clean_path)
    validate_clean(df)
    typer.echo("Validation passed")
