# ARCHITECTURE.md — CreatorOS

## 1. Context and constraints

| Constraint | Implication |
|---|---|
| 27 projects in ≥ 5 stacks (Next.js, React/Vite+Express, FastAPI, vanilla JS, TS LangGraph monorepo) | Standardize on one backend language and one frontend framework; port logic, not processes |
| 4 LLM providers in use (Gemini majority, Anthropic, OpenAI, Groq, plus Ollama locally) | Provider-agnostic LLM gateway with tiers |
| 5 data stores in use (SQLite, Postgres/pgvector, Supabase, Mongo, Chroma) | One store: Postgres + pgvector |
| 22 people, one integration day, evaluation criteria unknown | Contract-first; parallel porting; demo mode that never depends on live APIs |
| Every project already has agents + judge + LangSmith | Keep LangSmith; centralize judging; keep each agent's prompt IP |

## 2. Architecture style: modular monolith + optional remote capabilities

```
                         ┌───────────────────────────────────────────┐
  Browser  ─────────────►│  apps/web  (Next.js 15, App Router, TS)    │  Vercel
                         │  UI · Omnibox · Run drawer · Card registry │
                         └───────────────┬───────────────────────────┘
                              REST + SSE │  (JWT from Supabase Auth)
                         ┌───────────────▼───────────────────────────┐
                         │  apps/api  (FastAPI, Python 3.12)          │  Railway / Render
                         │  routers → services → orchestration        │
                         │  ┌───────────────────────────────────────┐ │
                         │  │ ORCHESTRATION (LangGraph)              │ │
                         │  │ intent_router · director · brain ·     │ │
                         │  │ autopilot · ingest pipelines           │ │
                         │  └──────────────┬────────────────────────┘ │
                         │  ┌──────────────▼────────────────────────┐ │
                         │  │ CAPABILITIES (17 specialists)          │ │
                         │  │ in-process by default; REMOTE adapter  │─┼──► e.g. clip-service (FFmpeg/Whisper)
                         │  └──────────────┬────────────────────────┘ │
                         │  ┌──────────────▼────────────────────────┐ │
                         │  │ PLATFORM: llm_gateway · context_builder│ │
                         │  │ judge_service · validators · memory    │ │
                         │  │ tools(web_search, fetch, transcribe)   │ │
                         │  └───────────────────────────────────────┘ │
                         └───────┬──────────────┬──────────────┬─────┘
                                 │              │              │
                  ┌──────────────▼───┐  ┌───────▼──────┐ ┌─────▼──────────┐
                  │ Postgres+pgvector│  │ Redis (arq)  │ │ Object storage │  Supabase / Upstash
                  │ + LangGraph ckpt │  │ jobs, cache, │ │ uploads, media │
                  └──────────────────┘  │ pub/sub      │ └────────────────┘
                                        └──────┬───────┘
                                   ┌───────────▼──────────┐
                                   │ apps/worker (arq)     │  same codebase as api
                                   │ ingest, long runs,    │
                                   │ offline evals, cron   │
                                   └──────────────────────┘
        All LLM/tool calls ──► LangSmith (traces, feedback, datasets, experiments)
```

## 3. Architecture decision records

