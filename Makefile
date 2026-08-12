# Psyche1 Makefile
# Targets for development workflow

.PHONY: help install run clean format lint test venv

help:
	@echo "Targets:"
	@echo "  install  - Install Python dependencies from requirements.txt"
	@echo "  run      - Run the application (python -m sources.main)"
	@echo "  clean    - Remove __pycache__, .pyc, .egg-info, build artifacts"
	@echo "  format   - Run black on sources/ (if installed)"
	@echo "  lint     - Run flake8 on sources/ (if installed)"
	@echo "  test     - Run pytest (once tests are written)"

.venv:
	python3 -m venv .venv

install: .venv
	. .venv/bin/activate &&	pip install -r requirements.txt

run: .venv
	. .venv/bin/activate && python3 -m sources.main

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .tox/

format:
	black sources/

lint:
	flake8 sources/ --max-line-length=100

test:
	pytest
