.PHONY: setup pipeline model report test dashboard all

PYTHON := .venv/bin/python

setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

pipeline:
	$(PYTHON) -m src.data_pipeline

model:
	$(PYTHON) -m src.train_model

report:
	$(PYTHON) -m src.generate_report

test:
	$(PYTHON) -m pytest -q

dashboard:
	.venv/bin/streamlit run dashboard/app.py

all: pipeline model report test

