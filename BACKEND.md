# BACKEND.md — Implementation plan (apps/api + apps/worker)

## 1. Stack

Python 3.12 · FastAPI · Pydantic v2 · SQLAlchemy 2 (async) + asyncpg · Alembic · pgvector (`pgvector` python) · LangGraph + `langgraph-checkpoint-postgres` · langchain-core + provider packages (`langchain-google-genai`, `langchain-anthropic`, `langchain-openai`, `langchain-groq`) · LangSmith SDK · arq + redis · sse-starlette · httpx · tenacity · python-multipart · yt-dlp (transcripts) · faster-whisper (optional, worker only) · ffmpeg (system, clip service only) · pytest + pytest-asyncio · ruff + mypy · uv for dependency management.

## 2. Monorepo layout

```
creatoros/
├── apps/
│   ├── web/                         # Next.js (see FRONTEND.md)
│   └── api/
│       ├── pyproject.toml
│       ├── alembic/                 # migrations generated from db/schema.sql
│       ├── app/
│       │   ├── main.py              # FastAPI app, CORS, routers, lifespan (load registry, warm gateway)
│       │   ├── core/                # config.py (pydantic-settings), auth.py, errors.py, logging.py, ids.py
│       │   ├── db/                  # session.py, models/*.py, repositories/*.py (creator-scoped)
│       │   ├── api/routers/         # one file per resource (see §4)
│       │   ├── services/            # campaign_service.py, ingest_service.py, discover_service.py ...
│       │   ├── orchestration/
│       │   │   ├── registry.py      # loads capability_registry.yaml, maps name → Capability class
│       │   │   ├── runner.py        # run_capability(): cache → call → validators → judge → persist → emit
│       │   │   ├── events.py        # RunEvent model, emitter (Redis pub/sub + run_events table)
│       │   │   ├── intent_router.py
│       │   │   ├── director/        # graph.py, state.py, nodes.py
│       │   │   ├── brain/           # supervisor.py, tools.py
│       │   │   ├── ingest/          # pipelines per source kind
│       │   │   └── autopilot/       # (P2)
│       │   ├── capabilities/
│       │   │   ├── _base.py         # Capability ABC, RunContext, CapabilityResult (AGENT_CONTRACT.md)
│       │   │   ├── _schemas/        # shared models: Citation, Card, PlatformLimits, Hook, Script ...
│       │   │   ├── research/        # capability.py, schemas.py, prompts/*.md, rubric.yaml, dataset.jsonl, tests/
│       │   │   ├── library/ ideation/ audience/ strategy/ hook/ script/ copy/ voice/
│       │   │   └── repurpose/ visual/ clip/ performance/ recycle/ pitch/ collab/ screenplay/
│       │   ├── platform/
│       │   │   ├── llm/             # gateway.py, tiers.py, providers.py, cache.py, usage.py
│       │   │   ├── context/         # builder.py, partials/creator_context.md
│       │   │   ├── judge/           # service.py, rubric_loader.py, pairwise.py
│       │   │   ├── validators/      # platform_limits.py, schema.py, citations.py, repetition.py, timestamps.py
│       │   │   ├── memory/          # embed.py, chunking.py, search.py (calls match_chunks)
│       │   │   ├── tools/           # web_search.py, web_fetch.py, youtube.py, transcribe.py, ffmpeg.py
│       │   │   └── tracing.py       # LangSmith helpers: tags, metadata, feedback
│       │   ├── rubrics/             # <capability>_v1.yaml (judge rubric registry)
│       │   ├── workers/             # settings.py (arq), jobs.py, cron.py
│       │   └── demo/                # seed.py, fixtures/*.json (recorded outputs for DEMO_MODE)
│       ├── evals/                   # run_evals.py, datasets sync to LangSmith, report.py
│       └── tests/                   # unit, integration (testcontainers pgvector), contract tests
├── packages/
│   └── api-types/                   # generated TS types from OpenAPI (openapi-typescript)
├── db/schema.sql                    # canonical DDL (this pack)
├── capability_registry.yaml         # canonical roster (this pack)
├── docker-compose.yml
├── .env.example
└── .github/workflows/ci.yml         # lint, typecheck, tests, gitleaks, contract tests, eval smoke
```

## 3. Core platform modules

