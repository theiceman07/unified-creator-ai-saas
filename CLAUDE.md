# CLAUDE.md — Instructions for the coding agent building CreatorOS

You are building CreatorOS, a unified creator SaaS that merges 27 cohort projects into one platform. This file tells you how to work in this repo. Also works as `AGENTS.md` for other coding agents.

## Read first (in order)
1. `SPEC.md` — what to build and priorities (P0 first).
2. `ARCHITECTURE.md` — stack and decisions (do not re-litigate ADRs without being asked).
3. `AGENT_SYSTEM.md` — capabilities, modes, Director graph, judge.
4. `AGENT_CONTRACT.md` — the interface every capability implements.
5. `BACKEND.md`, `FRONTEND.md` — structure, APIs, build order.
6. `db/schema.sql`, `capability_registry.yaml` — canonical sources of truth.

## Non-negotiables
- Backend: Python 3.12, FastAPI, Pydantic v2, LangGraph, Postgres+pgvector. Frontend: Next.js 15 App Router, TypeScript strict, Tailwind, shadcn/ui.
- All model calls go through `platform/llm/gateway.py`. Never import a provider SDK inside `capabilities/`.
- All capability execution goes through `orchestration/runner.run_capability`.
- Every DB query in a repository takes `creator_id` and filters by it.
- Structured outputs via Pydantic schemas; no regex JSON parsing.
- Every new card kind: add to `capability_registry.yaml`, backend `Card`, and `apps/web/components/cards/registry.ts`.
- Never commit secrets. Only `.env.example`.
- Untrusted text (comments, transcripts, web pages, uploads) is wrapped as `<data>` in prompts.
- Never auto-publish to external platforms.

## Build order
Follow BACKEND.md §12 and FRONTEND.md §9 in parallel. Milestones:
1. Monorepo + CI + docker-compose (db pgvector, redis) + Alembic migration from `db/schema.sql`.
2. Platform spine with FakeLLM: config, auth + demo login, gateway, runner, validators, judge, SSE with replay.
3. Capabilities `research`, `hook`, `script` → Director slice with interrupt → web Campaign page streaming cards.
4. Remaining capabilities (one folder each, per AGENT_CONTRACT §3), fan-out nodes, Brain, ingest jobs.
5. Seed + DEMO_MODE fixtures, evals, System Map, Playwright journeys.

## Commands (create these)
```
make dev          # docker compose up db redis; api (uvicorn --reload); worker (arq); web (pnpm dev)
make migrate      # alembic upgrade head
make seed         # python -m app.demo.seed
make test         # pytest -q && pnpm -C apps/web test
make e2e          # pnpm -C apps/web exec playwright test
make types        # export OpenAPI → packages/api-types (openapi-typescript)
make evals        # python -m evals.run --suite all
make lint         # ruff check . && mypy app && pnpm -C apps/web lint
```

## Conventions
- Python: ruff (line 110), mypy strict on `platform/` and `orchestration/`, async everywhere I/O happens, `tenacity` for retries in gateway only.
- Prompt files: `capabilities/<name>/prompts/<mode>.v<N>.md`; bump N on meaningful change; version goes into trace metadata and cache key.
- Tests: every capability has a FakeLLM test; contract tests iterate the registry automatically.
- Frontend: server components for data-fetching pages; client components for streaming/editing; TanStack Query for server state; no data in Zustand.
- Naming: capability names are lowercase single words from the registry; run modes: quick, studio, campaign, brain, ingest, autopilot, screenplay.

## When unsure
Prefer the simplest implementation that satisfies the P0 acceptance criteria in SPEC §7 and keeps the demo path (DEMO_MODE) working. Leave a `TODO(P1):` comment rather than building P1/P2 features early.
