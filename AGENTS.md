# AGENTS.md

## Scope
These instructions apply to the entire repository.

## Purpose
This repository provides a decision-first survey processing workflow.

## Hard constraints
- Do **not** write narrative interpretation of survey results.
- Do **not** auto-run heavy analysis scripts.
- Keep outputs structural/tabular (schema, cleaned data, validation checks, and decision tables only).

## Definition of done
A change is done when all of the following are true:
1. Code is formatted and linted.
2. Tests pass.
3. Commands run from Makefile without code edits by user.
4. Clean build writes expected files.
5. No interpretation prose is introduced.

## Standard commands
- Install: `python -m pip install -e .[dev]`
- Lint: `make lint`
- Test: `make test`
- Codebook: `make codebook`
- Build clean data: `make build_clean`
- Validate: `make validate`

## Implementation notes
- Preserve raw row order and create `row_id`.
- Keep original-to-cleaned column mapping.
- Normalize missing values consistently.
- Avoid dropping columns unless fully empty.
