# AltCPAInfo Workflow

Decision-first, reproducible survey processing workflow for the Alternative CPA Pathways survey.

## Guardrails
- Do **not** interpret survey results in this workflow.
- Outputs are structural only (schema/codebook/clean data/validation).

## Data placement
Preferred input path:

```text
data/raw/Alternative_CPA_Pathways_Survey.csv
```

If this file is missing, the workflow also checks the repository CSV filename already present.

## Setup
```bash
python -m pip install -e .[dev]
```

## Run commands
```bash
make format
make lint
make test
make codebook
make build_clean
make validate
```

Equivalent CLI commands:
```bash
python -m altcpa codebook
python -m altcpa build-clean
python -m altcpa validate
```

## Generated outputs
- `reports/codebook/columns.csv`
- `reports/codebook/column_map.csv`
- `reports/codebook/value_examples.json`
- `data/clean/clean.parquet`
- `data/interim/multiselect_long.parquet` (when multi-select patterns are detected)