### 3.1 LLM gateway (`platform/llm/gateway.py`)
```python
class LLMGateway:
    async def structured(self, *, tier: Tier, schema: type[BaseModel], messages: list[Msg],
                         capability: str, mode: str, prompt_version: str,
                         cache_key_parts: dict | None = None, temperature: float | None = None) -> tuple[BaseModel, Usage]
    async def text(self, *, tier: Tier, messages, stream: bool = False, **meta) -> AsyncIterator[str] | tuple[str, Usage]
    async def embed(self, texts: list[str]) -> list[list[float]]          # batches of 100, fixed EMBEDDING_DIM
```
- Tier → ordered provider list from env (`LLM_TIER_FAST=gemini:<model>,groq:<model>` …). First healthy provider wins; on timeout/5xx/429 fall through; circuit breaker per provider (open 60 s after 3 failures).
- Uses `with_structured_output(schema)`; on validation error, one repair call on fast tier.
- Cache: Redis `llm:{sha256}` TTL 24 h, Postgres `llm_cache` fallback. Bypass with `no_cache=True` (regenerate button).
- Usage accounting → `agent_runs.tokens_in/out/cost_usd` (price table in `tiers.py`).
- Every call wrapped with LangSmith `traceable` including tags/metadata from the `RunContext`.

### 3.2 Context builder (`platform/context/builder.py`)
`async def build(creator_id, *, topic: str | None) -> CreatorContext` — one query batch: creator, active voice profile (pinned version), strategy, top 5 active insights, last 20 CTAs, last 30 topics, 3–5 exemplar posts (highest engagement, optionally topic-similar via `match_chunks`). Trims to `token_budget`. Cached per run.

### 3.3 Runner (`orchestration/runner.py`) — the heart of uniform behavior
```python
async def run_capability(name: str, mode: str, payload: dict, rc: RunContext,
                         *, judge: JudgePolicy = JudgePolicy.default(), persist_as: AssetTarget | None = None) -> CapabilityResult:
    cap = registry.get(name); cap.assert_mode(mode, rc.run_mode)
    inp = cap.input_model.model_validate(payload)
    rc.emit(NodeStarted(capability=name, mode=mode))
    result = await with_timeout(cap.run(inp, rc.child(name, mode)), cap.timeout_s)
    checks = validators.run(name, result.output, rc.context)          # deterministic
    score = await judge_service.maybe_judge(name, inp, result, checks, policy=judge, rc=rc)
    if score and not score.passed and cap.supports_revise and judge.allow_repair:
        result = await cap.run(inp.with_feedback(score.fix_instructions), rc.child(name, mode, attempt=2))
        score = await judge_service.judge(name, inp, result, rc=rc)
    assets = await persist(result, persist_as, score) if persist_as else []
    rc.emit(NodeCompleted(capability=name, mode=mode, cards=result.cards, score=score, asset_ids=assets))
    return result
```
Quick mode, Studio mode, Director nodes and Brain tools all go through `run_capability`. This one function guarantees tracing, judging, validation, persistence and events are identical across all 17 capabilities.

### 3.4 Judge service (`platform/judge/service.py`)
Loads `rubrics/*.yaml` at boot. `judge()` builds a rubric prompt (criteria + anchors + input + output + deterministic check results), calls judge tier with a `JudgeScore` schema, computes weighted overall and hard fails, stores in `judge_scores`, posts LangSmith feedback. `pairwise(candidates, rubric)` runs a knockout tournament for hooks/titles. Policy object controls always/sample/never per mode.

### 3.5 Memory (`platform/memory`)
Chunking rules: transcripts 45–90 s windows with 10 s overlap keeping `start_s/end_s`; posts whole (split > 800 tokens); PDFs by heading. Search: `match_chunks` SQL function (0.75 vector + 0.25 keyword), optional LLM rerank of top 20 → 8 for Brain answers.

### 3.6 Tools
`web_search` (provider via env: Tavily/Serper/Brave; returns title/url/snippet), `web_fetch` (httpx + readability extraction, 15 s timeout, 200 KB cap), `youtube.transcript(url)` (yt-dlp captions, fallback to audio + Whisper in worker), `transcribe(file)` (faster-whisper small on CPU for demo lengths; API alternative via env), `ffmpeg.cut(source, start, end)` (clip service only).

## 4. REST API (prefix `/v1`, JSON, JWT bearer)

