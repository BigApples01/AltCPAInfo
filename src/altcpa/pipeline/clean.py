from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from altcpa.config import CODEBOOK_DIR, MISSING_TOKENS, MULTISELECT_LONG_PATH
from altcpa.pipeline.ingest import standardize_columns


def normalize_missing_value(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    if isinstance(value, str) and value.strip().lower() in MISSING_TOKENS:
        return pd.NA
    return value


def normalize_missing(df: pd.DataFrame) -> pd.DataFrame:
    return df.apply(lambda col: col.map(normalize_missing_value))


def add_row_id(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.insert(0, "row_id", range(1, len(out) + 1))
    return out


def _looks_boolean_text(series: pd.Series) -> bool:
    observed = {str(v).strip().lower() for v in series.dropna().unique()}
    return observed.issubset({"0", "1", "true", "false", "yes", "no", "y", "n"})


def _to_bool(value: object) -> bool:
    if pd.isna(value):
        return False
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y"}


def build_multiselect_long(
    cleaned_df: pd.DataFrame,
    column_map: pd.DataFrame,
    output_path: Path = MULTISELECT_LONG_PATH,
) -> pd.DataFrame:
    """Build optional long table for columns that look like Question - Option exports."""
    prefixes: dict[str, list[tuple[str, str]]] = {}
    for row in column_map.itertuples(index=False):
        original = str(row.original_column)
        clean = str(row.cleaned_column)
        if " - " in original:
            question, option = original.split(" - ", 1)
            prefixes.setdefault(question.strip(), []).append((clean, option.strip()))

    rows: list[dict[str, object]] = []
    for question, cols in prefixes.items():
        if len(cols) < 2:
            continue
        for clean_col, option in cols:
            if clean_col not in cleaned_df.columns:
                continue
            series = cleaned_df[clean_col]
            if not _looks_boolean_text(series):
                continue
            for record in cleaned_df[["row_id", clean_col]].itertuples(index=False):
                rows.append(
                    {
                        "row_id": int(record.row_id),
                        "question_id": question,
                        "option": option,
                        "selected": _to_bool(getattr(record, clean_col)),
                    }
                )

    long_df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not long_df.empty:
        long_df.to_parquet(output_path, index=False)
    return long_df


def build_codebook(df: pd.DataFrame, output_dir: Path = CODEBOOK_DIR, cap: int = 5) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    columns_rows: list[dict[str, object]] = []
    examples: dict[str, list[object]] = {}

    for col in df.columns:
        series = df[col]
        guessed_type = str(series.dtype)
        notes = "contains missing values" if series.isna().any() else ""
        columns_rows.append({"column_name": col, "guessed_type": guessed_type, "notes": notes})
        examples[col] = [
            (None if pd.isna(v) else v)
            for v in series.drop_duplicates().dropna().head(cap).tolist()
        ]

    pd.DataFrame(columns_rows).to_csv(output_dir / "columns.csv", index=False)
    with (output_dir / "value_examples.json").open("w", encoding="utf-8") as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)


def build_clean_frame(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    clean_df, column_map = standardize_columns(raw_df)
    clean_df = normalize_missing(clean_df)
    clean_df = add_row_id(clean_df)
    return clean_df, column_map
