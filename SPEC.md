# SPEC.md — CreatorOS

**One line:** CreatorOS is an AI creative operating system that takes a creator from idea → content → publishing → analytics → next idea in one workspace, built by unifying the cohort's 27 creator-economy agents into a single product.

**Product loop:** Discover → Decide → Create → Produce → Repurpose → Publish → Analyze → Learn → (back to Discover)

**Status:** v1.0 build spec · Owner: whole cohort · Companion docs: `ARCHITECTURE.md`, `AGENT_SYSTEM.md`, `BACKEND.md`, `FRONTEND.md`, `EVALUATION.md`, `EXECUTION_PLAN.md`

---

## 1. Problem

Creators run the same lifecycle every week — trend, research, idea, script, hook, record, edit, thumbnail, caption, post, analyze, reuse — across 5–10 disconnected tools. Each tool forgets who they are, and nothing learns from what performed. The cohort built 27 tools that each fix one stage. Shipped side by side they would be the same fragmented experience. Shipped as one system around a shared object and shared memory, they become a product.

## 2. Target users (MVP)

Serious solo creators and small creator teams with a repeated weekly workflow.

| Persona | Workflow | What they need most | Primary surfaces |
|---|---|---|---|
| **Educator / tech YouTuber** (long video + Shorts + LinkedIn) | 1 long video → many shorts/posts | Research, script, repurposing, thumbnails | Create, Production, Repurpose |
| **Podcaster** | 1 episode/week | Transcript → chapters, clips, show notes, social posts | Ingest, Clips, Repurpose |
| **Personal-brand creator** (Instagram + LinkedIn) | Daily short posts | What to post today, hooks, captions in their own voice | Home, Discover, Studio |

Later: creator teams → agencies → small businesses → brands.

## 3. Product principles

1. **One object, not 27 tools.** Everything operates on a **Campaign** (a.k.a. Content Project). No toolbox dashboard of generators.
2. **Remembers the creator.** Voice, pillars, audience, library and insights feed every generation.
3. **AI proposes, creator decides.** Editable everything; explicit checkpoints; never auto-publish.
4. **Show the work.** Every AI card shows which agent made it, its judge score, and a "why" line; every run links to its trace.
5. **Closed loop.** Analytics produce insights; insights visibly change the next recommendations.
6. **Never a blank screen.** Streaming cards, skeletons per step, partial results, offline drafts when providers fail.

## 4. Core concepts (glossary)

| Term | Definition | Stored in |
|---|---|---|
| Creator | The account owner and their niche/platforms/goals | `creators` |
| Voice Profile | Versioned model of the creator's style + brand rules | `voice_profiles` |
| Source | Anything uploaded or linked (video, podcast, CSV, post, PDF, comments) | `sources` |
| Library Item | A piece of content the creator made/published | `library_items` (+ `chunks` for search) |
| Opportunity | A suggested thing to make, with rationale and evidence | `opportunities` |
| **Campaign** | Root object: one idea with objective, master format, platforms, and all its assets | `campaigns` |
| Asset | Any typed output (hook, script, shot list, caption, platform post, clip…) | `assets`, `asset_versions` |
| Insight | A learned statement about what works, with evidence | `insights` |
| Capability | One canonical specialist agent (17 total) | `capability_registry.yaml` |
| Run | One execution in a mode (quick, studio, campaign, brain, ingest, autopilot, screenplay) | `agent_runs`, `run_events` |
| Judge Score | Rubric-based quality score for an asset | `judge_scores` |

## 5. Information architecture

Primary nav: **Home · Discover · Create · Library · Insights**
Secondary: **Calendar · Collaborate · Brand Deals · Settings**
Global: **Omnibox** ("What are you thinking about?") on Home and via ⌘K everywhere · **Run drawer** (live agent activity) · **System Map** (`/system`) showing all capabilities and their origin projects.

## 6. Functional requirements

Priority: **P0** = must work in today's integrated demo · **P1** = next build cycle · **P2** = Phase 2/3.

