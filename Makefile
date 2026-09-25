# Testpiramide-demo. Overzicht van alle commando's: make help
PYTHON ?= python
export PYTHONPATH := src

.DEFAULT_GOAL := help
.PHONY: help stap klaar reset setup run dashboard test lint all

help: ## Toon alle commando's
	@grep -hE '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  make %-10s %s\n", $$1, $$2}'

# --- Demo-navigatie -----------------------------------------------------------

stap: ## Ga naar het begin van stap N, bijv. make stap N=2
	@sh scripts/ga-naar.sh stap "$(N)"

klaar: ## Ga naar het eindresultaat van stap N, bijv. make klaar N=2
	@sh scripts/ga-naar.sh klaar "$(N)"

reset: ## Gooi alle lokale wijzigingen weg (toegepaste patches, werk van je agent)
	@git reset --hard --quiet HEAD
	@git clean -fd --quiet
	@echo "Schoon. Je staat op $$(git branch --show-current)."

# --- Pipeline -----------------------------------------------------------------

setup: ## Installeer het project en de dev-tools
	$(PYTHON) -m pip install -e ".[dev]"

run: ## Draai de pipeline (maakt eerst synthetische data als die er nog niet is)
	$(PYTHON) -m sales_forecast.pipeline

dashboard: ## Toon het dashboard (leest daily_sales)
	$(PYTHON) -m sales_forecast.dashboard

# --- Testpiramide --------------------------------------------------------------

test: ## Unit tests: snel, draai ze na elke wijziging
	$(PYTHON) -m pytest tests/unit -m unit -q

lint: ## Ruff: stijl en veelgemaakte fouten
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

all: lint test ## Alles: lint + test
