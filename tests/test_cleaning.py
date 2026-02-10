import pandas as pd

from altcpa.pipeline.clean import add_row_id, build_clean_frame, normalize_missing
from altcpa.pipeline.ingest import standardize_columns, to_snake_case


def test_snake_case_stability() -> None:
    assert to_snake_case("Question 1 / Pathway - A") == "question_1_pathway_a"


def test_normalize_missing_tokens() -> None:
    df = pd.DataFrame({"a": ["", "NA", "Prefer not to say", "ok"]})
    result = normalize_missing(df)
    assert result["a"].isna().sum() == 3
    assert result["a"].iloc[3] == "ok"


def test_row_id_uniqueness() -> None:
    df = pd.DataFrame({"x": [1, 2, 3]})
    out = add_row_id(df)
    assert out["row_id"].is_unique
    assert out["row_id"].tolist() == [1, 2, 3]


def test_column_map_output_exists(tmp_path) -> None:
    raw = pd.DataFrame([[1, 2, 3]], columns=["Column A", "Column A", "Another Column"])
    clean_df, column_map = build_clean_frame(raw)
    out_path = tmp_path / "column_map.csv"
    column_map.to_csv(out_path, index=False)

    assert "row_id" in clean_df.columns
    assert out_path.exists()
    map_df = pd.read_csv(out_path)
    assert {"original_column", "cleaned_column"}.issubset(map_df.columns)


def test_standardize_columns_resolves_collisions() -> None:
    df = pd.DataFrame([[1, 2]], columns=["A A", "A-A"])
    _, column_map = standardize_columns(df)
    assert column_map["cleaned_column"].tolist() == ["a_a", "a_a_1"]
