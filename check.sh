#!/bin/sh

echo "mypy"
uv run mypy

echo "ruff"
uv run ruff check
