.PHONY: install run dev migrate up down reset lint

install:
	pip install -e ".[dev]"

run:
	uvicorn social.main:app --host 0.0.0.0 --port 8005 --reload

dev: up run

migrate:
	alembic upgrade head

revision:
	alembic revision --autogenerate -m "$(msg)"

up:
	docker compose up -d

down:
	docker compose down

reset:
	docker compose down -v
	docker compose up -d
	sleep 2
	alembic upgrade head

lint:
	ruff check src/
	ruff format --check src/
