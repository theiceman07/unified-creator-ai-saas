# BUILD_PROMPT.md — Master prompt + phased build plan for CreatorOS

This file is written to be handed to a coding AI (Claude Code, Cursor, Windsurf, Copilot agent, etc.) that already has the CreatorOS pack in its repo: `README.md`, `SPEC.md`, `ARCHITECTURE.md`, `AGENT_SYSTEM.md`, `AGENT_CONTRACT.md`, `MIGRATION_MAP.md`, `BACKEND.md`, `FRONTEND.md`, `EVALUATION.md`, `EXECUTION_PLAN.md`, `CLAUDE.md`, `capability_registry.yaml`, `db/schema.sql`, `.env.example`.

## How to use this file

1. Put this file in the repo root next to the pack.
2. Paste **Part 1 (Master Prompt)** as the first message of the session (or into the agent's project instructions / rules file).
3. Run the **Phase prompts in Part 3** one at a time, in order. Don't paste the next phase until the current phase's **Gate** passes.
4. Use the reusable prompts in **Part 4** whenever a teammate ports a project, when something breaks, or for design review.
5. Part 2 is the visual direction. The master prompt tells the AI to follow it; you don't paste it separately.

---

# PART 1 — MASTER PROMPT (paste this first)

```
You are the lead engineer and design engineer building CreatorOS, a production-quality SaaS that unifies
27 creator-economy AI projects into one platform. You work inside this repository. The planning pack in
the repo root is the source of truth.

## Read before writing any code (in this order)
1. BUILD_PROMPT.md   (this plan; Part 2 is the visual direction you must follow)
2. CLAUDE.md          (repo conventions and non-negotiables)
3. SPEC.md            (what to build; P0 before P1 before P2)
4. ARCHITECTURE.md    (stack + ADRs — do not change decisions without asking me)
5. AGENT_SYSTEM.md    (capabilities, execution modes, Director graph, Brain, judge)
6. AGENT_CONTRACT.md  (interface every capability implements)
7. BACKEND.md, FRONTEND.md, EVALUATION.md
8. capability_registry.yaml, db/schema.sql, .env.example  (canonical; never fork their definitions)

After reading, reply with: (a) a 10-line summary of the product and architecture in your own words,
(b) any contradictions you found between files, (c) the list of phases you will execute. Then wait.

## Stack (fixed)
- Backend: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 async + asyncpg, Alembic, LangGraph
  (+ langgraph-checkpoint-postgres), langchain-core + provider packages, LangSmith, arq + Redis,
  sse-starlette, httpx, tenacity, uv, ruff, mypy, pytest.
- Database: Postgres 16 + pgvector (Supabase in cloud; pgvector/pgvector:pg16 locally).
- Frontend: Next.js 15 App Router, TypeScript strict, Tailwind CSS v4, shadcn/ui (restyled to our tokens),
  TanStack Query, Zustand, react-hook-form + zod, Tiptap, Recharts, openapi-fetch + openapi-typescript.
- Motion: GSAP 3 (ScrollTrigger, SplitText, Flip, CustomEase) + Lenis smooth scroll on marketing pages;
  Framer Motion only for small in-app state transitions. Three.js only for the one hero moment.
- Tests: pytest, Vitest + Testing Library, Playwright.

## Non-negotiables
- All model calls go through platform/llm/gateway.py. All capability execution goes through
  orchestration/runner.run_capability. No provider SDKs inside capabilities/.
- Every repository query is scoped by creator_id.
- Structured outputs via Pydantic; never regex JSON out of model text.
- Untrusted text (comments, transcripts, web pages, uploads) is wrapped as <data> in prompts.
- Never auto-publish to social platforms. Never commit secrets — only .env.example.
- DEMO_MODE must always work end to end with seeded data and recorded fixtures, with zero API keys.
- Every AI output in the UI is editable and shows: which capability made it, origin project numbers,
  judge score, and a "why" line.
- Follow Part 2 of BUILD_PROMPT.md for all visual decisions. Do not fall back to default shadcn styling,
  purple gradients, glassmorphism, or a grid of generator-tool cards.

## How you work
- One phase at a time. At the start of a phase, write a short plan (files to create/change, risks).
  At the end, run the phase's Gate commands and report: what was built, Gate results (paste output
  summaries), deviations from the pack and why, and TODOs left as `TODO(P1):` comments.
- Prefer the smallest implementation that satisfies the P0 acceptance criteria in SPEC.md §7.
- Write tests alongside code, not after. Keep CI green at every commit.
- Commit in small logical commits: `feat(api): ...`, `feat(web): ...`, `feat(cap:hook): ...`, `chore: ...`.
- If two pack files disagree, prefer: db/schema.sql and capability_registry.yaml > AGENT_CONTRACT.md >
  BACKEND.md/FRONTEND.md > SPEC.md > others. Tell me about the conflict.
- Ask me only when a decision changes the architecture, the data model, or scope. Otherwise decide,
  note the decision in docs/DECISIONS.md, and continue.
- When you build UI, take Playwright screenshots at 1440px and 390px, review them against Part 2's
  checklist, fix what fails, and tell me what you changed.
```

---

# PART 2 — VISUAL DIRECTION (inspired by bymonolog.com)

## 2.1 What we're taking from the reference — and what we're not

The reference is an award-winning studio site: warm stone/near-black palette with almost no color, enormous tightly-set grotesk headlines, small monospaced parenthetical labels, full-bleed sections that flip between light and dark, looping video thumbnails beside a single big outcome number, a numbered process told as a scroll story, smooth inertial scrolling, line-by-line text reveals, and a huge closing call to action.

**Take:** the restraint, the palette logic, the type scale and tracking, the section-theme flipping, the mono micro-labels, the scroll storytelling, the motion quality, the editorial confidence.
**Do not take:** their logo, copy, photography, videos, client names, testimonials, or font files. Their fonts (Khteka, Animo, Suisse Mono) are commercial — use them only if the team holds a license, otherwise use the substitutes below. Every word and asset in CreatorOS is our own.

**Honesty rule for marketing content:** we have no customers yet. No fake testimonials, fake logos or fake growth metrics. Replace the reference's "client stories" with **"Output stories"**: real demo runs ("One 20-minute podcast → 5 shorts, 3 reels, 1 thread, 8 quote posts") clearly labelled as demo output, and replace the logo wall with **"Built from 27 projects by 22 builders"** listing the original project names.

## 2.2 Design tokens

Palette (taken from the reference's warm neutral scale; no chromatic brand color):

```css
:root {
  /* ink (dark) */
  --ink-900: #080807;   /* page background in dark theme, text in light theme */
  --ink-800: #181715;   /* raised surface / card in dark theme */
  --ink-700: #393632;   /* borders on dark, pressed states */
  --ink-600: #524d47;   /* secondary text on light */
  --ink-500: #6b645c;   /* muted text */
  --ink-400: #938f8a;   /* placeholder, disabled, meta on dark */
  /* paper (light) */
  --paper-100: #e8e8e3; /* text on dark; brightest paper */
  --paper-200: #ddddd5; /* editor paper surface */
  --paper-300: #d1d1c7; /* page background in light theme */
  --paper-400: #bfbfb1; /* borders on light, primary button on dark */

  /* functional signals — used ONLY for judge badges, run status, validation. Muted to sit in the palette. */
  --signal-pass: #7d9471;
  --signal-warn: #b8954f;
  --signal-fail: #a5493d;
  --signal-live: var(--paper-100);  /* running state = pulsing paper, not a color */

  --radius-sm: 0.15rem;   /* inputs, chips, buttons */
  --radius-md: 1rem;      /* media, large panels */
  --radius-round: 100vw;  /* pills, avatar, status dots */
  --border: 0.094rem;     /* ~1.5px hairline used everywhere */
}
```

Theme rules: two themes implemented as section/surface classes, not just a global toggle — `.theme-dark` (bg `--ink-900`, text `--paper-100`, border `--ink-700`) and `.theme-light` (bg `--paper-300`, text `--ink-900`, border `--paper-400`). Marketing sections alternate them. The app shell is dark; **writing surfaces (script, captions, posts, pitches) render on paper (`--paper-200`) like a page on a dark desk** — this is the product's signature: generated work looks like a document you own, the machinery around it stays dark and quiet.

Typography:

| Role | Reference face | Free substitute | Use |
|---|---|---|---|
| Primary (UI + body + headlines) | Khteka | **Schibsted Grotesk** (variable) | Everything by default |
| Display (only the biggest moments) | Animo | **Anybody** (variable, width axis) | Landing hero, closing CTA, campaign title on completion |
| Mono micro-labels | Suisse Mono | **Geist Mono** | Parenthetical labels, timestamps, counters, origin chips, token/cost readouts |

Fluid type scale (clamp between 20rem and 100rem viewport, as in the reference):

```css
--fs-display:     clamp(5rem, 3.875rem + 5.625vw, 9.25rem);   /* lh .9, ls -.03em */
--fs-display-sm:  clamp(4rem, 2.95rem + 5.25vw, 8rem);        /* lh .9, ls -.03em */
--fs-h1:          clamp(3.5rem, 3.125rem + 1.875vw, 6rem);    /* lh 1,  ls -.03em */
--fs-h2:          clamp(3rem, 2.5625rem + 2.1875vw, 4.75rem); /* lh 1,  ls -.015em */
--fs-h3:          clamp(2rem, 1.625rem + 1.875vw, 3.5rem);    /* lh 1.1, ls -.015em */
--fs-h4:          clamp(1.5rem, 1.375rem + .625vw, 2rem);     /* lh 1.1, ls -.01em */
--fs-text-lg:     clamp(1.125rem, 1.09rem + .156vw, 1.25rem); /* lh 1.2, ls -.01em */
--fs-text:        clamp(1rem, .97rem + .156vw, 1.125rem);     /* lh 1.5 body / 1.2 UI */
--fs-text-sm:     .875rem;
--fs-label:       clamp(.65rem, .625rem + .125vw, .75rem);    /* mono, lh 1.2 */
```
Weights: 500 as the default weight for UI and headlines (the reference sets medium, not bold); 700 only for numbers that are the point (scores, outcome metrics). Body line length ≤ 70ch.

In-app scale is calmer: page titles use `--fs-h3` max; `--fs-display` appears in the app only on the Home greeting/omnibox and the campaign-complete moment.

Spacing: fluid steps `--space-1 … --space-8` (0.375→0.5rem up to 2.5→4rem) and section spacing `--section-sm/md/lg` (3→5rem, 4→7rem, 5.5→10rem). Site margin `clamp(.75rem, …, 1.75rem)`, gutter 1rem, 12-column grid on marketing, 12-column with fixed sidebar in app.

## 2.3 Signature elements (translated for CreatorOS)

| Reference device | CreatorOS version |
|---|---|
| Parenthetical mono labels "(scroll to explore)" | Mono labels in parentheses, sentence case: `(scroll to explore)`, `(running · 00:14)`, `(from #09 CTA Generator)`. Never all caps |
| Huge split-line headline reveal on load | Hero: "One idea. / Every platform. / Your voice." — lines reveal with GSAP SplitText (mask + y 100% → 0, stagger .08, CustomEase) once on load |
| Marquee of words "listen create obsess inspire" | Loop marquee: "discover  decide  create  produce  repurpose  publish  analyze  learn" — slow, pauses on hover, stops under reduced motion |
| Numbered process told as a pinned scroll story with video | **The creator loop** is a real sequence, so numbering is earned: 9 stages pinned with ScrollTrigger; each step shows a short looping screen recording of that part of the product |
| Case studies: looping video + one big outcome number | **Output stories** (demo, labelled): looping capture of a run + one big honest number ("1 podcast → 17 assets in 84 s") |
| Logo wall | "Built from 27 projects" grid: project number in mono + name, hover shows which capability it became |
| FAQ accordion | FAQ: what it does, which platforms, does it post for me (no), how it learns my voice, data privacy, pricing |
| Giant closing CTA + live clock + "ask AI about us" links | Closing CTA "Turn one idea / into a week / of content" with a single "Start with a demo creator" button; footer with live clock in the user's timezone and "Ask Claude/ChatGPT/Gemini about CreatorOS" prefilled links |
| Full-screen menu overlay | Marketing nav opens a full-screen ink overlay with large links; app uses a fixed sidebar instead |
| Theme flips between sections | Light hero → dark loop story → light output stories → dark "27 projects" → light FAQ → dark CTA/footer |

## 2.4 Motion rules

- Lenis smooth scroll on marketing pages only (never inside the app — app scrolling must be native and instant).
- One orchestrated moment per page. Landing: hero line reveal. App Home: the greeting resolves and the omnibox caret appears. Campaign run: cards slot into the timeline as steps complete (GSAP Flip from skeleton to card) — this is the product's core motion.
- Durations 0.4–0.9 s on marketing, 0.15–0.3 s in app. One custom ease token: `CustomEase.create("creator", "0.65, 0, 0.35, 1")`.
- `prefers-reduced-motion`: disable Lenis, marquee, SplitText, pinning; show final states.
- No sound (the reference has optional audio; skip it). No cursor followers. No hover animations on every card.

## 2.5 App screens in this language (wireframes)

**Home (dark shell)**
```
┌──────────┬──────────────────────────────────────────────────────────────────┐
│ CreatorOS│ (thursday · 09:12)                                               │
│          │                                                                   │
│ Home     │  Good morning, Priya.                       ← --fs-display-sm    │
│ Discover │  What are you thinking about?_              ← omnibox, paper text │
│ Create   │  ─────────────────────────────────────────────────────────────── │
│ Library  │  (today's opportunities)                                          │
│ Insights │  Trending        From your audience   From your analytics   …    │
│          │  AI agents for   "Agent vs chatbot?"  30–60 s explainers          │
│ ──────── │  beginners       asked 14 times        outperform 2.1×            │
│ Calendar │  (potential 82)  (from #10 #11)        (from #24)                 │
│ Collab   │  Create campaign Create campaign       Use in next campaign       │
│ Deals    │  ─────────────────────────────────────────────────────────────── │
│ System   │  (today's plan)  Reel · LinkedIn post · Story                     │
└──────────┴──────────────────────────────────────────────────────────────────┘
```
Opportunity "cards" are not boxed cards: they're columns separated by hairline rules, mono label on top, title in `--fs-h4`, rationale in muted text, one text button.

**Campaign workspace during a run**
```
┌──────────┬───────────────────────────────────────────────┬──────────────────┐
│ sidebar  │ AI agents for beginner developers   (score 4.3)│ (run · 00:41)    │
│          │ Audience growth · Reels → Shorts, LinkedIn     │ ● context   0.4s │
│          │ [Overview][Studio][Production][Distribution]   │ ● research  6.1s │
│          │ ┌───────────── paper surface ───────────────┐  │   #12 #18 #21    │
│          │ │ (hook 1 of 3 · judge 4.6)                 │  │ ● angles    3.2s │
│          │ │ ChatGPT isn't an agent. Here's the        │  │ ● hooks     2.8s │
│          │ │ difference in 45 seconds.                 │  │ ◌ script  …      │
│          │ │                                           │  │ ○ shot list      │
│          │ │ (script · 142 / 150 words · ~57 s)        │  │ ○ thumbnails     │
│          │ │ HOOK  …                                   │  │ ○ copy + CTA     │
│          │ │ BODY  …                                   │  │ ○ platforms      │
│          │ └───────────────────────────────────────────┘  │ (view trace ↗)   │
└──────────┴───────────────────────────────────────────────┴──────────────────┘
```

## 2.6 Design review checklist (the AI runs this on every UI phase)

- [ ] No default shadcn look: radii, borders, colors all come from tokens.
- [ ] Only the neutral palette; signal colors appear only on judge/status/validation.
- [ ] Headlines medium weight, tight tracking; body ≤ 70ch; labels mono, parenthetical, sentence case.
- [ ] Generated writing renders on paper surfaces; chrome stays dark.
- [ ] No grid of identical rounded cards with shadows; separation by hairlines and spacing.
- [ ] Numbered markers only where content is a real sequence (the loop, the run steps).
- [ ] One orchestrated motion moment per page; reduced motion respected.
- [ ] Contrast ≥ 4.5:1 for text (check `--ink-400` on `--ink-900` — use it only for ≥ 18px or non-essential meta).
- [ ] Visible focus ring (2px `--paper-100` outline on dark, `--ink-900` on light, 2px offset).
- [ ] 390px layout works: sidebar → bottom nav, run timeline → bottom sheet.
- [ ] No borrowed copy, photos, logos or fonts from the reference.

---

# PART 3 — PHASED BUILD PLAN (paste one phase at a time)

Each phase lists **Prompt** (paste it), **Deliverables**, and **Gate** (must pass before the next phase). Phases 4–5 (design + landing) can run in parallel with 1–3 if two agents/people are working.

### Phase 0 — Bootstrap the monorepo

**Prompt**
```
Phase 0. Create the monorepo exactly as laid out in BACKEND.md §2 (apps/api, apps/web, packages/api-types,
db/, evals/, docs/). Set up:
- uv-managed Python project in apps/api with the dependencies from BACKEND.md §1 and the stack in the master prompt.
- pnpm workspace; Next.js 15 app in apps/web with TypeScript strict, Tailwind v4, ESLint, Prettier.
- docker-compose.yml with pgvector/pgvector:pg16 and redis:7; api and worker services built from apps/api;
  web service optional.
- Makefile with the targets in CLAUDE.md (dev, migrate, seed, test, e2e, types, evals, lint).
- .github/workflows/ci.yml: ruff, mypy, pytest, pnpm lint/typecheck/test, gitleaks, OpenAPI types diff check.
- .env.example copied from the pack; .gitignore covers .env*, node_modules, .venv, data, recordings.
- docs/DECISIONS.md (empty log) and a root README quickstart (< 10 steps from clone to running demo).
Do not write product features yet.
```
**Deliverables:** runnable empty api (`/health`) and web (blank page), compose, Makefile, CI.
**Gate:** `make dev` starts db, redis, api, web · `curl localhost:8000/health` → `{"ok":true}` · `make lint` and `make test` pass · CI green on first push.

### Phase 1 — Data layer and backend spine

**Prompt**
```
Phase 1. Implement the data layer and spine:
1. Alembic initial migration that applies db/schema.sql verbatim (extensions, enums, tables, indexes,
   match_chunks function, RLS pattern). Add SQLAlchemy 2 models for every table.
2. Repositories in app/db/repositories/ — every method requires creator_id. Add an integration test
   proving creator A cannot read creator B's campaign.
3. core/config.py (pydantic-settings from .env.example), core/errors.py (error envelope and codes from
   BACKEND.md §4), core/logging.py (JSON logs with run_id/creator_hash).
4. Auth: Supabase JWT verification dependency current_creator(); DEMO_MODE-only POST /v1/demo/login that
   returns a token for the seeded demo creator.
5. Routers for /health, /health/deps, /me, /campaigns CRUD, /assets read/patch (with asset_versions).
6. A FakeLLM implementation of the gateway interface (returns schema-valid objects generated from the
   Pydantic schema with deterministic content) — used by all tests.
Write tests (unit + integration with a pgvector testcontainer).
```
**Gate:** `make migrate` clean on empty DB · `pytest` green including the cross-creator isolation test · Swagger shows the routers · demo login returns a token that works on `/v1/me`.

### Phase 2 — Agent platform: gateway, runner, judge, events, tracing

**Prompt**
```
Phase 2. Build the agent platform exactly per BACKEND.md §3 and AGENT_SYSTEM.md §7–§11:
1. platform/llm: gateway with tiers parsed from LLM_TIER_* env (provider:model lists), fallback chain,
   circuit breaker, per-tier timeouts, structured output with one JSON-repair retry, Redis cache with
   llm_cache table fallback, usage accounting. Providers: gemini, anthropic, openai, groq (skip any
   without a key). embed() batches 100 and enforces EMBEDDING_DIM.
2. capabilities/_base.py and capabilities/_schemas/ exactly as AGENT_CONTRACT.md §1 (Capability,
   RunContext, Card, Citation, CapabilityResult) plus shared models Hook, Script, PlatformPost,
   PlatformLimits, ResearchBrief, CreatorContext.
3. orchestration/registry.py loads capability_registry.yaml and validates that every listed capability
   class exists (allow "not yet implemented" stubs that raise a clear error).
4. platform/validators: platform limits, word budget (~150 wpm), banned words, citation ids, CTA
   repetition (embedding cosine), timestamp range, schema.
5. platform/judge: rubric loader for app/rubrics/*.yaml, judge(), pairwise() tournament, policies
   (always/sample/never per mode), writes judge_scores + LangSmith feedback.
6. orchestration/runner.run_capability exactly as BACKEND.md §3.3.
7. orchestration/events.py + GET /v1/runs/{id}/events SSE with the event types in BACKEND.md §5,
   persisted to run_events, Last-Event-ID replay, 15s heartbeat. Redis pub/sub with in-process fallback.
8. platform/tracing.py: LangSmith run naming, tags (mode:, cap:, origin:NN), metadata, feedback helper.
9. platform/context/builder.py building CreatorContext with token budget.
10. Contract test suite that parametrizes over the registry (AGENT_CONTRACT.md §7 checks).
```
**Gate:** unit tests for gateway fallback (simulate provider failure), cache hit, validators, judge math · SSE test: a fake run emits events and a reconnect with Last-Event-ID replays the rest · LangSmith shows a trace tree for a FakeLLM run when `LANGSMITH_TRACING=true`.

### Phase 3 — First capabilities and the Director slice

**Prompt**
```
Phase 3. Implement capabilities research, hook and script per AGENT_CONTRACT.md §3 (folder layout,
prompts/<mode>.v1.md with the prompt standard in AGENT_SYSTEM.md §12, rubric.yaml, dataset.jsonl with
≥ 8 rows incl. 3 edge cases, fixtures.json, FakeLLM tests). Use the origin projects in
MIGRATION_MAP.md for prompt content: research ← #12/#18/#21, hook ← #03 style taxonomy, script ← #05.
Then:
- POST /v1/capabilities/{name}/invoke (quick mode, sync and SSE variants) and GET /v1/capabilities.
- Director graph (orchestration/director) with CampaignState from AGENT_SYSTEM.md §5:
  load_context → (research ∥ library stub ∥ audience stub) → ideation.angles (temporary minimal
  implementation) → interrupt(choose_angle) → strategy brief (minimal) → hook (best-of-N pairwise) →
  script (judge + one repair). Use langgraph-checkpoint-postgres; POST /campaigns/{id}/runs,
  POST /runs/{id}/resume, POST /runs/{id}/cancel. Run graphs in the arq worker.
- intent_router with deterministic overrides + structured classification; POST /v1/intents.
Nodes not yet implemented must emit node.failed with retryable=false and let the graph continue.
```
**Gate:** with a real `GEMINI_API_KEY`: `POST /v1/intents {"text":"I want to explain AI agents to beginner developers"}` → route campaign · starting a run streams research → angles → checkpoint; resume → hooks → script, all persisted as assets with judge scores · same flow passes with FakeLLM in pytest · LangSmith shows one root trace with child runs tagged `origin:12`, `origin:03`, `origin:05`.

### Phase 4 — Design system and app shell

**Prompt**
```
Phase 4. Build the design system and the authenticated app shell following BUILD_PROMPT.md Part 2
exactly. Before coding, write docs/DESIGN.md: final tokens, font choices (license check), the theme
rules (dark chrome, paper writing surfaces), and the motion rules. Then:
- Tokens as CSS variables + Tailwind v4 theme mapping; .theme-dark and .theme-light surface classes.
- Fonts via next/font (Schibsted Grotesk, Anybody, Geist Mono unless licensed originals are provided).
- Restyle shadcn primitives (Button, Input, Textarea, Select, Dialog, Sheet, Tabs, Tooltip, Toast,
  DropdownMenu, Accordion) to tokens. Buttons: primary = paper on ink, secondary = hairline outline,
  text button = underline on hover. Radius --radius-sm.
- Components: MonoLabel "(…)", Hairline, Counter, OriginChip (#09 → links to /system), JudgeBadge
  (score + pass/warn/fail signal + critique tooltip), StatusDot (live pulse), PaperSurface, EmptyState.
- App shell: fixed sidebar (Home, Discover, Create, Library, Insights | Calendar, Collaborate, Brand deals,
  System, Settings), top bar with ⌘K omnibox trigger, RunDrawer (right panel; bottom sheet < 768px),
  mobile bottom nav. Supabase auth + "Try demo" login. Generated API types in packages/api-types.
- A /dev/kitchen-sink route showing every component in both themes (excluded from prod build).
Take screenshots at 1440 and 390 of the kitchen sink and shell, run the Part 2.6 checklist, fix issues.
```
**Gate:** kitchen sink renders all components in both themes · axe (Playwright + @axe-core/playwright) has no serious violations · Lighthouse accessibility ≥ 95 on the shell · checklist report included.

### Phase 5 — Marketing landing page (the bymonolog-inspired showcase)

**Prompt**
```
Phase 5. Build the public landing page at / following BUILD_PROMPT.md Part 2 (§2.3 signature elements,
§2.4 motion). Sections in order, alternating themes:
1. Light — Nav (wordmark "CreatorOS", links: Product, How it works, Built from 27, FAQ; "Try the demo"
   button; full-screen ink menu overlay on mobile). Hero headline "One idea. / Every platform. /
   Your voice." in --fs-display with SplitText line reveal; sub-line "An AI creative operating system
   that turns one idea into a complete, on-voice content campaign — and learns from what performs.";
   primary "Start with a demo creator", secondary "(scroll to explore)". Behind the headline, the one
   Three.js moment: a slow ring of 9 stage labels (the loop) in paper on light, static under reduced motion.
2. Dark — Marquee of the loop verbs. Then the problem statement in --fs-h2 (creators juggle 10 tools
   that forget who they are).
3. Dark, pinned — "The loop" scroll story: 9 numbered stages (Discover … Learn); each step shows a
   looping muted screen capture (placeholder MP4/WebM slots in /public/loops/, with poster images)
   and 2 lines of copy. Use ScrollTrigger pinning on ≥ 1024px; stacked list on mobile.
4. Light — Output stories: 3 rows, each a looping capture + one big honest number + one line
   (e.g. "1 podcast → 17 assets in 84 s"), every row labelled "(demo output)".
5. Dark — "Built from 27 projects by 22 builders": a grid of 27 rows, mono number + project name;
   hover/focus reveals the capability it became (data from capability_registry.yaml at build time).
6. Light — How it remembers you: voice profile, content library, insights — three short columns with hairlines.
7. Light — FAQ accordion (6 questions from Part 2.3).
8. Dark — Closing CTA "Turn one idea / into a week / of content" in --fs-display with one button,
   then footer: nav, live clock (user's timezone), "Ask Claude / ChatGPT / Gemini about CreatorOS"
   links with prefilled questions, © line.
Rules: Lenis only on this page; GSAP registered client-side only; all copy original; no fake
testimonials/logos/metrics; reduced motion shows final states; LCP < 2.5s (lazy-load Three.js and
videos below the fold; hero text renders server-side before animation).
```
**Gate:** Lighthouse performance ≥ 85, accessibility ≥ 95 on mobile emulation · reduced-motion run shows no animation · screenshots at 1440/390 attached with checklist results · no external assets from the reference site in the bundle.

### Phase 6 — Home, omnibox and the live campaign workspace

**Prompt**
```
Phase 6. Build the core app experience (FRONTEND.md §3.1–3.2, §4):
- Card registry (components/cards/registry.ts) and AiCard shell (origin chip, judge badge, why line,
  actions: edit, regenerate, copy, history). Generic fallback card for unknown kinds.
- useRunStream(runId): EventSource with Last-Event-ID reconnect, backoff, heartbeat timeout; reducer to
  {plan, steps, cards, checkpoint, summary}; writes assets into the TanStack Query cache; aria-live
  announcements. Unit-test the reducer with a recorded event log (save one from Phase 3 to
  apps/web/test/fixtures/run-events.json).
- Home: greeting, omnibox (text + attachment + example chips), opportunities row (hairline columns,
  not boxed cards), today's plan, continue-working. Omnibox calls POST /v1/intents and routes.
- Create page and Campaign workspace with tabs; Overview shows the run timeline in the RunDrawer and
  cards filling in (GSAP Flip from skeleton to card — the app's one orchestrated motion), the
  choose_angle checkpoint as inline angle columns with "Use this angle" and "Edit brief", completion
  banner with package score, asset count, time, cost, "View trace".
Writing assets (hooks, script, captions) render on PaperSurface.
```
**Gate:** Playwright J1 (SPEC §7) passes against the API in DEMO_MODE: omnibox → campaign → checkpoint → package with judge badges · page refresh mid-run resumes the timeline · screenshots + checklist.

### Phase 7 — Port the remaining capabilities and complete the Director

**Prompt**
```
Phase 7. Implement the remaining capabilities from capability_registry.yaml using the per-capability
porting prompt (BUILD_PROMPT.md Part 4.1) for each, in this order (P0 first): ideation, copy (caption
+ cta + title/description/hashtags), voice, repurpose, visual, strategy, audience, library,
performance, then P1: recycle, clip (remote-capability adapter + local stub), pitch, collab, screenplay.
For each, read MIGRATION_MAP.md for the origin projects and, if I provide fork paths/URLs, extract their
prompts and logic. Then complete the Director: parallel fan-out (visual.shot_list ∥ visual.thumbnail ∥
copy.full_pack ∥ repurpose.all with repurpose calling copy.cta via ctx.call_capability), strategy.schedule
→ calendar_entries, final_review, library write-back, insight usage ("applied_count"). Voice: score
script + primary copy and restyle once if < 3.5.
```
**Gate:** contract tests green for all 17 · each capability's dataset eval mean ≥ 3.6 with 0 validator failures (EVALUATION.md §2) · full campaign p50 < 90 s over 5 runs with real keys · LLM calls per campaign ≤ 18 (count in LangSmith).

### Phase 8 — Studio, Production, Distribution

**Prompt**
```
Phase 8. Build the campaign tabs (FRONTEND.md §3.3–3.5):
- Studio: Tiptap block editor on paper — Title, Hook (selected + alternates, "10 more"), Script with
  HOOK/BODY/CTA section marks and live word count vs budget + estimated duration, CTA (goal selector,
  variants), Caption (per-platform counters), Voice match chip + "Restyle to my voice". Block toolbar:
  Regenerate, Shorten, Expand, Restyle, Copy, History. Debounced autosave → PATCH assets (versions).
  Studio actions call POST /assets/{id}/regenerate (studio mode).
- Production: scene table (time, visual, B-roll, on-screen text, camera, props); 3 thumbnail concepts
  rendered as CSS wireframes (focal element block + overlay text + emotion note); clips list if a
  source exists.
- Distribution: native-looking previews for LinkedIn, X thread (per-tweet counters), Instagram caption,
  YouTube description, newsletter — all in our tokens (suggest the platform by layout, not by copying
  its branding). Copy/edit/regenerate per platform; char counters turn --signal-warn near the limit.
- Export campaign as Markdown.
```
**Gate:** Vitest: every card kind renders from fixtures · Playwright: edit a script line → version saved → restore works · regenerate shows new judge score · keyboard-only pass through Studio.

### Phase 9 — Ingest, Library + Brain, Audience, Insights, Discover

**Prompt**
```
Phase 9. Build ingestion and the intelligence surfaces (SPEC §6.4, 6.9–6.11; BACKEND.md §6):
- POST /v1/sources (upload/URL/YouTube/transcript/CSV) → arq jobs: import_comments (batch classify 50,
  embed, cluster, label, opportunities), import_analytics (normalize CSV, metrics, performance.patterns
  → insights, opportunities), posts → voice.build_profile, transcripts → chunks (+ clip.clips when
  available). Progress events on the same SSE protocol.
- refresh_opportunities job (after imports + nightly) feeding Home.
- Brain supervisor (AGENT_SYSTEM.md §6) with specialists-as-tools and start_campaign meta-tool;
  POST /brain/threads/{id}/messages streams tokens + cards.
- Web: Library (hybrid search, filters, Kanban statuses), Library chat with citation chips that open
  the item at the timestamp, item detail; Insights (KPI row, interpreted insights with evidence charts,
  "What should I make next?", recycle candidates, audience report with "Turn into content"); Discover
  tabs (Ideas, Trends, Research, Audience questions).
Use demo data from MIGRATION_MAP.md "Data migration notes" for fixtures.
```
**Gate:** Playwright J3 (comments → ideas), J4 (analytics → insight used in the next campaign brief), J6 (brain answer with citation) pass · 500 comments processed < 30 s · prompt-injection comment test from EVALUATION.md §7 passes.

### Phase 10 — System Map, onboarding, calendar, business, screenplay

**Prompt**
```
Phase 10. Build:
- /system (FRONTEND.md §3.8): orchestrators → 17 capabilities → platform services diagram (SVG built
  from capability_registry.yaml), each tile with modes, origin projects, 24h runs, p50 latency, avg
  judge score, status; "Try it" quick-mode panel; recent traces; table of all 27 projects → product
  location; coverage-matrix "Run this test" buttons (EVALUATION.md §6).
- Onboarding (4 steps + voice profile reveal as editable chips, "Use demo creator").
- Calendar (week/month list, reschedule, .ics export).
- Brand deals (pitch builder/editor with alignment score), Collaborate (filters → matches with
  overlap rationale and collab ideas), Screenplay workspace (story bible + scene editor + continuity
  warnings) — P1 scope; cut in the order of EXECUTION_PLAN.md §6 if time runs out.
- Settings: profile, voice versions, pillars, data imports, provider status from /health/deps.
```
**Gate:** /system shows all 17 capabilities with live stats after a seeded run set · all 27 projects mapped · onboarding → first campaign < 5 min in a timed run.

### Phase 11 — Demo mode, seed, evals, tests

**Prompt**
```
Phase 11. Make evaluation bulletproof (EVALUATION.md, BACKEND.md §9):
- app/demo/seed.py: demo creator with 25 posts, 1 podcast transcript, 500 comments, 60 days of
  analytics for 30 items, pillars, voice v1, 2 completed campaigns, opportunities.
- fixtures.json for every capability recorded from real runs; runner serves them when DEMO_MODE and
  providers fail, labelled "(offline draft)".
- evals/: sync datasets to LangSmith, run all capability suites + e2e_campaign, write evals/report.md
  (mean score, pass rate, validator failures, p50/p95 latency, cost per capability) and
  evals/calibration.md (judge vs two human raters on 20 samples for hook, script, copy, repurpose,
  research; Spearman ρ).
- /admin/evals page reading the latest report.
- Full Playwright suite (J1, J3, J4, J6, /system) on desktop + mobile; red-team list from
  EVALUATION.md §7 as automated tests where possible.
```
**Gate:** with ALL API keys removed and DEMO_MODE=true, the full demo script (EVALUATION.md §8) runs without an error screen · eval report generated · CI green.

### Phase 12 — Hardening, performance, deploy, evidence pack

**Prompt**
```
Phase 12. Production readiness:
- Rate limits, upload limits, error envelope everywhere, empty/error states for every page written
  in the interface voice (say what happened and what to do).
- Performance: route bundle < 250 KB gz, lazy Tiptap/Recharts/Three/GSAP, image/video optimization,
  Home LCP < 2.5 s. Accessibility pass (axe clean, keyboard paths, focus order, reduced motion).
- Deploy: web → Vercel; api + worker → Railway/Render (Dockerfile); Supabase (db, auth, storage) with
  migrations; Upstash Redis; LangSmith project creatoros-demo. Separate demo API keys.
- Evidence pack (EVALUATION.md §9): architecture diagram PNG from ARCHITECTURE.md, LangSmith links,
  eval + calibration reports, coverage matrix, CI badge, README quickstart verified on a clean machine,
  docs/DEMO.md with the 7-minute script and backups.
Run the Part 2.6 design checklist one final time across every page and report.
```
**Gate:** live URL passes the demo script twice in a row · Lighthouse (mobile) ≥ 85 perf / ≥ 95 a11y on landing, Home and Campaign · gitleaks clean · evidence pack complete.

---

# PART 4 — REUSABLE PROMPTS

### 4.1 Port one project into a capability (each teammate uses this)

```
Port project #<NN> "<Project Name>" into CreatorOS.
Source code: <path or URL of my fork + branch>.
Target (from MIGRATION_MAP.md): capability `<name>`, modes <modes>, UI surface <surface>.
1. Read AGENT_CONTRACT.md fully and my row in MIGRATION_MAP.md.
2. Inventory my project: list its agents, prompts, schemas, judge criteria, fallbacks, and UI pieces.
   Tell me what maps to which mode and what will be dropped (own server/DB/SDK calls/judge/auth).
3. Implement apps/api/app/capabilities/<name>/ per AGENT_CONTRACT.md §3 — keep my prompt wording and
   logic, convert schemas to Pydantic (reuse capabilities/_schemas where possible), move my judge
   criteria into rubric.yaml, write dataset.jsonl (≥ 8 rows, ≥ 3 edge cases), FakeLLM tests,
   fixtures.json, README.
4. Add/verify the card component for my card kind in apps/web/components/cards/, porting the best
   parts of my original UI but restyled to BUILD_PROMPT.md Part 2 tokens.
5. Run: contract tests, my unit tests, quick-mode invoke with the demo creator, and the LangSmith eval
   on my dataset. Report scores. Make sure traces carry tag origin:<NN>.
6. Update my MIGRATION_MAP.md row if the fork differs from what it says.
Definition of done = AGENT_CONTRACT.md §7.
```

### 4.2 Debug something broken

```
Something is broken: <symptom, steps, run_id / trace link / error text>.
Reproduce it with a failing test first. Then find the root cause (show the evidence: logs, trace,
event log). Fix the cause, not the symptom. Keep the test. Tell me: cause, fix, test added, and
anything else that could break the same way.
```

### 4.3 Design review of a screen

```
Review <route> against BUILD_PROMPT.md Part 2. Take Playwright screenshots at 1440 and 390 in the
relevant theme(s). Go through the 2.6 checklist item by item with pass/fail and evidence. Then list
the 3 changes that would most improve it (not more), make them, re-screenshot, and show before/after.
```

### 4.4 Add a new card kind or schema field

```
I need <field / card kind> for <capability>. Update in one commit: capabilities/_schemas (or the
capability schemas), capability_registry.yaml (if card kind), db expectations (if persisted), the web
card registry + component, OpenAPI types (make types), fixtures, and tests. Confirm nothing else
references the old shape.
```

### 4.5 Pre-evaluation check

```
Run the full pre-evaluation check: CI, Playwright suite (desktop + mobile), evals (report diff vs last
run), demo script with DEMO_MODE and no keys, demo script with real keys on the deployed URL, the
Part 2.6 checklist on landing/Home/Campaign/System, gitleaks. Give me a go/no-go table with any
blocking issues and the fix for each.
```

---

# PART 5 — Order of work if several people/agents run in parallel

| Track | Phases | Starts when |
|---|---|---|
| Backend spine | 0 → 1 → 2 → 3 | immediately |
| Design + marketing | 4 → 5 | after Phase 0 |
| App UI | 6 → 8 → 10 | after Phase 4 + a recorded event log from Phase 3 (or a hand-written mock log) |
| Capability owners (22 people) | 4.1 prompt, then 7 | after Phase 2 (contract frozen) |
| Intelligence | 9 | after Phase 3 |
| Quality | 11 → 12 | after Phase 7 starts landing capabilities |

Freeze `_base.py`, `_schemas/`, the SSE event list and card kinds at the end of Phase 2. After that, any change goes through prompt 4.4.
