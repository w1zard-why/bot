# Makefile
init:
	poetry install && pre-commit install
migrate:
	psql "$$PG_DSN" -f bot/app/db/schema.sql
run-dev:
	python -m bot.app.main
run-docker:
	docker compose up --build
