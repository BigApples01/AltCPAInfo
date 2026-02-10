PYTHON ?= python
PYTHONPATH ?= src

setup:
	$(PYTHON) -m pip install -e .[dev]

format:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m ruff format src tests

lint:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m ruff check src tests

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest

codebook:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m altcpa codebook

build_clean:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m altcpa build-clean

validate:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m altcpa validate
