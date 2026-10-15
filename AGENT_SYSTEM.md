# AGENT_SYSTEM.md — How ~70 agents become one coherent system

> Companion files: `capability_registry.yaml` (machine-readable roster), `AGENT_CONTRACT.md` (how each teammate ports their agent), `EVALUATION.md` (judges + evals).

---

## 1. The problem we are solving

Each of the 27 projects ships 2–3 agents plus its own LLM judge and its own LangSmith setup. Merged naively you get roughly 60–80 agents, 27 judges, 4 LLM providers, 5 databases and 27 slightly different definitions of "a hook" or "a script". The failure modes are predictable:

| Naive merge symptom | Consequence |
|---|---|
| Research done by 12, 18, 21 and 23 separately | Same topic researched 3–4× per campaign → cost, latency, contradictory facts |
| Hooks written by 03, 05, 16, 18, 21 | Five prompt styles, five output schemas, UI can't render them uniformly |
| 27 judges with different scales | Scores are incomparable → no platform-wide quality number |
| Each agent loads creator context its own way | Voice drifts between outputs of the same campaign |
| 27 tracing setups | No single trace for a campaign; evaluators can't see "agents working together" |

**Principle: merge by output type, parameterize by mode and context.** One capability per card kind. The project that invented a behavior becomes a *mode* of the canonical capability, not a separate agent.

---

## 2. Overlap matrix → canonical capabilities

