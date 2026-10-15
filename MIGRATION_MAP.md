# MIGRATION_MAP.md — Where each of the 27 projects goes

Stack column = what the **upstream** branch of `Rishi-ZAiFi/ASADI_Protosem01` contained when scanned (30 Sep 2026). Personal forks are newer (the 2–3 agents + judge + LangSmith versions), so **owners port from their fork** and correct this table in their PR.

Priority: **P0** needed for the integrated demo · **P1** next cycle · **P2** later.

| # | Project | Upstream stack observed | Extract (keep) | Becomes | UI surface | Pri |
|---|---|---|---|---|---|---|
| 01 | Content Idea Generator | Vanilla JS + Express, LangChain.js, Gemini, zod | Idea chain prompt, audience-aware idea schema | `ideation.ideas` | Discover › Ideas; Home cards | P0 |
| 02 | Content Repurposer | FastAPI + LangChain (Py) + Gemini, React/Vite; per-platform chains + orchestrator + content analysis | Platform chains (linkedin, x, instagram, youtube), content-analysis step | `repurpose.*` (canonical owner) | Campaign › Distribution | P0 |
| 03 | Hook Generator | Next.js + Gemini | Hook style taxonomy + prompt | `hook.generate` (canonical owner) | Studio › Hook block | P0 |
| 04 | Daily Content Planner | Next.js (branch also contains unrelated portfolio pages — ignore those); plan pages | Niche+goal → today's plan logic, PostCard UI | `strategy.daily_plan` | Home › Today's plan | P0 |
| 05 | Reel Script Builder | Python + LangChain + Gemini + LangSmith; local fallback | Hook/body/CTA structure prompt, duration handling, fallback generator | `script.reel_30/60` | Studio › Script | P0 |
| 06 | Clip Finder | Python FastAPI, Whisper, FFmpeg, YouTube service, Ollama/Anthropic, SQLite; tests (timestamp parser, clip validation) | Candidate scoring, timestamp validation tests, transcription + cutting | `clip.clips` (remote capability first) + ingest transcribe tool | Production › Clips; Library item | P1 (P0 with pre-transcribed demo) |
| 07 | Thumbnail Ideator | Next.js + Gemini + zod; fallback | Concept schema (composition, text overlay, emotion) | `visual.thumbnail` | Production › Thumbnails | P0 |
| 08 | Caption Assistant | Python app + static UI; Gemini/Anthropic/Ollama; LangChain | Platform caption rules, image-description → caption | `copy.caption` | Studio › Caption; Distribution | P0 |
| 09 | CTA Generator | Next.js + Anthropic + zod; Playwright e2e; unit tests | Goal-based CTA strategy, anti-repetition, e2e test setup | `copy.cta` (only CTA logic in system) | Studio › CTA block | P0 |
| 10 | Comment Analyzer | Node/Express + Gemini + SQLite; NLP pipeline; link fetcher; tests | Sentiment/theme pipeline, link fetcher (comments from URL) | `audience.analyze` | Insights › Audience | P0 |
| 11 | Comment-to-Content | FastAPI; pipeline clean→intent→cluster→gap→score→ideas→replies; LangGraph/CrewAI; Postgres/pgvector; Redis; Instagram connector | Whole pipeline design (canonical for audience ingest), gap + score logic, demo comments | `audience` pipeline + `ideation.comments_to_ideas` | Insights › Audience; Discover | P0 |
| 12 | Creator Research Assistant | Next.js + Gemini; dashboard/research/saved pages | Facts/angles/sources prompt, research page UI | `research.brief/deep` (canonical owner) | Discover › Research; Campaign research card | P0 |
| 13 | Voice Replicator | FastAPI + Alembic + Postgres/pgvector + Gemini; style/text/image analyzers, retrieval, validation | Style analyzer → VoiceProfile, retrieval of exemplars, validation service (→ `voice.score`) | `voice.*` + context_builder exemplars | Onboarding; Settings › Voice; Studio restyle | P0 |
| 14 | Podcast Assistant | Next.js + Gemini (duplicate `podcraft/` folder) | Title/description/chapters/highlights schema | `clip.podcast_pack` + `copy.title/description` | Production (podcast source) | P1 |
| 15 | Creator Workspace | React/Vite + Express + Gemini/Ollama; AI studio, trend radar, saved content | Idea→Research→Script→Published workflow, saved content UI | Library Kanban view + statuses; `library.search` | Library | P0 (statuses) |
| 16 | Content Recycler | React + Express + Mongo; recommendation engine, text similarity, CSV import, planner | Recommendation scoring + similarity, CSV import UI | `recycle.*` + analytics CSV import | Insights › Recycle; Home ♻️ | P1 (CSV import P0) |
| 17 | Brand Pitch Builder | React + Express + SQLite + Gemini/OpenAI; proposal editor, alignment score, packages, subject lines | Prompt builder, proposal editor UI, alignment score | `pitch.*` | Brand Deals | P1 |
| 18 | AI Content Director | Next.js + Anthropic; stages: research, angles, narrative, script, visuals, shot list, publishing | Stage prompts + stage stepper UI → Director node design | `director` (co-owner) + modes in research/ideation/script/visual/copy | Campaign workspace | P0 |
| 18b | AI Content Director (Guruvelah variant) | Next.js + Supabase + Gemini; trends, feedback, generations history, onboarding | Trend analysis route, feedback API, onboarding flow | Discover trends; feedback signals; onboarding | Home, Onboarding | P1 |
| 19 | Creator Second Brain | FastAPI + LangChain/LangGraph + Groq; supervisor + specialists (researcher, clip_editor, drift, promises, connections); pgvector; YouTube ingest; Whisper | Supervisor-with-agents-as-tools pattern (**platform Brain**), ingest pipeline, vector search | `brain` orchestrator + `library.*` + ingest pipeline | Library chat; Brain everywhere | P0 |
| 20 | AI Screenplay Workspace | FastAPI + Next.js + LangGraph + Chroma + Mongo | Story-bible state, continuity logic | `screenplay.*` + screenplay mode | Screenplay workspace | P1 |
| 21 | Autonomous Content Pipeline | TS monorepo: LangGraph.js (plan/refine graphs, critic), memory profile, worker, SSE run events, auth; Mongo; LangSmith | Graph structure, SSE event design, critic (→ validators), run page UI | `director` (co-owner) + `strategy.schedule` + SSE protocol | Campaign run view | P0 |
| 22 | AI Creative Producer | Empty upstream (pending) — port from fork | Pillars, 30-day strategy, adaptation from performance | `strategy.pillars/strategy_30d` + `autopilot` | Onboarding pillars; Home strategy | P0 (pillars) / P2 (autopilot) |
| 23 | Trend-to-Content Engine | Not on upstream — port from fork | Trend → creator-specific angle → hook/script/format | `ideation.trend_to_content` + `research` | Discover › Trends; Home 🔥 | P0 |
| 24 | Creator Analytics Copilot | Not on upstream — port from fork | Pattern detection, "why it worked" explanations | `performance.*` | Insights | P0 |
| 25 | AI Video Pre-Production Studio | Not on upstream — port from fork | Script → scenes → shot list → camera → props → B-roll | `visual.shot_list/full_preproduction` (canonical owner) | Production tab | P0 |
| 26 | Creator Collaboration Finder | Vanilla JS; matching engine, data.js dataset, eval.js (LangSmith) | Matching engine + seed dataset | `collab.*` + `collaborator_profiles` seed | Collaborate | P1 |
| 27 | Unified Creator AI Platform | Not on upstream — port from fork | Unified shell ideas, omnibox/routing | `intent_router` + app shell | Omnibox; layout | P0 |

