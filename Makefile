.PHONY: install test run demo clean

install:
	uv sync

test:
	uv run pytest -q

run:
	uv run uvicorn app.main:app --reload --port 8001

demo:
	uv run python -m app.demo

clean:
	rm -rf .pytest_cache __pycache__ .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
