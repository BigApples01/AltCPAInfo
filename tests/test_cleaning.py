from pathlib import Path

import pandas as pd

from altcpa.codebook import generate_codebook
from altcpa.pipeline.clean import add_row_id, build_clean_frame, normalize_missing
from altcpa.pipeline.ingest import standardize_columns, to_snake_case


def test_snake_case_stability() -> None:
    assert to_snake_case("Question 1 / Pathway - A") == "question_1_pathway_a"
    assert to_snake_case("123 Value") == "col_123_value"


def test_normalize_missing_tokens() -> None:
    df = pd.DataFrame({"a": ["", "NA", "N/A", "null", "None", "Prefer not to say", "ok"]})
    result = normalize_missing(df)
    assert result["a"].isna().sum() == 6
    assert result["a"].iloc[6] == "ok"


def test_row_id_uniqueness() -> None:
    df = pd.DataFrame({"x": [1, 2, 3]})
    out = add_row_id(df)
    assert out["row_id"].is_unique
    assert out["row_id"].tolist() == [1, 2, 3]


def test_output_files_created(tmp_path: Path) -> None:
    raw = pd.DataFrame(
        [["yes", "no", "value"]],
        columns=["Q1 - Option A", "Q1 - Option B", "Open Text"],
    )
    clean_df, column_map = build_clean_frame(raw)

    clean_path = tmp_path / "clean.parquet"
    clean_df.to_parquet(clean_path, index=False)
    assert clean_path.exists()

    codebook_dir = tmp_path / "codebook"
    generate_codebook(clean_df, column_map, output_dir=codebook_dir)

    assert (codebook_dir / "columns.csv").exists()
    assert (codebook_dir / "column_map.csv").exists()
    assert (codebook_dir / "value_examples.json").exists()


def test_standardize_columns_resolves_collisions() -> None:
    df = pd.DataFrame([[1, 2]], columns=["A A", "A-A"])
    _, column_map = standardize_columns(df)
    assert column_map["cleaned_column"].tolist() == ["a_a", "a_a_1"]
