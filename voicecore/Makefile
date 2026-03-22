.PHONY: dev build up down migrate seed logs clean test lint

dev:
	@echo "Starting development environment..."
	docker-compose up --build

build:
	@echo "Building Docker images..."
	docker-compose build

up:
	@echo "Starting production containers..."
	docker-compose up -d

down:
	@echo "Stopping containers..."
	docker-compose down

migrate:
	@echo "Running database migrations..."
	docker-compose exec backend alembic upgrade head

seed:
	@echo "Seeding demo data..."
	docker-compose exec backend python -m scripts.seed

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

clean:
	@echo "Cleaning up containers and volumes..."
	docker-compose down -v
	rm -rf frontend/.next

test:
	@echo "Running tests..."
	docker-compose exec backend pytest

lint:
	@echo "Running linters..."
	docker-compose exec backend ruff check .
	docker-compose exec frontend npm run lint

typecheck:
	@echo "Running type checks..."
	docker-compose exec backend mypy .
	docker-compose exec frontend npm run typecheck

deploy:
	@echo "Deploying to production..."
	git push origin main

restart:
	docker-compose restart backend

ps:
	docker-compose ps

shell-backend:
	docker-compose exec backend /bin/bash

shell-db:
	docker-compose exec postgres psql -U voicecore -d voicecore
