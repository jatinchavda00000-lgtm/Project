# ============================================
# Retail Sales Data Analysis
# File: Makefile
# Purpose: Convenience commands for common tasks
# ============================================
#
# Usage:
#   make help          Show all available targets
#   make install       Install dependencies
#   make run           Run full pipeline
#   make test          Run all tests
#   make clean         Remove generated files
#
# Note: This project does not use any API.
# ============================================

# --------------------------------------------
# Configuration
# --------------------------------------------

PYTHON          := python
PYTEST          := pytest
PIP             := pip

SRC_DIR         := src
TEST_DIR        := tests
SCRIPTS_DIR     := scripts
NOTEBOOKS_DIR   := notebooks
SQL_DIR         := sql
DATA_DIR        := data
OUTPUT_DIR      := output
IMAGES_DIR      := images
REPORTS_DIR     := reports
DASHBOARD_DIR   := dashboard

VENV_DIR        := venv

# OS detection (for venv activation path)
ifeq ($(OS), Windows_NT)
    VENV_PYTHON := $(VENV_DIR)/Scripts/python.exe
    VENV_PIP    := $(VENV_DIR)/Scripts/pip.exe
    RM_RF       := rmdir /S /Q
    RM_FILE     := del /Q
else
    VENV_PYTHON := $(VENV_DIR)/bin/python
    VENV_PIP    := $(VENV_DIR)/bin/pip
    RM_RF       := rm -rf
    RM_FILE     := rm -f
endif

# ============================================
# PHONY TARGETS
# ============================================

.PHONY: help \
        install install-dev install-conda \
        venv activate-info \
        setup \
        run run-fast run-synthetic \
        load clean-data features analyze visualize \
        notebooks notebooks-01 notebooks-02 notebooks-03 notebooks-04 notebooks-05 \
        sql sql-create sql-import sql-basic sql-agg sql-window sql-insights \
        test test-cleaning test-analysis test-utils test-cov \
        lint format \
        clean clean-output clean-images clean-reports clean-db clean-all \
        tree check-python check-deps \
        all

# ============================================
# DEFAULT TARGET
# ============================================

.DEFAULT_GOAL := help

# ============================================
# HELP
# ============================================

help:
	@echo "============================================================"
	@echo "  Retail Sales Data Analysis - Available Commands"
	@echo "============================================================"
	@echo ""
	@echo "  SETUP"
	@echo "    make install             Install Python dependencies"
	@echo "    make install-dev         Install dev + test dependencies"
	@echo "    make install-conda       Create Conda environment"
	@echo "    make venv                Create virtual environment"
	@echo "    make setup               Full setup (venv + install)"
	@echo ""
	@echo "  RUN"
	@echo "    make run                 Run full pipeline (all steps)"
	@echo "    make run-fast            Run pipeline without plots/SQL"
	@echo "    make run-synthetic       Run pipeline with synthetic data"
	@echo ""
	@echo "  PIPELINE STEPS"
	@echo "    make load                Load raw data"
	@echo "    make clean-data          Clean dataset"
	@echo "    make features            Engineer features"
	@echo "    make analyze             Run analysis"
	@echo "    make visualize           Generate 18 plots"
	@echo ""
	@echo "  NOTEBOOKS"
	@echo "    make notebooks           Generate all 5 notebooks"
	@echo "    make notebooks-01        Generate notebook 01"
	@echo "    make notebooks-02        Generate notebook 02"
	@echo "    make notebooks-03        Generate notebook 03"
	@echo "    make notebooks-04        Generate notebook 04"
	@echo "    make notebooks-05        Generate notebook 05"
	@echo ""
	@echo "  SQL"
	@echo "    make sql                 Run all SQL scripts (SQLite)"
	@echo "    make sql-create          Create tables"
	@echo "    make sql-basic           Run basic queries"
	@echo "    make sql-agg             Run aggregation queries"
	@echo "    make sql-window          Run window-function queries"
	@echo "    make sql-insights        Run final insight queries"
	@echo ""
	@echo "  TESTING"
	@echo "    make test                Run all tests"
	@echo "    make test-cleaning       Test data_cleaning module"
	@echo "    make test-analysis       Test analysis module"
	@echo "    make test-utils          Test utils module"
	@echo "    make test-cov            Run tests with coverage report"
	@echo ""
	@echo "  MAINTENANCE"
	@echo "    make clean               Clean generated outputs"
	@echo "    make clean-all           Clean everything (incl. venv)"
	@echo "    make tree                Show project tree"
	@echo "    make check-python        Verify Python version"
	@echo "    make check-deps          Verify dependencies installed"
	@echo ""
	@echo "  ALL"
	@echo "    make all                 Setup + run + test"
	@echo ""
	@echo "============================================================"

