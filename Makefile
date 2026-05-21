.PHONY: install build-ts format hook-update run

install:
	uv sync
	npm install

build-ts:
	npx tsc

format:
	npx prettier --write "**/*.{ts,js,css,html,json,md,yml,yaml}"
	uv run ruff format .

hook-update:
	uv run pre-commit autoupdate

run: build-ts
	uv run uvicorn main:app --reload --port 8000