### 6.1 Onboarding & Creator Memory (13, 22, 19)
- **FR-01 (P0)** 4-step onboarding: creator type, platforms, goals, import (paste 3–10 past posts / YouTube URL / CSV). Skippable; "Use demo creator" button.
- **FR-02 (P0)** On import, run `voice.build_profile` and show the profile (tone, sentence length, hook patterns, CTA style, words to avoid) as editable chips.
- **FR-03 (P1)** `strategy.pillars` proposes 3–5 content pillars + audience definition; creator edits.
- **FR-04 (P1)** Voice profile versions; each asset records the version it used.

### 6.2 Omnibox (27)
- **FR-05 (P0)** Free text + attachments → `intent_router` → route to campaign / quick / brain / ingest. Low confidence shows 2–3 action chips.
- **FR-06 (P0)** Recent prompts and "Try:" examples for first-time users.

### 6.3 Home — daily command center (04, 22, 23, 10, 24, 16)
- **FR-07 (P0)** Greeting + 4–5 opportunity cards: Trending, From your audience, From your analytics, Recycle, Strategy progress. Each card: title, rationale bullets, evidence link, "Create" button (seeds a campaign with `origin` + `origin_ref`).
- **FR-08 (P0)** "Today's plan" (`strategy.daily_plan`) — what to post today, per platform.
- **FR-09 (P1)** Weekly goal progress ("2 posts away from this week's goal").

### 6.4 Discover (01, 11, 12, 23, 24)
- **FR-10 (P0)** Idea Engine: topic (+optional audience) → validated ideas with scores (audience relevance, expertise fit, past performance, trend relevance, content gap, effort) and recommended formats.
- **FR-11 (P0)** Trend-to-content: enter a trend/topic → creator-specific angle → hook, script outline, format. (Trend source: manual entry + web search in MVP.)
- **FR-12 (P0)** Research panel: topic → key facts, angles, sources with citations.
- **FR-13 (P1)** Audience questions feed from analyzed comments with "Turn into content".

### 6.5 Create — AI Content Director (18, 21, 22, 27)
- **FR-14 (P0)** Start campaign from omnibox, opportunity, idea or upload. Form pre-filled: title, objective, primary platform, secondary platforms, master format.
- **FR-15 (P0)** Run the Director graph with live progress: each step appears as a card as it completes (research, angles, brief, hooks, script, shot list, thumbnail concepts, copy, platform versions, schedule).
- **FR-16 (P0)** Checkpoint: creator selects/edits the angle before production continues. Option "Auto-decide" skips checkpoints.
- **FR-17 (P0)** Final package view with overall quality score and per-asset judge badges.
- **FR-18 (P1)** Re-run any single step; downstream steps marked "stale" with "Update downstream" action.

### 6.6 Content Studio (03, 05, 08, 09, 13, 15)
- **FR-19 (P0)** Block editor for a campaign: Title · Hooks (pick 1 of 3+) · Script · CTA · Caption · Voice indicator. Every block: edit, regenerate, restyle-to-voice, shorten/expand, copy, version history, judge badge with critique on hover.
- **FR-20 (P0)** Quick generators reachable contextually (not as a toolbox): e.g. "10 more hooks", "CTA for leads goal".
- **FR-21 (P1)** Workspace statuses: Idea → Research → Script → Ready → Published (Kanban view) (15).

### 6.7 Production Studio (07, 25, 06, 14)
- **FR-22 (P0)** Production plan: scenes with timestamps, visual, B-roll, on-screen text, camera direction, props.
- **FR-23 (P0)** Thumbnail concepts (3): composition, focal element, text overlay (≤ 5 words), color/emotion; rendered as simple wireframe mock cards.
- **FR-24 (P1)** Upload long video/podcast → transcript → clip candidates with validated timestamps, hook, caption; podcast pack: title, description, chapters, highlights.
- **FR-25 (P2)** Actual clip cutting via ffmpeg + download.

