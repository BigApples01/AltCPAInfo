from __future__ import annotations

import re

import pandas as pd
import pandera as pa
from pandera.errors import SchemaError

LIKERT_TEXT_VALUES = {
    "strongly disagree",
    "disagree",
    "neutral",
    "agree",
    "strongly agree",
}


def detect_likert_columns(df: pd.DataFrame) -> list[str]:
    likert_cols: list[str] = []
    for col in df.columns:
        if col == "row_id":
            continue
        non_null = df[col].dropna()
        if non_null.empty:
            continue

        text_values = {str(v).strip().lower() for v in non_null.unique()}
        if text_values and text_values.issubset(LIKERT_TEXT_VALUES):
            likert_cols.append(col)
            continue

        numeric = pd.to_numeric(non_null, errors="coerce")
        if numeric.notna().all() and numeric.between(1, 5).all() and len(numeric.unique()) >= 3:
            if re.search(r"(likert|agreement|support|concern|importance|satisfaction)", col):
                likert_cols.append(col)
    return likert_cols


def validate_clean(df: pd.DataFrame) -> None:
    base_schema = pa.DataFrameSchema(
        {
            "row_id": pa.Column(int, checks=pa.Check.greater_than_or_equal_to(1), unique=True),
        },
        strict=False,
        coerce=True,
    )
    base_schema.validate(df)

    if df.columns.duplicated().any():
        raise SchemaError(base_schema, df, "Duplicate columns detected after cleaning")

    likert_cols = detect_likert_columns(df)
    for col in likert_cols:
        non_null = df[col].dropna()
        numeric = pd.to_numeric(non_null, errors="coerce")
        if numeric.notna().all():
            if not numeric.between(1, 5).all():
                raise ValueError(f"Likert numeric out of expected range in column '{col}'.")
        else:
            text_values = {str(v).strip().lower() for v in non_null.unique()}
            if not text_values.issubset(LIKERT_TEXT_VALUES):
                raise ValueError(f"Likert text values unexpected in column '{col}'.")