# ============================================
# SETUP
# ============================================

install:
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-cov

install-conda:
	conda env create -f environment.yml
	@echo "Activate with: conda activate retail-sales"

venv:
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created at: $(VENV_DIR)"
	@echo "Activate with:"
	@echo "  Windows : $(VENV_DIR)\\Scripts\\activate"
	@echo "  Linux   : source $(VENV_DIR)/bin/activate"

activate-info:
	@echo "To activate the virtual environment:"
	@echo "  Windows : $(VENV_DIR)\\Scripts\\activate"
	@echo "  Linux   : source $(VENV_DIR)/bin/activate"

setup: venv
	$(VENV_PIP) install -r requirements.txt
	@echo "Setup complete."

# ============================================
# RUN FULL PIPELINE
# ============================================

run:
	@echo "Running full pipeline..."
	$(PYTHON) $(SCRIPTS_DIR)/run_pipeline.py

run-fast:
	@echo "Running pipeline (skip plots + SQL)..."
	$(PYTHON) $(SCRIPTS_DIR)/run_pipeline.py --skip-plots --skip-sql

run-synthetic:
	@echo "Running pipeline with synthetic data..."
	$(PYTHON) $(SCRIPTS_DIR)/run_pipeline.py --synthetic

# ============================================
# INDIVIDUAL PIPELINE STEPS
# ============================================

load:
	@echo "Loading raw data..."
	$(PYTHON) $(SRC_DIR)/data_loader.py

clean-data:
	@echo "Cleaning data..."
	$(PYTHON) $(SRC_DIR)/data_cleaning.py

features:
	@echo "Engineering features..."
	$(PYTHON) $(SRC_DIR)/feature_engineering.py

analyze:
	@echo "Running analysis..."
	$(PYTHON) $(SRC_DIR)/analysis.py

visualize:
	@echo "Generating plots..."
	$(PYTHON) $(SRC_DIR)/visualization.py

setup-config:
	@echo "Setting up directories..."
	$(PYTHON) $(SRC_DIR)/config.py

# ============================================
# NOTEBOOK GENERATION
# ============================================

notebooks: notebooks-01 notebooks-02 notebooks-03 notebooks-04 notebooks-05
	@echo "All notebooks generated."

notebooks-01:
	$(PYTHON) $(SCRIPTS_DIR)/make_notebook_01.py

notebooks-02:
	$(PYTHON) $(SCRIPTS_DIR)/make_notebook_02.py

notebooks-03:
	$(PYTHON) $(SCRIPTS_DIR)/make_notebook_03.py

notebooks-04:
	$(PYTHON) $(SCRIPTS_DIR)/make_notebook_04.py

notebooks-05:
	$(PYTHON) $(SCRIPTS_DIR)/make_notebook_05.py

# ============================================
# SQL (SQLite by default)
# ============================================

sql: sql-create sql-basic sql-agg sql-window sql-insights
	@echo "All SQL scripts executed."

sql-create:
	@echo "Creating tables..."
	sqlite3 retail_sales.db < $(SQL_DIR)/01_create_table.sql

sql-import:
	@echo "Importing data..."
	sqlite3 retail_sales.db < $(SQL_DIR)/02_import_data.sql

sql-basic:
	@echo "Running basic queries..."
	sqlite3 retail_sales.db < $(SQL_DIR)/03_basic_queries.sql

sql-agg:
	@echo "Running aggregation queries..."
	sqlite3 retail_sales.db < $(SQL_DIR)/04_aggregation_queries.sql

