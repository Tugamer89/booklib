.PHONY: install format hook-update run

install:
	uv sync

format:
	npx prettier --write "**/*.{js,css,html,json,md,yml,yaml}"
	uv run ruff format .

hook-update:
	uv run pre-commit autoupdate

run:
	uv run uvicorn main:app --reload --port 8000