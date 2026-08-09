PYTHON ?= python
R ?= Rscript

.PHONY: setup-python test synthetic pipeline validate-data archive-pilot-sources validate-source-manifest prepare-ai-validation r-analysis paper clean

setup-python:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install -r requirements.lock && pip install -e .

test:
	PYTHONPATH=src $(PYTHON) -m pytest

synthetic:
	PYTHONPATH=src $(PYTHON) scripts/build_synthetic.py

pipeline:
	PYTHONPATH=src $(PYTHON) scripts/run_python_pipeline.py --input data/synthetic/wbes_fixture.csv --output data/processed/wbes_fixture_processed.csv

validate-data:
	PYTHONPATH=src $(PYTHON) scripts/validate_data.py

archive-pilot-sources:
	PYTHONPATH=src $(PYTHON) scripts/archive_pilot_sources.py --scope all --apply

validate-source-manifest:
	PYTHONPATH=src $(PYTHON) scripts/validate_source_manifest.py --verify-files

prepare-ai-validation:
	PYTHONPATH=src $(PYTHON) scripts/build_ai_validation_input.py
	PYTHONPATH=src $(PYTHON) scripts/draw_blinded_validation_sample.py

r-analysis:
	$(R) analysis/01_descriptives.R
	$(R) analysis/02_exposure_event_study.R
	$(R) analysis/03_adoption_event_study.R
	$(R) analysis/04_wbes_change_models.R
	$(R) analysis/05_robustness.R

paper:
	cd paper && latexmk -pdf -interaction=nonstopmode main.tex

clean:
	rm -rf data/interim/* data/processed/* outputs/*