## Canonical owners (to resolve overlaps)

Where several projects feed one capability, one person is **canonical owner** (final say on prompts/schema) and the others contribute modes:

| Capability | Canonical owner | Contributors |
|---|---|---|
| research | #12 | #18, #21, #23 |
| library | #19 | #15 |
| ideation | #01 | #11, #18, #23, #04 |
| audience | #11 | #10 |
| strategy | #22 | #04, #21 |
| hook | #03 | #05, #16, #18, #21 |
| script | #05 | #18, #21 |
| copy | #09 (CTA) + #08 (caption) co-own | #14, #18 |
| voice | #13 | — |
| repurpose | #02 | #21, #14 |
| visual | #25 | #07, #18 |
| clip | #06 | #14, #19 |
| performance | #24 | #22 |
| recycle | #16 | — |
| pitch | #17 | — |
| collab | #26 | — |
| screenplay | #20 | — |
| director | #18 + #21 | #22, #27 |
| brain | #19 | #27 |

## Data migration notes

| From | To |
|---|---|
| #16 Mongo `Post`, `PlanItem`, `User` | `library_items` + `performance_metrics`; `calendar_entries`; `creators` |
| #21 Mongo runs/profile | `agent_runs` + `run_events`; `voice_profiles`/`creator_strategy` |
| #20 Chroma + Mongo | `story_bibles` + `chunks` (re-embed) |
| #06, #10, #17 SQLite | seed scripts → `sources`/`comments`/`brand_pitches` |
| #11 demo_comments.json, #16 sample_instagram_data.csv, #26 data.js | **Demo seed data** (`apps/api/app/demo/fixtures/`) |
