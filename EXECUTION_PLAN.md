# EXECUTION_PLAN.md — 22 people, 27 projects, one integrated platform

## 1. Strategy in one paragraph

Freeze contracts first (schema, capability interface, SSE events, card kinds) so 22 people can work in parallel without blocking each other. A small platform squad builds the spine while everyone else ports their agent into the contract behind a FakeLLM. Integrate early on a thin vertical slice (research → hook → script in a campaign), then widen. Keep a demo-safe path (seed data + fixtures) green at all times.

## 2. Squads (everyone has two hats: capability owner + surface squad)

Hat 1 — **capability owner**: port your project per `AGENT_CONTRACT.md` into the capability listed in `MIGRATION_MAP.md` (typically 2–3 hours for single-prompt projects, longer for graph projects).
Hat 2 — **surface squad**: after your capability passes contract tests, join the squad below.

| Squad | Members (by project #) | Owns | First deliverable |
|---|---|---|---|
| **A. Platform core** | 19, 13, 11 (+ 21 for SSE) | FastAPI skeleton, DB/migrations, auth, LLM gateway, runner, validators, judge service, memory, SSE, jobs, tracing | `/health`, demo login, `run_capability` + SSE working with FakeLLM |
| **B. Orchestration** | 18, 21, 22, 27 | intent_router, Director graph, Brain supervisor, checkpoints, opportunities job | Director thin slice: context → research → angles → interrupt → hook → script |
| **C. Web shell & Create** | 09, 12, 03 | Next.js shell, auth, tokens, card registry, `useRunStream`, Create + Campaign workspace, Studio | Campaign page rendering a recorded event log |
| **D. Discover, Home & Insights UI** | 01, 04, 10, 16, 23, 24 | Home, Discover, Insights, Audience, CSV imports, Calendar | Home with seeded opportunities |
| **E. Production & Distribution** | 02, 05, 07, 08, 25, 14, 06 | Production + Distribution tabs, platform previews, clip service (remote), podcast pack | Distribution tab with 4 platform previews |
| **F. Library, Voice & Business** | 15, 17, 20, 26 | Library + Kanban, Brain chat UI, voice/onboarding screens, Brand deals, Collaborate, Screenplay | Library search + Brain chat |
| **G. Quality & Demo** (rotating 2 people from any squad after hour 5) | — | Seed data, fixtures, eval harness, calibration, Playwright, demo script, evidence pack | `evals/report.md` |

One **integration lead** (suggest #21 or #18 owner) merges to `main`, runs the integration checkpoints and owns the demo branch. One **product lead** (anyone) owns SPEC decisions and cuts scope. Adjust names to people's strengths; this is a proposal.

## 3. Timeline for today (≈ 8 working hours)

| Time | Everyone | Platform (A) | Orchestration (B) | Web (C/D/E/F) |
|---|---|---|---|---|
| **H0 – 0:45** | Read SPEC §6 + AGENT_CONTRACT; confirm your row in MIGRATION_MAP | Create monorepo, CI, `.env.example`, commit `schema.sql`, registry, `_base.py`, `_schemas/`, FakeLLM | Write `CampaignState`, event list, card kinds with C | Next.js shell, tokens, generate types from stub OpenAPI |
| **0:45** | 🔒 **CONTRACT FREEZE** — `_base.py`, `_schemas/`, event protocol, card kinds, schema.sql. Changes after this need integration-lead approval | | | |
| **0:45 – 3:00** | Port your capability (prompts, schemas, rubric, dataset ≥ 8, tests w/ FakeLLM) | Gateway (1 provider), runner, validators, judge with 2 rubrics, SSE + replay, auth, repositories | Director slice with research/hook/script; intent_router | Card registry + AiCard; `useRunStream` on recorded log; Home, Campaign overview |
| **3:00** | ✅ **Checkpoint 1**: one real campaign slice runs end-to-end (real LLM) and streams to the UI | | | |
| **3:00 – 5:00** | Capabilities merge as they pass contract tests; owners move to surface squads | Memory + ingest (comments CSV, analytics CSV, posts → voice), jobs, fallback chain, cache | Fan-out nodes (visual, copy, repurpose, schedule); Brain supervisor with tools; opportunities job | Studio, Production, Distribution, Library, Insights, Discover, System Map |
| **5:00** | ✅ **Checkpoint 2**: full Director package + Brain chat + comments & analytics imports work on the demo creator | | | |
| **5:00 – 6:30** | Fix, polish, write coverage-matrix row for your project | DEMO_MODE fixtures, seed script, rate limits, error envelope | Checkpoint UX, stale steps, insight usage in brief | Onboarding, Calendar, mobile pass, a11y pass, empty states |
| **6:30 – 7:30** | Squad G runs evals + calibration; everyone records fixtures | Deploy (Vercel + Railway + Supabase + Upstash) | Trace review in LangSmith: tags, naming | Playwright J1/J3/J4/J6 green |
| **7:30** | 🧊 **CODE FREEZE** — only demo-blocking fixes | | | |
| **7:30 – 8:00** | Demo rehearsal ×2, evidence pack, recording | | | |

If the session is shorter, keep the order and cut from the bottom of §6.

## 4. Critical path

`schema.sql + _base.py` → `run_capability + SSE` → `research, hook, script` capabilities → Director slice → card registry + run view → fan-out capabilities → seed + fixtures → deploy. Everything else hangs off this path and can slip without breaking the demo.

## 5. Git workflow

- New repo (or `creatoros` branch in the cohort repo) with the monorepo layout in BACKEND.md §2.
- `main` protected; PRs need 1 review + CI green. Integration lead merges.
- Branch names: `cap/<capability>-<desc>`, `feat/web-<area>`, `platform/<area>`, `orch/<area>`.
- `CODEOWNERS`: `apps/api/app/capabilities/<name>/` → canonical owner(s); `platform/`, `orchestration/`, `_schemas/`, `schema.sql` → squads A/B.
- Commit message: `feat(cap:copy): port #09 CTA goal strategy` — the `#NN` makes contribution traceable.
- No `.env`, no keys. gitleaks runs on every PR.

## 6. Scope cut list (cut from the bottom first)

1. Autopilot (already P2)
2. Screenplay workspace
3. Collab finder UI (keep capability in Brain tools)
4. Brand deals editor (keep generation)
5. Real media transcription (use pre-transcribed demo transcript)
6. Clip cutting
7. Calendar drag-and-drop (keep list view)
8. Stale-step propagation
**Never cut:** Director campaign with streaming, Studio editing, Repurpose, Brain chat with citations, comments & analytics imports feeding ideas, System Map, judge badges, DEMO_MODE.

## 7. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Schema churn breaks parallel work | High | High | Contract freeze at 0:45; `_schemas` changes need approval |
| Provider rate limits during demo | Med | High | Fallback chain, cache, DEMO_MODE fixtures, separate demo API keys |
| Fork code differs from upstream assumptions | High | Med | Owners correct MIGRATION_MAP in their PR; contract hides differences |
| Graph projects (19, 20, 21) take too long to port | Med | Med | Register a thin version first (single node), deepen later |
| Heavy media deps (#06) break deploy | Med | Med | Run as remote capability; demo uses pre-transcribed file |
| UI inconsistency from 20 contributors | High | Med | Card registry + AiCard shell + tokens; no project global CSS |
| Latency > 90 s for full campaign | Med | Med | Parallel fan-out, fast tier for hooks/copy, stream cards |
| Judge scores look arbitrary | Med | Med | Calibration table; show critique text, not just numbers |
| Secrets leaked in a merge | Low | High | gitleaks, `.env.example` only, review checklist |
| Evaluators test an edge case live | Med | Med | Edge cases in every dataset; graceful refusal/empty states |

## 8. Communication cadence

Kickoff 15 min (walk through SPEC §1–5 and the contract) · 10-min syncs at each checkpoint (per squad: done / blocked / next) · one shared channel for contract questions answered by squad A within 10 min · integration lead posts `main` status after each merge wave.

## 9. After today (roadmap)

| Week | Focus |
|---|---|
| +1 | Media ingest with transcription + clips (#06, #14), recycle (#16), pitch (#17), collab (#26) fully in product; eval dashboard; stale-step propagation |
| +2 | Screenplay workspace (#20); pillars + 30-day strategy UI (#22); OAuth analytics import (YouTube) |
| +3–4 | Autopilot weekly loop with approval inbox; team workspaces; publishing integrations (behind approval) |
