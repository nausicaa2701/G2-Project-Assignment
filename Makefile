# Reproduce every result from the raw data, then run the web application.
#   make all    environment + data + notebook (ETL, analysis, model suite, experiments) + tests
#   make app    web application at http://localhost:8501 (runs immediately on the bundled data and results)

PYTHON ?= python3
VENV   := .venv
BIN    := $(VENV)/bin
PY     := $(BIN)/python
RAW    := data/raw
DATA_URL := https://www.kaggle.com/api/v1/datasets/download/kaggle/world-development-indicators

.PHONY: help all setup data notebook test app clean

help:
	@echo "make setup     create $(VENV) and install requirements.txt"
	@echo "make data      download Country.csv, Series.csv and Indicators.csv into $(RAW)/ (archive of about 390 MB)"
	@echo "make notebook  execute WDI_Analysis.ipynb end to end: data/processed/, figures/, results/"
	@echo "make test      automated tests"
	@echo "make app       start the web application"
	@echo "make all       setup + data + notebook + test"

all: setup data notebook test

$(PY):
	$(PYTHON) -m venv $(VENV)
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt

setup: $(PY)

$(RAW)/Indicators.csv:
	mkdir -p $(RAW)
	curl -L --fail -o data/wdi.zip "$(DATA_URL)"
	unzip -o data/wdi.zip Country.csv Series.csv Indicators.csv -d $(RAW)
	rm -f data/wdi.zip

data: $(RAW)/Indicators.csv

notebook: setup data
	$(BIN)/jupyter nbconvert --to notebook --execute --inplace \
		--ExecutePreprocessor.timeout=-1 WDI_Analysis.ipynb

test: setup
	MPLBACKEND=Agg $(PY) tests/test_models.py
	MPLBACKEND=Agg $(PY) tests/test_story.py
	MPLBACKEND=Agg $(PY) tests/test_part2.py
	$(PY) tests/test_app.py

app: setup
	$(BIN)/streamlit run app.py

clean:
	rm -rf data/processed
