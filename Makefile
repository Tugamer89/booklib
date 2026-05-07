.PHONY: reqs dev-reqs format lint hook-update install

reqs:
	pip-compile --strip-extras requirements.in

dev-reqs: reqs
	pip-compile --strip-extras requirements-dev.in

install:
	pip-sync requirements.txt requirements-dev.txt

format:
	npx prettier --write "**/*.{js,css,html,json,md,yml,yaml}"
	ruff format .

hook-update:
	pre-commit autoupdate

run:
	uvicorn main:app --reload --port 8000