sql-window:
	@echo "Running window-function queries..."
	sqlite3 retail_sales.db < $(SQL_DIR)/05_window_functions.sql

sql-insights:
	@echo "Running final insight queries..."
	sqlite3 retail_sales.db < $(SQL_DIR)/06_final_insights.sql

# ============================================
# TESTING
# ============================================

test:
	$(PYTEST) $(TEST_DIR)/ -v

test-cleaning:
	$(PYTEST) $(TEST_DIR)/test_data_cleaning.py -v

test-analysis:
	$(PYTEST) $(TEST_DIR)/test_analysis.py -v

test-utils:
	$(PYTEST) $(TEST_DIR)/test_utils.py -v

test-cov:
	$(PYTEST) $(TEST_DIR)/ -v --cov=$(SRC_DIR) --cov-report=html --cov-report=term
	@echo "Coverage report: htmlcov/index.html"

# ============================================
# LINT / FORMAT (optional)
# ============================================

lint:
	@echo "Linting..."
	-$(PYTHON) -m flake8 $(SRC_DIR) $(TEST_DIR) --max-line-length=100 || true

format:
	@echo "Formatting with black..."
	-$(PYTHON) -m black $(SRC_DIR) $(TEST_DIR) --line-length=100 || true

# ============================================
# CLEAN
# ============================================

clean: clean-output clean-images clean-reports clean-db
	@echo "Cleaned generated outputs."

clean-output:
	@echo "Cleaning output/..."
	-$(RM_RF) $(OUTPUT_DIR)/*.csv
	-$(RM_RF) $(OUTPUT_DIR)/*.json
	-$(RM_RF) $(OUTPUT_DIR)/*.txt

clean-images:
	@echo "Cleaning images/..."
	-$(RM_RF) $(IMAGES_DIR)/*.png
	-$(RM_RF) $(IMAGES_DIR)/*.pdf

clean-reports:
	@echo "Cleaning reports/..."
	-$(RM_RF) $(REPORTS_DIR)/*.pdf
	-$(RM_RF) $(REPORTS_DIR)/*.pptx
	-$(RM_RF) $(REPORTS_DIR)/*.md

clean-db:
	@echo "Removing SQLite database..."
	-$(RM_FILE) retail_sales.db

clean-pycache:
	@echo "Removing __pycache__ folders..."
	-$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__') if p.is_dir()]"

clean-notebooks:
	@echo "Removing generated notebooks..."
	-$(RM_FILE) $(NOTEBOOKS_DIR)/*.ipynb

clean-all: clean clean-pycache
	@echo "Cleaning virtual environment..."
	-$(RM_RF) $(VENV_DIR)
	-$(RM_RF) .pytest_cache
	-$(RM_RF) .coverage
	-$(RM_RF) htmlcov
	@echo "Full clean complete."

# ============================================
# MAINTENANCE
# ============================================

tree:
	@echo "Project tree:"
	@$(PYTHON) -c "import os; [print(os.path.join(root, f)) for root, dirs, files in os.walk('.') if '__pycache__' not in root and 'venv' not in root and '.git' not in root for f in files]" | head -100

check-python:
	@$(PYTHON) --version
	@$(PYTHON) -c "import sys; assert sys.version_info >= (3, 10), 'Python 3.10+ required'; print('[OK] Python version OK')"

check-deps:
	@$(PYTHON) -c "import pandas; print(f'pandas: {pandas.__version__}')"
	@$(PYTHON) -c "import numpy; print(f'numpy: {numpy.__version__}')"
	@$(PYTHON) -c "import matplotlib; print(f'matplotlib: {matplotlib.__version__}')"
	@$(PYTHON) -c "import seaborn; print(f'seaborn: {seaborn.__version__}')"
	@$(PYTHON) -c "import sqlalchemy; print(f'sqlalchemy: {sqlalchemy.__version__}')"
	@$(PYTHON) -c "import pytest; print(f'pytest: {pytest.__version__}')"
	@echo "[OK] All core dependencies present."

# ============================================
# COMPOSITE TARGETS
# ============================================

all: setup run test
	@echo "All tasks complete."

# ============================================
# END OF MAKEFILE
# ============================================