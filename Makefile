.PHONY: dev migrate seed test e2e types evals lint

dev:
	docker compose up -d db redis
	@echo "Starting api..."
	cd apps/api && uv run uvicorn app.main:app --reload --port 8000 &
	@echo "Starting worker..."
	cd apps/api && uv run arq app.workers.settings.WorkerSettings &
	@echo "Starting web..."
	cd apps/web && pnpm dev &
	wait

migrate:
	cd apps/api && uv run alembic upgrade head

seed:
	cd apps/api && uv run python -m app.demo.seed

test:
	cd apps/api && uv run pytest -q
	pnpm -C apps/web test

e2e:
	pnpm -C apps/web exec playwright test

types:
	# Assuming openapi-typescript is installed globally or in apps/web
	pnpm exec openapi-typescript http://localhost:8000/openapi.json -o packages/api-types/index.d.ts

evals:
	cd apps/api && uv run python -m evals.run --suite all

lint:
	cd apps/api && uv run ruff check .
	cd apps/api && uv run mypy app
	pnpm -C apps/web lint
