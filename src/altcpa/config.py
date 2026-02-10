from pathlib import Path

RAW_CSV_PATH = Path("data/raw/Alternative_CPA_Pathways_Survey.csv")
CLEAN_PARQUET_PATH = Path("data/clean/clean.parquet")
MULTISELECT_LONG_PATH = Path("data/interim/multiselect_long.parquet")
CODEBOOK_DIR = Path("reports/codebook")
DECISION_PACKET_DIR = Path("reports/decision_packet")

MISSING_TOKENS = {
    "",
    "na",
    "n/a",
    "null",
    "none",
    "prefer not to say",
}

SEGMENT_CANDIDATES = [
    "role",
    "employer_type",
    "license_status",
    "geography",
    "state",
    "industry",
]

KEY_QUESTION_CANDIDATES = [
    "support",
    "concern",
    "macc",
    "mobility",
    "pathway",
    "preference",
]
