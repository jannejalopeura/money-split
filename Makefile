# Makefile for money-split development

.PHONY: help install test lint format typecheck check run clean

# Default target
help:
	@echo "Available commands:"
	@echo "  install    - Install dependencies"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linting"
	@echo "  format     - Format code"
	@echo "  typecheck  - Run type checking"
	@echo "  check      - Run all checks (lint, format, typecheck, test)"
	@echo "  run        - Run the application"
	@echo "  clean      - Clean up generated files"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	uv sync --extra dev

# Run tests
test:
	@echo "🧪 Running tests..."
	uv run pytest tests/ -v

# Run linting
lint:
	@echo "📋 Running linting..."
	uv run ruff check src/ tests/

# Format code
format:
	@echo "🎨 Formatting code..."
	uv run ruff format src/ tests/

# Check formatting (without making changes)
format-check:
	@echo "🎨 Checking code formatting..."
	uv run ruff format --check src/ tests/

# Run type checking
typecheck:
	@echo "🔧 Running type checking..."
	uv run ty check . --config-file ty.toml --python-version 3.8

# Run all checks
check: lint format-check typecheck test
	@echo "🎉 All checks passed!"

# Run the application
run:
	@echo "💰 Starting Money Split App..."
	uv run python src/app.py

# Clean up generated files
clean:
	@echo "🧹 Cleaning up..."
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf .pytest_cache/
	rm -rf logs/*.log
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