| Method & path | Purpose | Mode |
|---|---|---|
| `GET /health` · `GET /health/deps` | Liveness; DB/Redis/LLM/LangSmith checks | — |
| `GET /me` · `PATCH /me` | Creator profile | — |
| `POST /onboarding` | Save onboarding answers, create creator, trigger ingest of provided posts | ingest |
| `GET /voice` · `POST /voice/build` · `PATCH /voice` | Voice profile read/build/edit (creates new version) | ingest |
| `GET /strategy` · `POST /strategy/pillars` | Pillars/audience | quick |
| `POST /intents` | Omnibox → `{route, capability, slots, confidence, suggestions}` | — |
| `GET /capabilities` | Registry (for UI + System Map), with health stats | — |
| `POST /capabilities/{name}/invoke` | Quick mode `{mode, input}` → `{run_id}` (SSE) or `?sync=true` → result | quick |
| `POST /campaigns` · `GET /campaigns` · `GET /campaigns/{id}` · `PATCH` · `DELETE` | Campaign CRUD (GET returns assets grouped by kind) | — |
| `POST /campaigns/{id}/runs` | Start Director `{auto_decide: bool, from_step?: str}` → `{run_id}` | campaign |
| `GET /runs/{id}` | Run status + summary + trace URL | — |
| `GET /runs/{id}/events` | **SSE** stream; supports `Last-Event-ID` replay from `run_events` | all |
| `POST /runs/{id}/resume` | Resume interrupt `{checkpoint, decision}` | campaign |
| `POST /runs/{id}/cancel` | Cancel | all |
| `GET /assets/{id}` · `PATCH /assets/{id}` | Edit (creates `asset_versions` row, `edited_by=user`) | — |
| `POST /assets/{id}/regenerate` | `{instruction?, mode?}` studio action (regenerate, shorten, restyle…) | studio |
| `GET /assets/{id}/versions` | Version history | — |
| `POST /sources` (multipart or `{url}`) · `GET /sources/{id}` | Upload/link → ingest job | ingest |
| `GET /library` · `GET /library/search?q=` | Library list; hybrid search | — |
| `POST /brain/threads` · `POST /brain/threads/{id}/messages` (SSE) | Chat with Brain | brain |
| `GET /opportunities` · `PATCH /opportunities/{id}` · `POST /opportunities/{id}/convert` | Home/Discover feed; convert → campaign | — |
| `POST /discover/ideas` · `POST /discover/trend` · `POST /discover/research` | Discover panels (thin wrappers on quick mode) | quick |
| `POST /audience/import` · `GET /audience/report` · `POST /audience/clusters/{id}/to-ideas` | Comments | ingest/quick |
| `POST /analytics/import` · `GET /insights` · `POST /insights/next` · `POST /library/{id}/explain` | Analytics copilot | ingest/quick |
| `GET /recycle/candidates` · `POST /recycle/{library_id}/refresh` | Recycler | quick/campaign |
| `GET /calendar?from&to` · `PATCH /calendar/{id}` · `GET /calendar.ics` | Calendar | — |
| `POST /pitches` · `GET /pitches/{id}` · `PATCH` | Brand pitch | quick |
| `POST /collab/search` | Collab finder | quick |
| `POST /screenplay/{campaign_id}/scene` · `GET/PATCH /screenplay/{campaign_id}/bible` | Screenplay | screenplay |
| `POST /feedback` | Signals | — |
| `GET /admin/evals/latest` · `POST /admin/evals/run` | Eval reports (admin only) | — |
| `GET /campaigns/{id}/export?format=md` | Export package | — |

Error envelope: `{"error": {"code": "CAPABILITY_TIMEOUT", "message": "...", "retryable": true, "run_id": "..."}}`. Codes: `VALIDATION_ERROR, NOT_FOUND, UNAUTHORIZED, RATE_LIMITED, CAPABILITY_TIMEOUT, PROVIDER_UNAVAILABLE, JUDGE_FAILED, INGEST_FAILED, INTERNAL`.

## 5. SSE event protocol (`GET /v1/runs/{id}/events`)

Each event: `id: <seq>`, `event: <type>`, `data: <json>`.

| type | data | UI behavior |
|---|---|---|
| `run.started` | `{run_id, mode, plan: [{step, capability, label}]}` | Render timeline skeleton with all planned steps |
| `node.started` | `{step, capability, mode, origin_projects}` | Step spinner; show origin tag |
| `node.progress` | `{step, message}` (short "thought", ≤ 140 chars) | Subtitle under step |
| `node.token` | `{step, delta}` (optional, script/brain only) | Typewriter in active card |
| `node.completed` | `{step, cards: [Card], asset_ids, score?: JudgeScoreLite, latency_ms, cache_hit}` | Render card(s) via card registry; judge badge |
| `node.failed` | `{step, error, retryable}` | Inline retry button; run continues |
| `judge.scored` | `{asset_id, overall, passed, critique}` | Update badge |
| `checkpoint.required` | `{checkpoint: "choose_angle", options: [...], default}` | Modal/inline picker |
| `run.completed` | `{package_score, asset_count, cost_usd, latency_ms, trace_url}` | Summary banner |
| `run.failed` | `{error}` | Error state with partial results kept |
| `heartbeat` | `{}` every 15 s | — |

`Card` shape (shared by all capabilities): `{kind, title, data, citations?: [Citation], origin: {capability, mode, projects: ["09"]}, asset_id?}`.

