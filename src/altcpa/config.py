from pathlib import Path

RAW_CSV_PATH = Path("data/raw/Alternative_CPA_Pathways_Survey.csv")
RAW_CSV_FALLBACKS = [
    Path("Alternative CPA Pathways Survey_December 31, 2025_09.45.csv"),
]

CLEAN_PARQUET_PATH = Path("data/clean/clean.parquet")
MULTISELECT_LONG_PATH = Path("data/interim/multiselect_long.parquet")
CODEBOOK_DIR = Path("reports/codebook")

MISSING_TOKENS = {
    "",
    "na",
    "n/a",
    "null",
    "none",
    "prefer not to say",
}