### 6.8 Repurpose (02, 21, 14)
- **FR-26 (P0)** One master asset → LinkedIn post, X thread, Instagram caption, YouTube description, (P1) newsletter, carousel outline. Platform limits enforced.
- **FR-27 (P1)** "Repurpose this" on any library item.

### 6.9 Library & Second Brain (19, 15)
- **FR-28 (P0)** Library list of all campaigns, assets and imported items with search (hybrid semantic + keyword) and filters.
- **FR-29 (P0)** Brain chat: "Have I talked about X?", "What can become a reel?", answers with citations/timestamps linking to items.
- **FR-30 (P1)** Drift ("how has my opinion on X changed"), promises ("what did I promise viewers"), connections.

### 6.10 Audience Intelligence (10, 11)
- **FR-31 (P0)** Import comments (CSV/JSON paste or demo data) → sentiment, intent (question/complaint/praise/request), themes/clusters, top questions, opportunities.
- **FR-32 (P0)** "Turn into content" on a cluster/question → ideation(source=comments).
- **FR-33 (P2)** Suggested replies.

### 6.11 Insights & Analytics Copilot (24, 22, 16)
- **FR-34 (P0)** Import analytics CSV (or demo) → dashboard with interpreted insights ("30–60 s explainers outperform"), not just numbers.
- **FR-35 (P0)** "Explain why this worked" on a single item; "What should I make next" → ideas seeded by insights.
- **FR-36 (P0)** Insights visibly feed the Director: campaign brief shows "Using insight: …".
- **FR-37 (P1)** Recycle panel: candidates to repost/rework/refresh with a one-click refresh campaign.

### 6.12 Calendar (04, 21)
- **FR-38 (P0)** Campaign schedule written to a week/month calendar; drag to reschedule; export .ics / copy-to-clipboard per post.
- **FR-39 (P2)** Direct publishing integrations.

### 6.13 Collaborate & Brand Deals (26, 17)
- **FR-40 (P1)** Collab finder over a seeded creator dataset: filters (niche, platform, size, location) → matches with overlap rationale and collab ideas.
- **FR-41 (P1)** Brand pitch builder: brand info + creator profile → media kit, pitch email with subject line options, proposal sections, packages, alignment score; editable and exportable.

### 6.14 Screenplay Workspace (20)
- **FR-42 (P1)** Story bible (characters, locations, rules, timeline); scene drafting with continuity check warnings.

### 6.15 Transparency & Quality (all)
- **FR-43 (P0)** Run drawer shows the live agent timeline (agent name, status, duration, judge score, "view trace").
- **FR-44 (P0)** `/system` page: every capability, its modes, origin project numbers, health (last run status, p50 latency, avg judge score).
- **FR-45 (P0)** Feedback: thumbs up/down, "used this", edits captured as signals.
- **FR-46 (P1)** `/admin/evals`: latest offline eval results per capability.

### 6.16 Export
- **FR-47 (P0)** Export campaign as Markdown / copy all; per-asset copy buttons.
- **FR-48 (P1)** PDF media kit / production sheet.

## 7. Key user journeys and acceptance criteria

**J1 — Idea to campaign (P0, the main demo)**
Given a creator with a voice profile, when they type "I want to explain AI agents to beginner developers" and press Enter, then within 4 s the first card (research) streams in; they pick an angle; within 90 s the package contains ≥ 3 hooks, 1 script within the word budget, a shot list, 3 thumbnail concepts, primary caption + CTA, ≥ 3 platform versions and a schedule; every asset shows a judge badge; the campaign appears in Library and Calendar.

**J2 — Podcast/video to content (P1; P0 with a pre-transcribed demo file)**
Upload transcript or media → ingest progress → topics, statements, audience questions, clip candidates with valid timestamps → "Create campaign from best opportunity" → J1 from the brief step.

**J3 — Comments to ideas (P0)**
Import comments → clusters and questions in < 30 s for 500 comments → "Turn into content" → validated ideas citing the comments that motivated them.

