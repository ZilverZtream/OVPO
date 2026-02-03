.PHONY: lint test install up clean

lint:
	pre-commit run --all-files

test:
	python -m pytest tests/ -v

install:
	pip install -e ".[dev]"
	pre-commit install

up:
	@echo "Starting OVPO services..."
	@echo "TODO: Implement docker-compose or service startup"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