| Function | Implemented in projects | Canonical capability | How duplicates are absorbed |
|---|---|---|---|
| External topic research | 12, 18 (research stage), 21 (research step), 23 (trend research) | `research` | Modes `brief`/`deep`/`fact_check`. Runs once per campaign; `ResearchBrief` is passed to every downstream node |
| Internal "what have I said" | 19 (researcher, drift, promises, connections), 15 (workspace search) | `library` | #19's specialists become modes |
| Ideas / angles | 01, 11 (comments→ideas), 18 (angles), 23 (trend→content), 04 (daily idea) | `ideation` | `source` param: topic, trend, comments, analytics, library_gap, recycle. Validation scoring built in |
| Comment analysis | 10, 11 (clean/intent/cluster) | `audience` | #11's pipeline (clean→intent→cluster→gap→score) + #10's sentiment/themes |
| Strategy & planning | 04, 22, 21 (calendar) | `strategy` | Modes `pillars`, `strategy_30d`, `daily_plan`, `weekly_plan`, `schedule` |
| Hooks | 03, 05, 16 (new hook), 18, 21 | `hook` | #03's style taxonomy is canonical; others call `hook` |
| Scripts | 05 (reel), 18 (script/narrative), 21 (YT script) | `script` | Modes by format; word budget per duration |
| Captions / CTA / titles / descriptions | 08, 09, 14 (title/description), 18 (publishing copy) | `copy` | One call can return a `full_pack`; CTA anti-repetition (from #09) is the only CTA logic in the system |
| Voice / style | 13 | `voice` | Not a generator: profile builder + restyler + scorer, injected into every generation |
| Platform adaptation | 02, 21, 14 | `repurpose` | #02's per-platform chains become modes; calls `copy.cta` rather than writing its own CTAs |
| Thumbnails & pre-production | 07, 18 (visuals, shot list), 25 | `visual` | `thumbnail`, `shot_list`, `full_preproduction` |
| Clips / podcast moments | 06, 14 (chapters, highlights), 19 (clip_editor) | `clip` | Transcription & cutting are platform services; LLM only scores/labels moments |
| Performance analysis | 24, 22 (adapt using performance) | `performance` | Emits `insights` rows that the Director reads (closed loop) |
| Recycling | 16 | `recycle` | Similarity + recency + performance scoring from #16 kept; LLM writes refresh plan |
| Brand pitch | 17 | `pitch` | — |
| Collab finder | 26 | `collab` | — |
| Screenplay | 20 | `screenplay` | Separate mode with story bible memory |
| Orchestration | 18, 21, 22, 27 | `director`, `brain`, `autopilot`, `intent_router` | See §4 |
| Judging | all 27 | `judge_service` | One service, rubric per capability (§6) |

**Result:** 4 orchestrators + 17 specialists + 1 judge service + 5 platform pipelines. Every one of the 27 projects is still visibly represented (see coverage check at the bottom of `capability_registry.yaml`).

---

## 3. Agent tiers

```
TIER 0  ORCHESTRATORS   intent_router · director · brain · autopilot
            │  decide WHAT runs, in which order, with which human checkpoints
TIER 1  SPECIALISTS     research · library · ideation · audience · strategy · hook · script · copy
            │           voice · repurpose · visual · clip · performance · recycle · pitch · collab · screenplay
            │  do ONE job, return a typed output + UI card, never call the DB or providers directly
TIER 2  PLATFORM        llm_gateway · context_builder · judge_service · validators · ingest_pipeline
                        memory (pgvector) · tools (web_search, web_fetch, transcribe, ffmpeg) · scheduler
```

Rules that keep this efficient:
1. Specialists never call other specialists directly, with one allowed exception declared in the registry (`repurpose → copy.cta`), which goes through `ctx.call_capability()` so it is traced and cached.
2. Specialists never build their own creator context; they receive `CreatorContext` from the orchestrator.
3. Specialists never judge themselves; they declare a `rubric` id and the orchestrator calls `judge_service`.
4. Every specialist works in every mode listed in its `modes_allowed`; there is no "campaign-only" copy of a prompt.

---

## 4. Execution modes (the "agentic modes")

The same 17 specialists run under seven execution modes. The mode decides the graph shape, latency budget and where the human sits.

| Mode | Trigger | Graph shape | Human in loop | Latency target | Origin |
|---|---|---|---|---|---|
| **Quick** | "give me 10 hooks for X", tool chips | Single capability → validators → (judge if cheap) | Edits result | p50 < 6 s | 01, 03, 07, 08, 09 |
| **Studio** | Buttons inside the Content Studio editor (regenerate block, restyle, shorten) | Single capability scoped to one asset + voice restyle | Every step | p50 < 5 s | 05, 08, 09, 13, 15 |
| **Campaign** | "Create campaign", "Turn this idea into content" | Director LangGraph DAG with parallel fan-out and 1–2 interrupts | Approve angle; optional approve script | First card < 4 s, full package < 90 s | 18, 21, 22 |
| **Brain (chat)** | Omnibox questions, Library chat | Supervisor with specialists-as-tools; streams cards | Conversational | First token < 2 s | 19, 15, 27 |
| **Ingest** | Upload video/podcast/CSV/comments, paste links | Deterministic pipeline (transcribe → chunk → embed) + LLM enrichment (audience, clip, performance, voice.build_profile) | None (async, progress bar) | Async; progress events | 06, 10, 11, 14, 16, 19, 24 |
| **Autopilot** (Phase 3) | "Manage my content strategy this week", weekly cron | performance → discover → ideation → director(xN) → calendar | Approval inbox; never auto-publishes | Background | 22, 21 |
| **Screenplay** | Screenplay workspace | Stateful loop: bible → scene → continuity_check → bible_update | Every scene | p50 < 10 s | 20 |

### 4.1 Mode selection (intent_router)

The omnibox ("What are you thinking about?") sends text + optional attachments to `intent_router` (fast tier, structured output):

```json
{
  "route": "campaign | quick | brain | ingest | autopilot | screenplay",
  "capability": "hook",                  // for quick
  "slots": {"topic": "MCP for beginners", "platforms": ["instagram_reels"], "format": "reel_60", "count": 10},
  "confidence": 0.82,
  "suggestions": [ {"label": "Create full campaign", "route": "campaign"}, {"label": "Just 10 hooks", "route": "quick", "capability": "hook"} ]
}
```

Routing rules (deterministic overrides before the LLM): attachment present → `ingest` then offer campaign; text starts with a question about the past ("did I", "have I", "what did I say") → `brain`; confidence < 0.6 → show `suggestions` as chips instead of guessing.

Examples from the product doc: "I want to explain MCP to beginners" → campaign. "Turn this podcast into content" + file → ingest → campaign(origin=upload). "I haven't posted in three days" → strategy.daily_plan (quick). "Find something old I can reuse" → recycle.candidates (quick). "This reel got 100K views, help me make the next one" → performance.explain_item → campaign seeded with the insight.

---

## 5. The Director (Campaign mode) graph

LangGraph `StateGraph` with a Postgres checkpointer (resumable after interrupts and reconnects).

```
                    ┌──────────────────────┐
                    │ load_context          │  context_builder (voice vN, pillars, active insights,
                    └──────────┬───────────┘   recent assets, last 20 CTAs)  — once per run
             ┌─────────────────┼──────────────────┐        PARALLEL
             ▼                 ▼                  ▼
      research.brief     library.search     audience.questions_only
      (external facts)   (what I said)      (open questions on topic)
             └─────────────────┼──────────────────┘
                               ▼
                    ideation.angles  (3–5 angles, each scored: relevance, gap, effort, formats)
                               ▼
                 ⏸ INTERRUPT: creator picks angle / edits brief   (auto-pick in Autopilot)
                               ▼
                    strategy.brief (objective, primary+secondary platforms, master format, key message)
                               ▼
                    hook.generate (N=8) ──► judge pairwise best-of-N → top 3
                               ▼
                    script.<format> (uses hook #1, research citations, voice)
                               ▼
                    judge(script) ── fail ──► script.revise (1 retry with critique) ──┐
                               │ pass                                                  │
                               ◄───────────────────────────────────────────────────────┘
             ┌─────────────────┼──────────────────┬────────────────────┐   PARALLEL FAN-OUT
             ▼                 ▼                  ▼                    ▼
      visual.shot_list   visual.thumbnail   copy.full_pack      repurpose.all
                                            (primary platform)  (secondary platforms; calls copy.cta)
             └─────────────────┼──────────────────┴────────────────────┘
                               ▼
                    strategy.schedule  → calendar_entries
                               ▼
                    final_review: validators on all assets + judge sample → package score
                               ▼
                    persist assets + versions → library write-back (embed accepted assets)
```

`CampaignState` (Pydantic / TypedDict):

```python
class CampaignState(TypedDict, total=False):
    run_id: str; campaign_id: str; creator_id: str
    request: CampaignRequest          # topic, objective, platforms, format, origin, source_ids
    context: CreatorContext
    research: ResearchBrief | None
    library_hits: list[LibraryHit]
    audience_signals: AudienceSignals | None
    angles: list[Angle]; chosen_angle: Angle | None
    brief: StrategyBrief | None
    hooks: list[Hook]; top_hooks: list[Hook]
    script: Script | None; script_attempts: int
    production: ProductionPlan | None
    thumbnails: list[ThumbnailConcept]
    copy: CopyPack | None
    platform_posts: list[PlatformPost]
    schedule: list[CalendarEntryIn]
    scores: Annotated[dict[str, JudgeScore], merge_dicts]
    errors: Annotated[list[NodeError], operator.add]
```

Node rules:
- Every node wraps a capability via `run_capability(name, mode, input, state)`, which handles caching, tracing tags, event emission, validator+judge calls and error capture.
- A failed non-critical node (thumbnail, schedule) records an error and the graph continues; the UI shows "retry this step". Only `script` failure after retry fails the run, and even then earlier cards remain saved.
- `Send` API is used for fan-out so the four production branches run concurrently.
- Interrupts use `interrupt()`; the frontend calls `POST /v1/runs/{id}/resume` with the chosen angle.

---

## 6. Brain (chat) mode

Adopt #19's supervisor design platform-wide: specialists are tools; each tool returns a short text summary for the supervisor to reason over plus a full card streamed to the UI (cards are never sent back into the model context, which keeps token use low).

Tools exposed to the Brain: `library.*`, `research.brief`, `ideation.ideas`, `audience.analyze`, `performance.patterns`, `recycle.candidates`, `hook.generate`, `copy.cta`, `strategy.daily_plan`, `pitch.pitch`, `collab.find`, plus one meta-tool `start_campaign(topic, …)` that hands off to the Director and returns the run link. Summarization middleware compacts long threads; threads are checkpointed in Postgres.

System prompt skeleton: role ("you are this creator's creative partner"), team roster with one-line tool descriptions, rules (split multi-part requests; don't call tools for greetings; never invent quotes/timestamps; keep `[n]` citations; suggest one next action).

---

## 7. Shared infrastructure that removes duplication

### 7.1 CreatorContext (built once per run)

```python
class CreatorContext(BaseModel):
    creator: CreatorSummary                 # niche, platforms, goals, languages
    voice: VoiceProfile                     # version pinned for the whole run
    voice_exemplars: list[str]              # 3–5 best-performing posts, trimmed
    pillars: list[Pillar]
    audience: AudienceSummary
    active_insights: list[Insight]          # top 5 by confidence — the closed loop
    recent_ctas: list[str]                  # last 20, for anti-repetition
    recent_topics: list[str]                # to avoid repeating themselves
    token_budget: int = 1800                # context_builder trims to fit
```

Rendered into prompts through a single template partial `prompts/_partials/creator_context.md`, so every specialist sees the creator the same way.

### 7.2 Voice injection
All text-producing capabilities append the voice partial. For high-stakes outputs (script, primary caption) the Director calls `voice.score`; if below 3.5/5 it calls `voice.restyle` once. Voice match is also a universal judge criterion, so drift is measured, not assumed.

### 7.3 Memory write-back
Accepted/edited assets are embedded into `chunks` via `library_items`. Insights from `performance` get `applied_count` incremented when the Director uses them — this is how the platform can show "this recommendation came from last week's analytics".

### 7.4 Research reuse
`ResearchBrief` has stable citation ids (`[R1]…[Rn]`). Script, copy and repurpose must cite by id when stating facts; the validator checks that every cited id exists.

---

## 8. Judge system (one service, many rubrics)

### 8.1 Two stages
1. **Deterministic validators** (free, instant): JSON schema, platform char limits (X 280/tweet, IG caption ≤ 2,200, YT title ≤ 100, LinkedIn ≤ 3,000), word budget per duration (~150 wpm; 60 s ≈ 130–160 words), banned words from brand rules, timestamps within media duration, citation ids resolvable, CTA cosine similarity vs `recent_ctas` < 0.9, duplicate hooks.
2. **LLM judge** (judge tier; prefer a different model family than the generator to reduce self-preference bias).

### 8.2 Rubric format (`rubrics/<capability>_v1.yaml`)
```yaml
id: hook_v1
capability: hook
universal: [relevance, voice_match, specificity, platform_fit, safety]
specific:
  - {key: scroll_stop, desc: "Would this stop a scroll in the first 2 seconds?"}
  - {key: curiosity_gap, desc: "Opens a question the video answers"}
  - {key: clarity_3s, desc: "Understandable when read or heard in 3 seconds"}
scale: 1-5            # anchors per score defined in the file
pass_threshold: 3.6   # weighted mean
weights: {relevance: 1.0, voice_match: 1.0, specificity: 1.0, platform_fit: 0.7, safety: 2.0, scroll_stop: 1.5, curiosity_gap: 1.0, clarity_3s: 1.0}
hard_fail: [safety < 3]
```

Universal criteria (identical wording in every rubric so scores are comparable across the platform): **relevance** to request/brief, **voice_match**, **specificity** (non-generic, concrete), **platform_fit**, **groundedness** (claims supported by research/library ids — only where facts are stated), **safety/brand** rules.

### 8.3 Judge output
```json
{"rubric_id":"script_v1","rubric_version":"1.0","scores":{"relevance":5,"voice_match":4,"structure":4,"pacing":3},
 "overall":4.1,"pass":true,"critique":"Body runs 170 words for a 60s reel.","fix_instructions":"Cut example 2; keep one analogy."}
```

### 8.4 Policies
- **Repair loop:** on fail, one retry with `fix_instructions` appended. Never more than one (cost cap). Second failure → keep best attempt, mark "needs review" in UI.
- **Best-of-N:** hooks and titles use pairwise comparisons (tournament of 8 → 3) rather than absolute scores; pairwise is more reliable for ranking.
- **Sampling:** Campaign mode judges script, primary copy and hooks always, and samples 1 of the remaining production assets. Quick mode runs validators always, the LLM judge on a configurable sample (default 30%) plus always in `EVAL_MODE`. Everything is judged in offline evals.
- **Logging:** each score is written to `judge_scores` and to LangSmith as feedback on the generating run (`feedback_key = judge.<criterion>`), so traces show quality inline.
- **Calibration:** 20 human-labelled examples per core rubric (hook, script, copy, repurpose, research); report judge-vs-human agreement in `EVALUATION.md`.

---

## 9. Efficiency playbook

| Lever | Implementation | Effect (estimate) |
|---|---|---|
| Research once | Shared `ResearchBrief` per campaign | Removes 2–3 duplicate research calls per campaign |
| Context once | `CreatorContext` built at run start, pinned voice version | Consistent voice; fewer DB round trips |
| Model tiers | fast (classification, hooks, captions), standard (scripts, repurpose), reasoning (director planning, strategy, performance), judge | 40–60% cost reduction vs. using the top model everywhere |
| Parallel fan-out | LangGraph `Send` for research ∥ library ∥ audience and production ∥ copy ∥ repurpose | Campaign wall time ≈ longest branch rather than the sum |
| Caching | `sha256(capability, mode, prompt_version, model, normalized_input, voice_version)` → Redis (TTL 24 h) / `llm_cache` | Instant regenerate-free revisits, cheap demo reruns |
| Batching | Comments classified in batches of 50; embeddings in batches of 100 | 1 call per 50 comments instead of 50 |
| Validators before judge | Cheap checks catch ~most format failures | Fewer LLM judge calls |
| One repair max | Hard cap | Bounded worst-case cost |
| Streaming | SSE cards per node | Perceived latency drops even when total time doesn't |

Rough call budget for one campaign (estimate for planning, verify in LangSmith): naive merge ≈ 35–45 LLM calls; this design ≈ 14–18 calls including judges.

---

## 10. Failure handling

- **Provider fallback chain** per tier in the LLM gateway (e.g. Gemini → Claude → OpenAI → Groq), with timeouts per tier (fast 15 s, standard 45 s, reasoning 90 s).
- **Structured output repair:** on parse failure, one "fix this JSON to match schema" call on the fast tier, then fail the node.
- **Template fallback:** keep the local-fallback generators several projects already have (#05, #07) behind `DEMO_MODE`/`OFFLINE_FALLBACK`, clearly labelled "offline draft" in the UI.
- **Partial success is success:** a campaign with 9/10 assets renders with a retry button on the missing one.
- **Prompt injection:** comments, transcripts, web pages and uploaded files are wrapped as `<data>` blocks with an instruction that they are content to analyze, not instructions. The audience capability never executes instructions found in comments.

---

## 11. Tracing conventions (LangSmith)

- One LangSmith project per environment: `creatoros-dev`, `creatoros-demo`, `creatoros-eval`.
- Root run name = mode (`campaign`, `brain`, `quick:hook`); child run names = `cap:<capability>.<mode>`, `judge:<rubric_id>`, `tool:<name>`.
- Tags: `mode:<mode>`, `cap:<name>`, `origin:<project_no>` (e.g. `origin:09`) — this lets the team and evaluators filter traces by original project and prove each one runs inside the platform.
- Metadata: `campaign_id`, `creator_hash` (never raw PII), `prompt_version`, `model`, `voice_version`, `cache_hit`.
- `agent_runs.langsmith_run_id` stores the root id; the UI "View trace" button deep-links to it.
- Prompts live in the repo at `capabilities/<name>/prompts/<mode>.v<N>.md`; the version string is part of trace metadata and the cache key.

---

## 12. Prompt engineering standard (every capability)

Each prompt file follows the same sections: **Role** · **Creator context partial** · **Task** (mode-specific) · **Inputs** (wrapped as data) · **Constraints** (platform limits, word budget, banned words) · **Output schema** (enforced via structured output, never "return JSON please") · **Quality bar** (the rubric's criteria in plain words, so generation and judging aim at the same target) · **2 few-shot examples** (prefer the creator's own top posts when available).

Edge cases every capability must handle and test: empty/one-word input, very long input (truncate with notice), non-English or code-mixed input (e.g. Hinglish/Tanglish — respond in the creator's configured language), NSFW/unsafe topic (refuse gracefully in-card), missing creator profile (use neutral defaults and say so).
