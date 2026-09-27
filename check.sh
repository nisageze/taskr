#!/bin/sh
set -e

echo "mypy"
uv run mypy

echo "ruff"
uv run ruff check

echo "format"
uv run ruff format --check

echo "pytest"
uv run pytest -v