| ADR | Decision | Why | Rejected alternative |
|---|---|---|---|
| 001 | **Python FastAPI + LangGraph** for the backend | Deepest agentic projects are Python (11, 13, 19, 20) or LangGraph (21 TS ports cleanly); media stack (Whisper/FFmpeg, #06) is Python; LangSmith eval SDK is most mature in Python | Keep 27 services (27 deploys, 27 auths, incompatible schemas); TS-only backend (loses #06/#13/#19 code) |
| 002 | **Next.js 15 + TypeScript + Tailwind + shadcn/ui** frontend | Most project UIs are Next.js (03, 07, 09, 12, 14, 18, 20, 21) → components port with minimal change | Vite SPA (loses routing/SSR conventions most teams used) |
| 003 | **Postgres + pgvector (Supabase)** as the only datastore | Relational campaign/asset model + vectors + auth + storage in one; #11, #13, #19 already use pgvector | Mongo (#16, #21), Chroma (#20), SQLite (#06, #10, #17) — migrate data shapes into schema.sql |
| 004 | **Campaign is the root aggregate**; everything is an `asset` of a campaign | Prevents "27 mini-apps"; one UI card registry | Per-tool tables |
| 005 | **Capability registry + uniform contract** (`AGENT_CONTRACT.md`) | Lets 22 people port in parallel without stepping on each other; orchestrators treat capabilities uniformly | Ad-hoc function calls |
| 006 | **Director = planner/executor graph; Brain = supervisor with agents-as-tools** | Campaigns need a deterministic, checkpointable DAG; chat needs flexible routing (#19 pattern proven) | One giant ReAct agent for everything (slow, unpredictable, hard to evaluate) |
| 007 | **One judge service with a rubric registry** | Comparable scores; one calibration; cost control | 27 per-project judges |
| 008 | **LLM gateway with model tiers + fallback chain** | Cost/latency control; provider outages don't break demo | Each capability picks its own SDK |
| 009 | **SSE** for streaming | One-way server→client is all we need; works through proxies; simple reconnect with `Last-Event-ID` | WebSockets |
| 010 | **LangSmith** for tracing, feedback, datasets, experiments | Already used by the cohort; evaluator-visible evidence | Custom logging only |
| 011 | **arq + Redis** for background jobs, with a Postgres `jobs` table fallback | Lightweight asyncio queue; fallback keeps local dev simple | Celery (heavier), BullMQ (Node) |
| 012 | **No auto-publishing** | Safety, scope, platform API approvals | Direct posting |
| 013 | **Remote capability escape hatch** | Heavy deps (FFmpeg/Whisper) or a stack that can't be ported today can run as a service implementing the same HTTP contract | Forcing everything in-process today |
| 014 | **Types generated from OpenAPI** (`openapi-typescript`) | Pydantic is the single schema source; frontend never drifts | Hand-written TS types |

## 4. Layer responsibilities

| Layer | Owns | Must not |
|---|---|---|
| `api/routers` | HTTP, auth dependency, request validation, SSE endpoints | Call LLMs, contain business logic |
| `services` | Use cases (create campaign, import comments), transactions, authorization by `creator_id` | Build prompts |
| `orchestration` | LangGraph graphs, interrupts, fan-out, calling judge | Talk to providers directly |
| `capabilities/<name>` | Prompts, input/output schemas, capability logic, rubric, dataset | Touch DB, call other capabilities (except declared), pick models |
| `platform` | LLM gateway, context builder, judge, validators, memory, tools, tracing | Know about specific capabilities |
| `db` | SQLAlchemy models, repositories (always filter by `creator_id`), migrations | — |

## 5. Main data flows

### 5.1 Campaign run (sequence)
```
Web                API                     Worker/Graph                LLM/Tools        DB
 │ POST /campaigns  │                          │                          │              │
 │─────────────────►│ insert campaign ─────────┼──────────────────────────┼─────────────►│
 │ POST /campaigns/{id}/runs                   │                          │              │
 │─────────────────►│ insert agent_run, enqueue│                          │              │
 │◄─ {run_id} ──────│─────────────────────────►│ load_context ────────────┼─────────────►│
 │ GET /runs/{id}/events (SSE)                 │ research ∥ library ∥ audience ─────────►│
 │◄═══ node.completed(card) ═══ pubsub ◄───────│ emit events (Redis pub/sub + run_events)│
 │◄═══ checkpoint.required ════════════════════│ interrupt()                             │
 │ POST /runs/{id}/resume {angle}              │                          │              │
 │─────────────────►│─────────────────────────►│ brief → hooks → judge → script → judge  │
 │◄═══ cards ... ══════════════════════════════│ fan-out: visual ∥ copy ∥ repurpose      │
 │◄═══ run.completed(package_score) ═══════════│ persist assets, write-back embeddings ─►│
```

### 5.2 Ingest
Upload → object storage → `sources` row → job: transcribe (if media) → chunk (transcripts 45–90 s windows with timestamps; posts whole; PDFs by section) → embed (batch 100) → `chunks` → enrichment fan-out based on source kind: comments → `audience.analyze`; analytics CSV → `performance.patterns` → `insights`; past posts → `voice.build_profile`; transcript → `clip.clips` + `ideation(source=library_gap)` → `opportunities`.

### 5.3 Home feed (opportunity generation)
On import completion and nightly cron: collect trend candidates (web search on pillars), top audience questions, active insights, recycle candidates → `ideation` scores them → top 5 written to `opportunities` with evidence ids. Home reads from the table (fast page load; no LLM on page view).

## 6. Deployment topology

| Component | MVP host | Local dev |
|---|---|---|
| Web | Vercel | `pnpm dev` (port 3000) |
| API | Railway/Render (1 instance, 1 GB) | `uvicorn app.main:app --reload` (8000) |
| Worker | Same image, `arq app.workers.settings.WorkerSettings` | same |
| Postgres/pgvector, Auth, Storage | Supabase | `docker compose up db` (pgvector image) or Supabase CLI |
| Redis | Upstash | `docker compose up redis` |
| Tracing | LangSmith cloud | same |

`docker-compose.yml` (to be written in the build system) defines: `db` (pgvector/pgvector:pg16), `redis`, `api`, `worker`, `web`.

## 7. Scale and what to revisit

Assumed MVP load: tens of concurrent creators, < 5 concurrent campaigns. Single API + single worker suffice. Revisit when: campaigns > 50 concurrent (scale workers horizontally; graph runs are stateless apart from the checkpointer), chunks > 5 M (partition by creator, tune HNSW), media ingest heavy (move `clip`/transcription to a GPU remote capability), multi-tenant teams (add `workspace_id` above `creator_id`).

## 8. Security model

Supabase Auth issues JWT → FastAPI dependency verifies with the project JWT secret → resolves `creator_id` → every repository method requires `creator_id`. Service role key only on the server. Uploads: max 500 MB media / 20 MB docs, MIME allow-list, virus scanning out of scope. Secrets via env only; CI runs `gitleaks`. Untrusted text is wrapped as data in prompts. Rate limit per creator on run creation (e.g. 20 campaigns/hour).

## 9. Trade-offs we accept

| Choice | Cost we accept |
|---|---|
| Port everything to Python | JS/TS owners translate code today (mostly prompts + zod → pydantic, small effort) |
| One datastore | Some projects' data shapes change (Mongo documents → jsonb columns) |
| Centralized judge | Owners lose their bespoke judge code; their criteria move into rubric YAML (nothing lost semantically) |
| Checkpoints in campaign mode | Slightly slower end-to-end; much better creator control and demo narrative |
| Modular monolith | Single deploy blast radius; mitigated by remote capability option and per-node error isolation |
