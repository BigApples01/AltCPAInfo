from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from altcpa.config import RAW_CSV_FALLBACKS

SNAKE_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def resolve_raw_csv_path(path: Path) -> Path:
    if path.exists():
        return path
    for fallback in RAW_CSV_FALLBACKS:
        if fallback.exists():
            return fallback
    raise FileNotFoundError(
        f"Raw CSV not found at '{path}' and no fallback file was found: {RAW_CSV_FALLBACKS}"
    )


def read_raw_csv(path: Path) -> pd.DataFrame:
    """Read raw CSV without altering row order."""
    resolved = resolve_raw_csv_path(path)
    return pd.read_csv(resolved)


def to_snake_case(name: str) -> str:
    value = name.strip()
    value = re.sub(r"[\s/\\\-]+", "_", value)
    value = re.sub(r"[^0-9a-zA-Z_]+", "", value)
    value = re.sub(r"_+", "_", value)
    value = value.strip("_").lower()
    if not value:
        return "unnamed_column"
    if value[0].isdigit():
        value = f"col_{value}"
    return value


def standardize_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    counts: dict[str, int] = {}
    cleaned_columns: list[str] = []
    mapping_rows: list[dict[str, str]] = []

    for original in df.columns:
        base = to_snake_case(str(original))
        idx = counts.get(base, 0)
        cleaned = base if idx == 0 else f"{base}_{idx}"
        counts[base] = idx + 1
        cleaned_columns.append(cleaned)
        mapping_rows.append({"original_column": str(original), "cleaned_column": cleaned})

    out = df.copy()
    out.columns = cleaned_columns
    return out, pd.DataFrame(mapping_rows)
