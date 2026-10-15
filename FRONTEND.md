# FRONTEND.md — Implementation plan (apps/web)

## 1. Stack

Next.js 15 (App Router, TypeScript strict) · Tailwind CSS · shadcn/ui (Radix) · lucide-react · TanStack Query (server state) · Zustand (UI state: run drawer, omnibox, selection) · react-hook-form + zod (forms) · Tiptap (Studio block editor) · Recharts (Insights) · Framer Motion (restrained; card enter, step transitions) · `@supabase/ssr` (auth) · `openapi-fetch` + generated types from `packages/api-types` · Vitest + Testing Library · Playwright (e2e; reuse #09's e2e setup).

## 2. Route map

```
app/
├── (marketing)/page.tsx                 # Landing: value prop, "Try demo" (demo login), sign in
├── (auth)/login, callback
├── onboarding/page.tsx                  # 4 steps + voice profile reveal
└── (app)/layout.tsx                     # Sidebar, top bar (omnibox ⌘K), RunDrawer, Toaster
    ├── home/page.tsx                    # Command center
    ├── discover/page.tsx                # Tabs: Ideas · Trends · Research · Audience questions
    ├── create/page.tsx                  # Omnibox-first; recent campaigns; start campaign form
    ├── campaigns/[id]/page.tsx          # Campaign workspace (tabs below)
    │   ├── ?tab=overview                # Brief, package score, live run timeline
    │   ├── ?tab=studio                  # Hooks · Script · CTA · Caption (block editor)
    │   ├── ?tab=production              # Shot list, thumbnail concepts, (clips)
    │   ├── ?tab=distribution            # Platform versions side-by-side
    │   └── ?tab=schedule                # Calendar slots for this campaign
    ├── library/page.tsx                 # Grid/list + search + filters; Kanban toggle (Idea→Research→Script→Ready→Published)
    ├── library/chat/page.tsx            # Brain chat (also available as a side panel)
    ├── library/[itemId]/page.tsx        # Item detail: transcript w/ timestamps, metrics, "Repurpose", "Explain why"
    ├── insights/page.tsx                # Metrics + interpreted insights + recycle panel + audience report
    ├── calendar/page.tsx                # Week/month
    ├── collaborate/page.tsx             # Collab finder
    ├── brand-deals/page.tsx · brand-deals/[id]/page.tsx   # Pitch builder/editor
    ├── screenplay/[campaignId]/page.tsx # Story bible + scene editor
    ├── system/page.tsx                  # System Map: capabilities, modes, origin projects, health
    ├── admin/evals/page.tsx             # Eval results (admin)
    └── settings/page.tsx                # Profile, voice, pillars, API/provider status, data import
```

## 3. Key screens

### 3.1 Home (command center)
- Header: "Good morning, {name}" + one-line status ("2 posts away from this week's goal").
- **Omnibox** (large): placeholder "What are you thinking about?"; attachments (file, YouTube link); example chips on first visit. Enter → `POST /intents` → route (campaign → navigate to new campaign and open RunDrawer; quick → inline result sheet; brain → library/chat with message; ingest → upload progress).
- **Opportunities row**: 5 cards (🔥 Trending, 💬 Audience, 📈 Performance, ♻️ Recycle, 🎯 Strategy). Card: title, potential score, 2–3 "why" bullets, evidence link, primary "Create" and secondary "Save/Dismiss".
- **Today's plan**: per-platform suggestions from `strategy.daily_plan`.
- **Continue working**: last 3 campaigns with status and package score.
- One dominant CTA: **Create content**. No grid of generator tools.

### 3.2 Campaign workspace
- Left: campaign header (title, objective, platforms, status, package score ring).
- Center: tab content.
- Right (collapsible): **RunDrawer** — live agent timeline.
- Overview tab during a run shows the plan steps from `run.started` as skeleton cards that fill in on `node.completed`. Checkpoint "Choose your angle" renders 3–5 angle cards (score, why, formats) with "Use this" + "Edit brief".
- Completion banner: package score, asset count, time taken, cost, "View trace".

### 3.3 Studio tab (block editor)
Blocks: **Title** · **Hook** (selected + alternates carousel, "10 more") · **Script** (Tiptap with section markers HOOK / BODY / CTA and live word count vs budget and estimated duration) · **CTA** (variants, goal selector) · **Caption** (per platform limit counter) · **Voice** (match score chip; "Restyle to my voice"). Block toolbar: Regenerate · Shorten · Expand · Restyle · Copy · History · Judge badge (hover → critique). Edits autosave (debounced PATCH) and create versions.

### 3.4 Production tab
Scene table (time range, visual, B-roll, on-screen text, camera, props) · thumbnail concept cards drawn as simple wireframe (CSS layout with text overlay + focal element label, no image generation required) · clip list (if source media): timestamp chips, hook, caption, "copy timestamps", (v1) "cut clip".

### 3.5 Distribution tab
Side-by-side platform previews styled like each platform (LinkedIn post, X thread with per-tweet counters, IG caption, YT description, newsletter). Each preview: copy, edit, regenerate for that platform, char counter, judge badge.

### 3.6 Library + Brain
Search bar (hybrid), filters (platform, format, status, pillar, date), cards with metrics. Brain chat: messages with streamed cards under the assistant reply (library answers with `[n]` citations that open the item at the timestamp; idea cards with "Create campaign").

### 3.7 Insights
KPI tiles (views, engagement rate, followers) → **Interpreted insights** list (statement, confidence, evidence chart, "Use in next campaign") → "What should I make next?" → ideas → Recycle candidates → Audience report (sentiment donut, clusters, top questions with "Turn into content").

### 3.8 System Map (`/system`) — evaluation-critical
Visual of the architecture: orchestrators → 17 capabilities → platform services. Each capability tile: name, modes, **origin projects** (e.g. "from #03 Hook Generator, #05, #16, #18, #21"), last-24h runs, p50 latency, avg judge score, status dot. Clicking a tile opens a "Try it" panel (quick mode) and recent traces. A table below maps all 27 original projects → where they live in the product (from `capability_registry.yaml`). This page is the single strongest proof that "all agents work together".

## 4. Shared UI architecture

### 4.1 Card registry
`components/cards/registry.ts` maps backend `card.kind` → React component. Every capability's output renders through the same shell:

```tsx
<AiCard kind="hook" origin={{capability:'hook', projects:['03','05']}} score={score} onRegenerate onCopy onEdit>
  <HookCardBody data={card.data} />
</AiCard>
```
`AiCard` provides: header (icon, title, origin chip), judge badge, "why" line, actions, version menu, loading/failed states. Required kinds for MVP: research_brief, angle, idea, strategy_brief, content_plan, hook, script, shot_list, thumbnail_concept, caption, cta, platform_post, x_thread, library_answer, audience_report, insight, recycle_recommendation, clip, pitch, collab_match, scene. Unknown kind → generic JSON-pretty card (never crash).

### 4.2 Streaming
`hooks/useRunStream(runId)` — EventSource with `Last-Event-ID` reconnect, exponential backoff, heartbeat timeout 30 s; reduces events into `{plan, steps: Record<step, StepState>, cards, checkpoint, summary}`; writes completed assets into the TanStack Query cache for the campaign so tabs update live. `aria-live="polite"` region announces step completions.

### 4.3 Data layer
`lib/api.ts` (openapi-fetch client with auth header from Supabase session) · query keys `['campaign', id]`, `['assets', campaignId]`, `['opportunities']`, … · optimistic updates on asset edits · error toasts mapped from error codes (`retryable` → retry action).

### 4.4 State (Zustand)
`useUI`: sidebar collapsed, runDrawer {open, runId}, omnibox {open, draft}, theme. No server data in Zustand.

## 5. Design system

- Tokens in CSS variables (`--bg`, `--surface`, `--text`, `--muted`, `--accent`, `--success`, `--warning`, `--danger`, radii, spacing); dark and light themes; default dark with one accent.
- Type: Inter (UI) + a mono for timestamps/scripts; scale 12/14/16/20/24/32.
- Stage colors used consistently across app (Discover, Create, Produce, Distribute, Analyze) so users learn the lifecycle visually.
- Judge badge: 1–5 score, color by threshold, tooltip critique. Origin chip: small `#09` pill linking to System Map.
- Empty states always offer one action (import, try demo data, create).
- Reuse from projects where strong: #18 stage stepper and stage cards, #17 proposal editor + alignment score card, #21 run page event rendering, #12 research page + sidebar, #09 studio interactions and Playwright tests, #16 CSV import view and stat cards. Restyle to tokens; don't import their global CSS.

## 6. UX rules (non-negotiable)

1. Never a blank screen: skeletons per step; partial results always visible.
2. Every AI output is editable and shows who made it and its score.
3. Every long operation shows progress and is cancellable.
4. Every destructive action confirms; every edit is versioned.
5. Keyboard: ⌘K omnibox, ⌘Enter run, ⌘C on focused card copies, `?` shortcuts help.
6. Mobile: sidebar → bottom nav (Home, Discover, Create, Library, Insights); RunDrawer → bottom sheet.

## 7. Performance and accessibility budgets

LCP < 2.5 s on Home (opportunities are precomputed server-side) · JS per route < 250 KB gz · Tiptap and Recharts lazy-loaded · WCAG 2.1 AA (contrast ≥ 4.5:1, visible focus, labelled controls, reduced-motion respected) · Lighthouse ≥ 90 performance/accessibility on Home and Campaign.

## 8. Testing

Vitest: card registry renders every kind from fixtures; `useRunStream` reducer with recorded event logs; char counters. Playwright (desktop + mobile viewport) for journeys J1 (idea → campaign incl. checkpoint), J3 (comments → ideas), J4 (analytics → insights → campaign), J6 (brain question with citation), plus System Map loads all 17 capabilities. Run against `DEMO_MODE` API with fixtures for determinism.

## 9. Build order (frontend)

1. App shell, auth + demo login, tokens/theme, sidebar, generated API types.
2. Card registry + `AiCard` + `useRunStream` with a mock event log (can start before backend is ready).
3. Create → Campaign workspace Overview with live run + checkpoint.
4. Studio, Production, Distribution tabs.
5. Home with opportunities + omnibox routing.
6. Library + Brain chat; Insights; Discover.
7. System Map; Calendar; onboarding polish.
8. Collaborate, Brand deals, Screenplay (v1 if time).
9. Accessibility pass, mobile pass, Playwright green.
