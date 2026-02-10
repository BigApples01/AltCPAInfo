from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from altcpa.config import CODEBOOK_DIR


def generate_codebook(
    df: pd.DataFrame,
    column_map: pd.DataFrame,
    output_dir: Path = CODEBOOK_DIR,
    cap: int = 5,
) -> None:
    """Generate structure-only codebook artifacts (no distributions)."""
    output_dir.mkdir(parents=True, exist_ok=True)

    columns_rows: list[dict[str, object]] = []
    examples: dict[str, list[object]] = {}

    for col in df.columns:
        series = df[col]
        columns_rows.append(
            {
                "column_name": col,
                "guessed_type": str(series.dtype),
                "notes": "contains missing values" if series.isna().any() else "",
            }
        )
        samples = series.dropna().drop_duplicates().head(cap).tolist()
        examples[col] = [None if pd.isna(v) else v for v in samples]

    pd.DataFrame(columns_rows).to_csv(output_dir / "columns.csv", index=False)
    column_map.to_csv(output_dir / "column_map.csv", index=False)
    with (output_dir / "value_examples.json").open("w", encoding="utf-8") as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)
