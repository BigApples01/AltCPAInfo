from __future__ import annotations

import re

import pandas as pd
import pandera as pa

from altcpa.config import MISSING_TOKENS
from altcpa.pipeline.ingest import SNAKE_CASE_PATTERN

LIKERT_TEXT_VALUES = {
    "strongly disagree",
    "disagree",
    "neutral",
    "agree",
    "strongly agree",
}


def detect_likert_columns(df: pd.DataFrame) -> list[str]:
    candidates: list[str] = []
    for col in df.columns:
        if col == "row_id":
            continue
        non_null = df[col].dropna()
        if non_null.empty:
            continue

        text_values = {str(v).strip().lower() for v in non_null.unique()}
        if text_values.issubset(LIKERT_TEXT_VALUES):
            candidates.append(col)
            continue

        nums = pd.to_numeric(non_null, errors="coerce")
        if nums.notna().all() and nums.between(1, 5).all() and re.search(
            r"(likert|agreement|support|concern|importance|satisfaction)", col
        ):
            candidates.append(col)
    return candidates


def validate_clean(df: pd.DataFrame) -> None:
    schema = pa.DataFrameSchema(
        {
            "row_id": pa.Column(int, checks=[pa.Check.ge(1)], unique=True, nullable=False),
        },
        strict=False,
        coerce=True,
    )
    schema.validate(df)

    if list(df.columns)[0] != "row_id":
        raise ValueError("'row_id' must be the first column.")

    dupes = df.columns[df.columns.duplicated()].tolist()
    if dupes:
        raise ValueError(f"Duplicate cleaned columns detected: {dupes}")

    invalid = [c for c in df.columns if not SNAKE_CASE_PATTERN.match(c)]
    if invalid:
        raise ValueError(f"Non-snake_case cleaned columns detected: {invalid}")

    bad_missing_tokens: dict[str, list[str]] = {}
    for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
            observed = {str(v).strip().lower() for v in df[col].dropna().unique()}
            overlap = sorted(observed.intersection(MISSING_TOKENS))
            if overlap:
                bad_missing_tokens[col] = overlap
    if bad_missing_tokens:
        raise ValueError(f"Missing tokens were not normalized in columns: {bad_missing_tokens}")

    for col in detect_likert_columns(df):
        non_null = df[col].dropna()
        nums = pd.to_numeric(non_null, errors="coerce")
        if nums.notna().all():
            if not nums.between(1, 5).all():
                raise ValueError(f"Likert numeric out of range [1,5] in '{col}'.")
        else:
            text_values = {str(v).strip().lower() for v in non_null.unique()}
            if not text_values.issubset(LIKERT_TEXT_VALUES):
                raise ValueError(f"Likert text values unexpected in '{col}'.")
