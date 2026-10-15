# EVALUATION.md — Being ready for unknown metrics

The final output will be evaluated with criteria we don't know. The strategy is to produce **evidence for every plausible axis** and make that evidence visible inside the product, not in a slide.

## 1. Likely evaluation axes → evidence we will show

| Axis (likely) | What evaluators will look for | Our evidence | Where |
|---|---|---|---|
| **Integration** — "all agents working together, seamless" | One product, not 27 tabs; agents hand off to each other | Director run where 10+ capabilities from ~15 origin projects stream into one campaign; System Map showing every project's home | Campaign run view, `/system` |
| Problem solving / core logic (from repo README checklist) | Each original challenge still solvable | Coverage matrix §6: each project's original build challenge reproduced as a test case | `/system` "Try it", eval report |
| AI quality | Outputs good, specific, on-voice | Offline eval scores per capability with judge + human calibration | `/admin/evals`, LangSmith experiments |
| Agent design | Sensible orchestration, not one giant prompt | Modes table, graph diagram, checkpoints, repair loop, best-of-N | AGENT_SYSTEM.md, live traces |
| Observability | Traces, feedback, datasets | LangSmith project with tagged traces (`origin:NN`), judge feedback on runs | "View trace" buttons |
| UI & usability | Intuitive, coherent, responsive | Omnibox-first flow; 5 nav items; mobile; accessibility pass | Live app, Lighthouse report |
| Prompt engineering (README checklist) | Robust, structured, edge cases handled | Prompt standard, structured output everywhere, edge-case rows in every dataset | Repo `prompts/`, datasets |
| Code quality (README checklist) | Modular, typed, tested | Contract tests over all capabilities, CI green, lint/typecheck | GitHub Actions |
| Documentation (README checklist) | Setup in minutes | Root README quickstart, per-capability README, this pack | Repo |
| Zero leaked secrets (README checklist) | `.env.example` only | gitleaks in CI | CI badge |
| Reliability | Demo doesn't break | Fallback chain, DEMO_MODE fixtures, partial results | Live |
| Performance & cost | Reasonable speed/spend | Latency and cost per run in run summary; benchmark table | Run banner, report |
| Product thinking / business | Who it's for, why it wins | Personas, loop, moat, pricing (SPEC §2, §12) | Pitch + landing page |
| Teamwork / process | Everyone contributed | CODEOWNERS, `origin:NN` tags, per-capability PRs | GitHub |

## 2. Offline evaluation harness (LangSmith)

- **Datasets:** one per capability (`creatoros/<capability>`), ≥ 8 rows each (≥ 3 edge cases), synced from `capabilities/<name>/dataset.jsonl` by `evals/sync_datasets.py`. Plus `creatoros/e2e_campaign` (10 topics × 3 creator profiles).
- **Evaluators per row:** (1) deterministic validators (pass/fail), (2) LLM judge with the capability rubric (1–5 per criterion), (3) optional reference comparison where a reference output exists, (4) latency and cost.
- **E2E campaign evaluators:** package completeness (all expected asset kinds present), cross-asset consistency (hook used in script, CTA goal matches objective, facts in copy trace to research ids), voice consistency across assets (voice.score variance), total latency, total cost.
- **Run:** `python -m evals.run --suite all --model-profile default --experiment-prefix demo-2026-09-30` → LangSmith experiment + `evals/report.md` (table per capability: mean score, pass rate, validator failures, p50/p95 latency, cost).
- **Gates:** P0 capability merges only if mean ≥ 3.6 and validator failures = 0 on its dataset. CI runs a 3-row smoke eval on main.
- **Regression:** each prompt version bump runs its capability suite and compares to the previous experiment.

## 3. Judge calibration (proves the judge is trustworthy)

For hook, script, copy, repurpose and research: 20 outputs each, two teammates score them blind with the rubric. Report Spearman correlation and exact-agreement ±1 between judge and human mean. Target ρ ≥ 0.6. If lower, tighten rubric anchors and re-run. Publish the table in `evals/calibration.md`. Use a different model family for the judge than the generator where possible.

## 4. Online signals (in product)

Judge sampling scores · thumbs up/down · accepted/copied/exported · edit ratio (Levenshtein between AI version and final) · regenerate count · checkpoint choices. All written to `feedback` and LangSmith feedback on the originating run. Low-scored runs are auto-added to an annotation queue for dataset growth.

## 5. Benchmarks to report