## 6. Background jobs (arq)

| Job | Trigger | Steps |
|---|---|---|
| `run_campaign` | POST runs | Executes Director graph; emits events |
| `ingest_source` | POST sources | fetch/transcribe → chunk → embed → enrich by kind |
| `import_comments` | audience import | batch classify (50/call) → embed → cluster (HDBSCAN or k-means on embeddings) → label clusters (fast tier) → opportunities |
| `import_analytics` | analytics import | normalize CSV → metrics → `performance.patterns` → insights → opportunities |
| `refresh_opportunities` | cron nightly + after imports | trend search per pillar, recycle candidates, questions, insights → ideation scoring → top 5 |
| `rebuild_voice` | ≥ 10 new accepted assets | `voice.build_profile` → new version (inactive until creator accepts) |
| `run_evals` | manual / CI nightly | see EVALUATION.md |
| `autopilot_week` | cron (P2) | autopilot graph |

Without Redis (`QUEUE_BACKEND=postgres`) jobs are polled from the `jobs` table by the worker; events use an in-process broadcaster + `run_events` replay.

## 7. Data model notes

See `db/schema.sql`. Key rules: `campaigns` is the root aggregate; `assets.content` is validated against the producing capability's output schema before insert; every edit creates an `asset_versions` row; `judge_overall` denormalized on `assets` for list views; `agent_runs.langsmith_run_id` powers "View trace". Migration from project data: Mongo documents (#16, #21) → jsonb in `assets.content` / `library_items`; SQLite tables (#06, #10, #17) → mapped in `demo/seed.py`; Chroma collections (#20) → re-embed into `chunks`.

## 8. Auth

Supabase Auth (email magic link + Google). FastAPI dependency `current_creator()` verifies JWT (`SUPABASE_JWT_SECRET`), loads/creates `creators` row. `DEMO_MODE=true` exposes `POST /v1/demo/login` issuing a token for the seeded demo creator (evaluators can use the app without signing up).

## 9. Demo mode and seed data (evaluation insurance)

`python -m app.demo.seed` creates **"Demo Creator — Tech Educator"** with: 25 past posts (voice source), 1 podcast transcript (~20 min), 500 comments, 60 days of analytics for 30 items, 5 pillars, voice profile v1, 2 finished campaigns, opportunities populated. Each capability ships `demo/fixtures/<capability>.json` with recorded outputs for the golden inputs. When `DEMO_MODE=true` and a provider fails, the runner serves the fixture (labelled `offline draft`) so the live demo never shows an error.

## 10. Testing

| Level | What | Tooling |
|---|---|---|
| Unit | Validators, chunking, cache keys, rubric scoring math, schema round-trips per capability | pytest |
| Contract | Every registered capability: input/output models export JSON schema, `run()` works with `FakeLLM` returning schema-valid data, declared rubric exists, dataset has ≥ 8 rows | pytest parametrized over registry |
| Integration | Director graph end-to-end with `FakeLLM`, interrupt/resume, SSE replay, repository scoping (creator A can't read B) | pytest + testcontainers (pgvector) |
| Eval | Golden datasets with real models (nightly / before demo) | LangSmith `evaluate()` — EVALUATION.md |
| Load smoke | 10 concurrent campaigns with FakeLLM latency 1–3 s | locust or simple asyncio script |

CI (`.github/workflows/ci.yml`): ruff, mypy, pytest (unit+contract+integration), gitleaks, OpenAPI export + `packages/api-types` diff check, eval smoke (3 rows per capability, fast tier) on main.

## 11. Observability

LangSmith (all LLM/tool calls; tags per AGENT_SYSTEM.md §11) · structured JSON logs with `run_id`, `creator_hash`, `capability` · `/health/deps` · `agent_runs` table powers the System Map stats (p50 latency, error rate, avg judge score per capability over last 24 h).

## 12. Build order (backend)

1. Skeleton: config, DB session, Alembic from `schema.sql`, auth dependency, `/health`, demo login.
2. Platform: LLM gateway (one provider first), tracing helper, `RunContext`, event emitter + SSE endpoint with replay.
3. Registry + runner + validators + judge service (with 1 rubric).
4. First three capabilities ported end-to-end: `research`, `hook`, `script` → quick mode working from Swagger.
5. Director graph (context → research → angles → interrupt → brief → hooks → script) → then fan-out nodes as capabilities land.
6. Remaining capabilities in parallel (owners), each merged only when contract tests pass.
7. Ingest pipelines (comments, analytics CSV, posts → voice; transcript text) → opportunities job.
8. Brain supervisor with tools.
9. Seed + fixtures + DEMO_MODE; evals; hardening.