**J4 — Analytics to next content (P0)**
Import analytics CSV → ≥ 3 interpreted insights with evidence → "What should I make next" → ideas that reference the insights → new campaign brief shows "Using insight".

**J5 — Recycle (P1)**
Library → Recycle candidates with reason → "Refresh" → new hook, updated script, new caption and platform versions linked to the original.

**J6 — Ask my brain (P0)**
"What did I say about React?" → answer with citations that open the source item (and timestamp for transcripts).

## 8. Non-functional requirements

| Area | Requirement |
|---|---|
| Latency | Quick mode p50 < 6 s; first streamed card < 4 s; campaign full package p50 < 90 s; Brain first token < 2 s |
| Reliability | No unhandled error screens; every capability has provider fallback; partial results persist; SSE reconnect resumes from last event |
| Quality | Offline eval judge pass-rate ≥ 85% on golden sets for P0 capabilities; no P0 asset violates platform limits |
| Cost | Tracked per run (tokens, $). Target ≤ ₹15 (~$0.18) per full campaign on default tiers; cache hits free |
| Observability | 100% of LLM calls traced in LangSmith with mode/capability/origin tags; `agent_runs` row per run |
| Security | No secrets in repo (`.env.example` only); JWT auth; all queries scoped by `creator_id`; RLS on Supabase tables; uploads size/type-checked; prompt-injection wrapping for untrusted text |
| Privacy | Creator content never used across creators; trace metadata uses hashed ids |
| Accessibility | WCAG 2.1 AA: contrast, keyboard navigation, focus states, `aria-live` for streaming cards |
| Responsiveness | Fully usable at 375 px (mobile) and ≥ 1280 px |
| Language | UI English; generation respects creator language setting; handles code-mixed input |

## 9. Out of scope for MVP

Direct posting to social platforms (export/copy + calendar instead) · Instagram/YouTube OAuth analytics sync (CSV/link import instead) · video rendering/editing beyond optional clip cutting · payments/billing · team roles and permissions · mobile native app.

## 10. Release scope

| Release | Contents |
|---|---|
| **MVP (today's integrated build)** | Onboarding + voice, Omnibox, Home, Discover (ideas, trend, research), Director campaign mode, Studio, Production plan + thumbnails, Repurpose, Library + Brain chat, Audience import, Analytics import + insights, Calendar, Run drawer, System map, demo creator |
| **v1 (next cycle)** | Media ingest with transcription + clips, podcast pack, recycle, pitch builder, collab finder, screenplay workspace, eval dashboard, stale-step propagation |
| **v2 (Phase 3)** | Autopilot weekly strategy agent with approval inbox, publishing integrations, team workspaces, OAuth analytics sync |

## 11. Success metrics

| Type | Metric | Target |
|---|---|---|
| Activation | New user completes first campaign | ≥ 60% within first session; median < 5 min |
| Value | Assets accepted with light edits (edit ratio < 30%) | ≥ 50% |
| Retention proxy | Opportunities clicked on Home per session | ≥ 1 |
| Quality | Judge pass rate (online sample) | ≥ 85% |
| Loop | Campaigns whose brief uses ≥ 1 insight (once analytics imported) | ≥ 70% |
| System | Run error rate | < 2% |

## 12. Business model (for evaluation narrative)

Freemium: free tier (N campaigns/month, fast-tier models), Pro (unlimited campaigns, media ingest, analytics copilot, voice versions), Team/Agency (multiple creators, approvals). Moat: creator context + content graph + feedback loop — generation gets more personal the longer it is used, which a single-purpose caption generator can't match.

## 13. Assumptions and open questions

- The latest agent code lives in personal forks; upstream branches are older (e.g. `22_AI_Creative_Producer` is empty upstream; 23, 24, 25, 27 not on upstream). Owners port from their forks.
- Trend data in MVP comes from web search + manual entry; a real trend API is v1.
- Evaluation metrics are unknown; `EVALUATION.md` prepares evidence for every plausible axis.
- Default provider is Gemini (most projects already use it); the gateway allows switching per tier.