| Measure | How | Target |
|---|---|---|
| Campaign end-to-end p50/p95 | 10 campaigns, default tiers | p50 < 90 s |
| Time to first card | same | < 4 s |
| Quick mode p50 per capability | 20 calls each | < 6 s |
| LLM calls per campaign | LangSmith child run count | ≤ 18 |
| Cost per campaign | usage accounting | ≤ ~$0.18 |
| Cache hit latency | repeat run | < 1 s |
| Error rate | all runs during eval day | < 2% |

## 6. Coverage matrix (original build challenges as tests)

Every original build challenge from the repo README becomes an acceptance test run through the unified platform (quick mode or campaign). Example rows:

| # | Original challenge | Unified-platform test |
|---|---|---|
| 01 | topic + audience → 10 ideas | `ideation.ideas` count=10 with validation scores |
| 02 | one input → LinkedIn, IG, X, YT | `repurpose.all` returns 4 valid platform posts |
| 03 | 10 hooks, different styles | `hook.generate` n=10, ≥ 6 distinct styles |
| 05 | idea → hook, body, CTA | `script.reel_60` has 3 sections, 130–160 words |
| 06 | transcript → best moments with timestamps | `clip.clips` timestamps within duration, each ≥ 15 s |
| 09 | contextual CTAs by goal | `copy.cta` goal-aligned, not similar to recent CTAs |
| 10 | comments → themes, questions, complaints, opportunities | `audience.analyze` has all four sections |
| 13 | new draft in creator's style | `voice.restyle` voice.score ≥ 4 |
| 18 | research → angles → narrative → script → visuals → shot list → copy | Director campaign produces all |
| 19 | "Have I talked about this before?" | Brain answer with ≥ 1 citation |
| 21 | Research → YT script → 3 reels → LinkedIn → X → captions → calendar | Director with `master_format=youtube_long`, 3 reel scripts, schedule |
| 22 | goal → audience, pillars, 30-day strategy, adapt with performance | `strategy.strategy_30d` references active insights |
| … | (fill all 27 rows — owners add theirs in the PR) | |

Put the full table in `/system` so evaluators can click "Run this test" per project.

## 7. Red-team and robustness checklist

Prompt injection in comments ("ignore previous instructions and…") → audience report treats it as a comment · empty and one-word inputs · 50k-character transcript (truncation notice) · code-mixed language input · unsafe topic (graceful refusal card) · provider outage (kill primary API key → fallback provider; kill all → DEMO fixtures labelled offline) · SSE disconnect mid-run (refresh page → timeline replays) · two users (creator A can't access B's campaign — integration test) · malformed CSV import (row-level errors shown).

## 8. Demo script (7 minutes)

1. **(0:00)** Landing → "Try demo" → Home: greeting, 5 opportunity cards with evidence. "This isn't a toolbox — it's a creator's daily command center."
2. **(0:45)** Omnibox: "I want to explain AI agents to beginner developers." → Campaign opens, RunDrawer shows research ∥ library ∥ audience running with origin chips (#12, #19, #11).
3. **(1:30)** Checkpoint: pick angle (scores + why). Mention insight used: "30–60 s explainers outperform" (from #24 analytics).
4. **(2:15)** Stream: hooks (best-of-N judged), script with word budget, then parallel fan-out: shot list (#25), thumbnails (#07), copy + CTA (#08/#09), platform versions (#02). Judge badges appear.
5. **(3:30)** Studio: edit a line, restyle to voice (#13), show version history. Distribution tab: LinkedIn/X/IG previews with char counters.
6. **(4:30)** Library chat: "Have I talked about MCP before?" → cited answer (#19). Insights: import comments → clusters → "Turn into content" (#10/#11).
7. **(5:30)** `/system`: all 17 capabilities, 27 origin projects, health stats; click "View trace" → LangSmith tree of the campaign.
8. **(6:15)** Eval report: scores per capability, calibration, latency/cost. Close on the loop: Discover → Create → Analyze → Learn.

**Backups:** DEMO_MODE on the demo instance; pre-run campaign already in Library; a screen recording of the full flow; second deployment URL.

## 9. Evidence pack checklist (have ready before evaluation)

- [ ] Live URL + demo login
- [ ] Architecture diagram (from ARCHITECTURE.md) as an image
- [ ] `/system` page populated with real stats
- [ ] LangSmith project link with a clean campaign trace
- [ ] `evals/report.md` + `evals/calibration.md`
- [ ] Coverage matrix with all 27 rows green
- [ ] CI badge green; gitleaks clean
- [ ] Root README quickstart tested on a fresh machine
- [ ] 3-minute recorded walkthrough
