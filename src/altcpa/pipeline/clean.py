from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from altcpa.config import MISSING_TOKENS, MULTISELECT_LONG_PATH
from altcpa.pipeline.ingest import standardize_columns


def normalize_missing_value(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    if isinstance(value, str) and value.strip().lower() in MISSING_TOKENS:
        return pd.NA
    return value


def normalize_missing(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        out[col] = out[col].map(normalize_missing_value)
    return out


def add_row_id(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "row_id" in out.columns:
        out = out.drop(columns=["row_id"])
    out.insert(0, "row_id", range(1, len(out) + 1))
    return out


def build_clean_frame(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    clean_df, column_map = standardize_columns(raw_df)
    clean_df = normalize_missing(clean_df)

    empty_cols = [c for c in clean_df.columns if clean_df[c].isna().all()]
    non_empty_cols = [c for c in clean_df.columns if c not in empty_cols]
    clean_df = clean_df[non_empty_cols + empty_cols]

    clean_df = add_row_id(clean_df)
    return clean_df, column_map


def _looks_boolean_like(series: pd.Series) -> bool:
    observed = {str(v).strip().lower() for v in series.dropna().unique()}
    return bool(observed) and observed.issubset(
        {"0", "1", "true", "false", "yes", "no", "y", "n", "selected", "checked"}
    )


def _to_bool(value: object) -> bool:
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "selected", "checked"}


def _detect_question_option_pairs(column_map: pd.DataFrame) -> dict[str, list[tuple[str, str]]]:
    pairs: dict[str, list[tuple[str, str]]] = {}

    for row in column_map.itertuples(index=False):
        original = str(row.original_column)
        cleaned = str(row.cleaned_column)

        if " - " in original:
            question, option = original.split(" - ", 1)
            pairs.setdefault(question.strip(), []).append((cleaned, option.strip()))
            continue

        match = re.match(r"^(.*?)[_\-](?:option|choice|select)[_\-]?(.*)$", cleaned)
        if match:
            q = match.group(1).strip("_-")
            opt = match.group(2).strip("_-") or cleaned
            pairs.setdefault(q, []).append((cleaned, opt))

    return {q: cols for q, cols in pairs.items() if len(cols) >= 2}


def build_multiselect_long(
    cleaned_df: pd.DataFrame,
    column_map: pd.DataFrame,
    output_path: Path = MULTISELECT_LONG_PATH,
) -> pd.DataFrame:
    question_pairs = _detect_question_option_pairs(column_map)

    rows: list[dict[str, object]] = []
    for question_id, pairs in question_pairs.items():
        for cleaned_col, option in pairs:
            if cleaned_col not in cleaned_df.columns:
                continue
            series = cleaned_df[cleaned_col]
            if not _looks_boolean_like(series):
                continue

            subset = cleaned_df[["row_id", cleaned_col]]
            for row in subset.itertuples(index=False):
                rows.append(
                    {
                        "row_id": int(row.row_id),
                        "question_id": question_id,
                        "option": option,
                        "selected": _to_bool(getattr(row, cleaned_col)),
                    }
                )

    long_df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not long_df.empty:
        long_df.to_parquet(output_path, index=False)
    elif output_path.exists():
        output_path.unlink()
    return long_df
