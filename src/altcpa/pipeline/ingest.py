from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


def read_raw_csv(path: Path) -> pd.DataFrame:
    """Read raw CSV without altering order."""
    return pd.read_csv(path)


def to_snake_case(name: str) -> str:
    value = name.strip()
    value = re.sub(r"[\s/\\\-]+", "_", value)
    value = re.sub(r"[^0-9a-zA-Z_]+", "", value)
    value = re.sub(r"_+", "_", value)
    value = value.strip("_").lower()
    return value or "unnamed_column"


def standardize_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return dataframe with stable snake_case names and column map."""
    counts: dict[str, int] = {}
    clean_cols: list[str] = []
    mapping_rows: list[dict[str, str]] = []

    for original in df.columns:
        base = to_snake_case(str(original))
        idx = counts.get(base, 0)
        clean = base if idx == 0 else f"{base}_{idx}"
        counts[base] = idx + 1
        clean_cols.append(clean)
        mapping_rows.append({"original_column": str(original), "cleaned_column": clean})

    out = df.copy()
    out.columns = clean_cols
    map_df = pd.DataFrame(mapping_rows)
    return out, map_df
