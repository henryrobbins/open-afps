# Common dev commands for the open-atp package.

.PHONY: help install test test-docker test-modal test-aristotle test-agent cov cov-open cov-clean lint format typecheck check gen-provers check-provers build build-image docs docs-serve docs-clean clean

help:
	@echo "Targets:"
	@echo "  install         Sync deps with uv"
	@echo "  test            Run pytest, skipping docker/modal/live-API tests"
	@echo "  test-docker     Run docker-marked tests (requires the built image)"
	@echo "  test-modal      Run modal-marked tests (requires a Modal token)"
	@echo "  test-aristotle  Run the live Aristotle API test (needs ARISTOTLE_API_KEY)"
	@echo "  test-agent      Run the live agent CLI test (billable + needs creds)"
	@echo "  cov             Run pytest with coverage; HTML to htmlcov/, XML to coverage.xml"
	@echo "  cov-open        Open the HTML coverage report"
	@echo "  cov-clean       Remove coverage artifacts"
	@echo "  lint            Run ruff check"
	@echo "  format          Run ruff format + ruff check --fix"
	@echo "  typecheck       Run mypy"
	@echo "  check           Run lint + typecheck + check-provers + test"
	@echo "  gen-provers     Regenerate the prover table in README from docs/provers.yaml"
	@echo "  check-provers   Fail if README's prover table is stale"
	@echo "  build           Build the sdist + wheel into dist/"
	@echo "  build-image     Build the open-atp:latest Docker image"
	@echo "  docs            Build the Sphinx docs once"
	@echo "  docs-serve      Live-reload docs in browser"
	@echo "  docs-clean      Remove built docs"
	@echo "  clean           Remove build + cache artifacts"

install:
	uv sync

test:
	uv run pytest

test-docker:
	uv run pytest -m 'docker'

test-modal:
	uv run pytest -m 'modal'

test-aristotle:
	uv run pytest -m 'aristotle_api'

test-agent:
	uv run pytest -m 'agent_api'

cov:
	uv run pytest \
		--cov=open_atp \
		--cov-report=term-missing \
		--cov-report=html \
		--cov-report=xml

cov-open: cov
	@python -c "import os, webbrowser; webbrowser.open('file://' + os.path.abspath('htmlcov/index.html'))"

cov-clean:
	rm -rf htmlcov coverage.xml .coverage

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests
	uv run ruff check --fix src tests

typecheck:
	uv run mypy

check: lint typecheck check-provers test

gen-provers:
	uv run python docs/_ext/provers_table.py

check-provers:
	uv run python docs/_ext/provers_table.py --check

build:
	uv build

build-image:
	docker build -t open-atp:latest images/

docs:
	uv run --extra docs sphinx-build -W -b html docs docs/_build/html

docs-serve:
	uv run --extra docs sphinx-autobuild --watch src \
		--ignore '*/provers/_table.md' docs docs/_build/html

docs-clean:
	rm -rf docs/_build

clean: docs-clean cov-clean
	rm -rf build dist .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
