from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from altcpa.config import DECISION_PACKET_DIR, KEY_QUESTION_CANDIDATES, SEGMENT_CANDIDATES


def _candidate_columns(df: pd.DataFrame, keywords: list[str]) -> list[str]:
    return [c for c in df.columns if any(k in c for k in keywords)]


def _first_available(df: pd.DataFrame, keywords: list[str]) -> str | None:
    cols = _candidate_columns(df, keywords)
    return cols[0] if cols else None


def generate_decision_packet(
    clean_df: pd.DataFrame,
    output_dir: Path = DECISION_PACKET_DIR,
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: dict[str, str] = {}

    segment_cols = _candidate_columns(clean_df, SEGMENT_CANDIDATES)
    key_cols = _candidate_columns(clean_df, KEY_QUESTION_CANDIDATES)

    for seg in segment_cols[:3]:
        for key in key_cols[:3]:
            table = pd.crosstab(clean_df[seg], clean_df[key], dropna=False)
            path = output_dir / f"crosstab__{seg}__{key}.csv"
            table.to_csv(path)
            generated[f"crosstab:{seg}:{key}"] = str(path)

    concern_col = _first_available(clean_df, ["concern", "risk", "barrier"])
    if concern_col and segment_cols:
        summary_rows: list[pd.DataFrame] = []
        for seg in segment_cols[:3]:
            top = (
                clean_df.groupby(seg, dropna=False)[concern_col]
                .value_counts(dropna=False)
                .groupby(level=0)
                .head(5)
                .rename("count")
                .reset_index()
            )
            top.insert(0, "segment_column", seg)
            summary_rows.append(top)
        if summary_rows:
            out = pd.concat(summary_rows, ignore_index=True)
            path = output_dir / "top_concerns_by_segment.csv"
            out.to_csv(path, index=False)
            generated["top_concerns"] = str(path)

    target_col = _first_available(clean_df, ["macc", "support", "preference", "pathway"])
    feature_cols = [c for c in segment_cols[:3] if c != target_col]
    model_summary = {
        "target_column": target_col,
        "feature_columns": feature_cols,
        "model_type": "placeholder_logistic_or_ordinal",
        "status": "not_run",
    }
    model_path = output_dir / "driver_model_summary.json"
    with model_path.open("w", encoding="utf-8") as f:
        json.dump(model_summary, f, indent=2)
    generated["driver_model_summary"] = str(model_path)

    text_col = _first_available(clean_df, ["other", "comment", "open", "text", "feedback"])
    if text_col:
        review = clean_df[["row_id", text_col]].copy()
        review = review.rename(columns={text_col: "text_response"})
        review["theme_label"] = pd.NA
        review["review_notes"] = pd.NA
        path = output_dir / "text_theme_review_sheet.csv"
        review.to_csv(path, index=False)
        generated["text_theme_review_sheet"] = str(path)

    manifest = output_dir / "manifest.json"
    with manifest.open("w", encoding="utf-8") as f:
        json.dump(generated, f, indent=2)

    return generated
