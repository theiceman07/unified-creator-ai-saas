-- =====================================================================
-- CreatorOS — canonical Postgres schema (Supabase-compatible)
-- Requires: Postgres 15+, extensions pgvector, pg_trgm, pgcrypto
-- Every table that holds creator data carries creator_id and is protected by RLS.
-- The ROOT AGGREGATE is `campaigns` (a.k.a. Content Project). Every asset hangs off it.
-- =====================================================================

create extension if not exists vector;
create extension if not exists pg_trgm;
create extension if not exists pgcrypto;

-- ---------- enums ----------
create type platform as enum ('youtube','youtube_shorts','instagram','instagram_reels','tiktok','linkedin','x','podcast','newsletter','blog');
create type campaign_status as enum ('idea','planning','in_production','ready','scheduled','published','archived');
create type objective as enum ('audience_growth','engagement','authority','leads','monetization','brand_deal','community');
create type asset_status as enum ('draft','accepted','rejected','published','archived');
create type run_mode as enum ('quick','studio','campaign','brain','ingest','autopilot','screenplay');
create type run_status as enum ('queued','running','waiting_human','completed','failed','cancelled');
create type source_kind as enum ('text','url','youtube','audio','video','pdf','csv_analytics','csv_comments','post','transcript','image');

-- asset_kind is TEXT + check constraint (not enum) so new capabilities can add kinds without a migration lock.
-- Canonical kinds (keep in sync with capability_registry.yaml -> outputs.card_kind):
-- research_brief, angle, idea, strategy_brief, content_plan, hook, script, shot_list, thumbnail_concept,
-- caption, cta, title, description, hashtags, platform_post, x_thread, carousel, newsletter,
-- clip, chapter_list, podcast_notes, audience_report, insight, recycle_recommendation,
-- pitch, collab_match, scene, story_bible

-- ---------- identity ----------
create table creators (
  id              uuid primary key default gen_random_uuid(),
  auth_user_id    uuid unique,                 -- supabase auth.users.id
  display_name    text not null,
  handle          text,
  niche           text,
  creator_types   text[] default '{}',         -- educational, podcast, business ...
  platforms       platform[] default '{}',
  goals           objective[] default '{}',
  timezone        text default 'Asia/Kolkata',
  languages       text[] default '{en}',
  is_demo         boolean default false,
  created_at      timestamptz default now()
);

-- Voice / brand memory (from #13 Voice Replicator). Versioned: generation records which version it used.
create table voice_profiles (
  id              uuid primary key default gen_random_uuid(),
  creator_id      uuid not null references creators(id) on delete cascade,
  version         int not null,
  profile         jsonb not null,              -- tone, vocabulary, sentence_length, humor, hook_patterns, cta_style, emoji_policy
  brand_rules     jsonb default '{}'::jsonb,   -- words_to_avoid, must_include, compliance notes
  example_ids     uuid[] default '{}',         -- library_items used as few-shot exemplars
  is_active       boolean default true,
  created_at      timestamptz default now(),
  unique (creator_id, version)
);

-- Content pillars / audience definition (from #22 Creative Producer)
create table creator_strategy (
  creator_id      uuid primary key references creators(id) on delete cascade,
  audience        jsonb default '{}'::jsonb,
  pillars         jsonb default '[]'::jsonb,
  cadence         jsonb default '{}'::jsonb,   -- posts/week per platform
  updated_at      timestamptz default now()
);

-- ---------- sources & knowledge (Second Brain, #19 / #15) ----------
create table sources (
  id              uuid primary key default gen_random_uuid(),
  creator_id      uuid not null references creators(id) on delete cascade,
  kind            source_kind not null,
  title           text,
  uri             text,                        -- url or storage path
  raw_text        text,
  meta            jsonb default '{}'::jsonb,   -- duration_s, published_at, platform, metrics snapshot
  ingest_status   text default 'pending',      -- pending|processing|ready|failed
  ingest_error    text,
  created_at      timestamptz default now()
);

-- Everything the creator has made or published (library). Published posts imported via CSV/links land here.
create table library_items (
  id              uuid primary key default gen_random_uuid(),
  creator_id      uuid not null references creators(id) on delete cascade,
  source_id       uuid references sources(id) on delete set null,
  asset_id        uuid,                        -- if it originated from a CreatorOS asset
  platform        platform,
  title           text,
  body            text,
  published_at    timestamptz,
  topics          text[] default '{}',
  format          text,                        -- reel, long_video, post, thread, podcast_episode...
  created_at      timestamptz default now()
);

-- Chunks for RAG. ONE embedding model and ONE dimension for the whole platform.
create table chunks (
  id              uuid primary key default gen_random_uuid(),
  creator_id      uuid not null references creators(id) on delete cascade,
  source_id       uuid references sources(id) on delete cascade,
  library_item_id uuid references library_items(id) on delete cascade,
  ord             int not null,
  text            text not null,
  start_s         numeric,                     -- for transcripts (clips, citations)
  end_s           numeric,
  embedding       vector(768) not null,        -- change dimension ONLY here + EMBEDDING_DIM env
  tsv             tsvector generated always as (to_tsvector('simple', text)) stored,
  meta            jsonb default '{}'::jsonb
);
create index chunks_embedding_idx on chunks using hnsw (embedding vector_cosine_ops);
create index chunks_tsv_idx on chunks using gin (tsv);
create index chunks_creator_idx on chunks (creator_id);

-- ---------- core aggregate ----------
create table campaigns (
  id              uuid primary key default gen_random_uuid(),
  creator_id      uuid not null references creators(id) on delete cascade,
  code            text,                        -- human id e.g. CNT-1024
  title           text not null,
  topic           text,
  objective       objective default 'audience_growth',
  origin          text default 'idea',         -- idea|trend|comment|analytics|recycle|upload|autopilot
  origin_ref      uuid,                        -- opportunity / source / library_item id
  master_format   text,                        -- reel_60, youtube_long, podcast_episode, linkedin_post...
  primary_platform platform,
  platforms       platform[] default '{}',
  status          campaign_status default 'idea',
  brief           jsonb default '{}'::jsonb,   -- chosen angle, audience, key message
  voice_profile_version int,
  created_at      timestamptz default now(),
  updated_at      timestamptz default now()
);
create index campaigns_creator_idx on campaigns (creator_id, updated_at desc);

create table assets (
  id              uuid primary key default gen_random_uuid(),
  creator_id      uuid not null references creators(id) on delete cascade,
  campaign_id     uuid references campaigns(id) on delete cascade,   -- null allowed for quick-mode outputs
  kind            text not null,
  platform        platform,
  title           text,
  content         jsonb not null,              -- validated by the capability's output schema
  status          asset_status default 'draft',
  current_version int default 1,
  produced_by     text,                        -- capability name
  run_id          uuid,
  judge_overall   numeric,                     -- denormalized latest judge score for fast UI badges
  position        int default 0,
  created_at      timestamptz default now(),
  updated_at      timestamptz default now()
);
create index assets_campaign_idx on assets (campaign_id, kind);

create table asset_versions (
  id              uuid primary key default gen_random_uuid(),
  asset_id        uuid not null references assets(id) on delete cascade,
  version         int not null,
  content         jsonb not null,
  edited_by       text not null,               -- 'ai:<capability>' | 'user'
  edit_note       text,
  created_at      timestamptz default now(),
  unique (asset_id, version)
);

-- ---------- discovery & intelligence ----------
create table opportunities (
  id              uuid primary key default gen_random_uuid(),
  creator_id      uuid not null references creators(id) on delete cascade,
  kind            text not null,               -- trend|audience_question|analytics|recycle|library_gap|strategy
  title           text not null,
  rationale       jsonb default '[]'::jsonb,   -- ["audience engages with AI basics", ...]
  score           numeric,                     -- 0..100 potential
  evidence        jsonb default '{}'::jsonb,   -- ids of comments/metrics/chunks backing it
  status          text default 'new',          -- new|saved|dismissed|converted
  campaign_id     uuid references campaigns(id),
  expires_at      timestamptz,
  created_at      timestamptz default now()
);

create table comments (
  id              uuid primary key default gen_random_uuid(),
  creator_id      uuid not null references creators(id) on delete cascade,
  library_item_id uuid references library_items(id) on delete cascade,
  author          text,
  text            text not null,
  likes           int default 0,
  posted_at       timestamptz,
  sentiment       text,                        -- positive|neutral|negative
  intent          text,                        -- question|praise|complaint|request|spam|other
  cluster_id      uuid,
  created_at      timestamptz default now()
);

create table comment_clusters (
  id              uuid primary key default gen_random_uuid(),
  creator_id      uuid not null references creators(id) on delete cascade,
  label           text not null,
  summary         text,
  size            int default 0,
  representative  text[],
  created_at      timestamptz default now()
);

create table performance_metrics (
  id              uuid primary key default gen_random_uuid(),
  creator_id      uuid not null references creators(id) on delete cascade,
  library_item_id uuid references library_items(id) on delete cascade,
  captured_at     timestamptz default now(),
  views           bigint, likes bigint, comments bigint, shares bigint, saves bigint,
  watch_time_s    bigint, avg_view_duration_s numeric, retention_3s numeric, ctr numeric,
  followers_gained int,
  raw             jsonb default '{}'::jsonb
);

create table insights (
  id              uuid primary key default gen_random_uuid(),
  creator_id      uuid not null references creators(id) on delete cascade,
  kind            text not null,               -- performance|audience|voice|strategy
  statement       text not null,               -- "30-60s explainers outperform long posts"
  evidence        jsonb default '{}'::jsonb,
  confidence      numeric,
  applied_count   int default 0,               -- how often the Director used it (closed loop proof)
  active          boolean default true,
  created_at      timestamptz default now()
);

-- ---------- planning ----------
create table calendar_entries (
  id              uuid primary key default gen_random_uuid(),
  creator_id      uuid not null references creators(id) on delete cascade,
  campaign_id     uuid references campaigns(id) on delete cascade,
  asset_id        uuid references assets(id) on delete set null,
  platform        platform not null,
  scheduled_for   timestamptz not null,
  status          text default 'planned',      -- planned|ready|published|skipped
  note            text
);

-- ---------- business ----------
create table brand_pitches (
  id              uuid primary key default gen_random_uuid(),
  creator_id      uuid not null references creators(id) on delete cascade,
  brand_name      text not null,
  brand_info      jsonb default '{}'::jsonb,
  proposal        jsonb default '{}'::jsonb,   -- sections, packages, subject lines
  alignment_score numeric,
  status          text default 'draft',
  created_at      timestamptz default now()
);

create table collaborator_profiles (          -- seed dataset of creators to match against (#26)
  id              uuid primary key default gen_random_uuid(),
  name            text not null,
  niche           text,
  platforms       platform[],
  audience_size   int,
  location        text,
  topics          text[],
  embedding       vector(768)
);

-- ---------- screenplay (#20) ----------
create table story_bibles (
  id              uuid primary key default gen_random_uuid(),
  creator_id      uuid not null references creators(id) on delete cascade,
  campaign_id     uuid references campaigns(id) on delete cascade,
  characters      jsonb default '[]'::jsonb,
  locations       jsonb default '[]'::jsonb,
  timeline        jsonb default '[]'::jsonb,
  rules           jsonb default '[]'::jsonb,
  updated_at      timestamptz default now()
);

-- ---------- agent runs, judging, feedback ----------
create table agent_runs (
  id              uuid primary key default gen_random_uuid(),
  creator_id      uuid not null references creators(id) on delete cascade,
  campaign_id     uuid references campaigns(id) on delete cascade,
  mode            run_mode not null,
  capability      text,                        -- for quick/studio mode
  input           jsonb not null,
  status          run_status default 'queued',
  langsmith_run_id text,                       -- deep link into LangSmith trace
  thread_id       text,                        -- LangGraph checkpointer thread
  started_at      timestamptz,
  finished_at     timestamptz,
  latency_ms      int,
  tokens_in       int default 0,
  tokens_out      int default 0,
  cost_usd        numeric default 0,
  error           text,
  created_at      timestamptz default now()
);

create table run_events (                      -- persisted SSE events (replay after reconnect)
  id              bigserial primary key,
  run_id          uuid not null references agent_runs(id) on delete cascade,
  seq             int not null,
  type            text not null,
  payload         jsonb not null,
  created_at      timestamptz default now(),
  unique (run_id, seq)
);

create table judge_scores (
  id              uuid primary key default gen_random_uuid(),
  asset_id        uuid references assets(id) on delete cascade,
  run_id          uuid references agent_runs(id) on delete cascade,
  capability      text not null,
  rubric_id       text not null,
  rubric_version  text not null,
  judge_model     text not null,
  scores          jsonb not null,              -- {criterion: 1..5}
  overall         numeric not null,
  passed          boolean not null,
  critique        text,
  deterministic   jsonb default '{}'::jsonb,   -- validator results
  created_at      timestamptz default now()
);

create table feedback (
  id              uuid primary key default gen_random_uuid(),
  creator_id      uuid not null references creators(id) on delete cascade,
  asset_id        uuid references assets(id) on delete cascade,
  run_id          uuid references agent_runs(id) on delete cascade,
  signal          text not null,               -- thumbs_up|thumbs_down|regenerate|edited|accepted|copied|exported
  value           numeric,                     -- e.g. edit distance ratio
  comment         text,
  created_at      timestamptz default now()
);

create table llm_cache (
  key             text primary key,            -- sha256(capability|prompt_version|model|input|voice_version)
  response        jsonb not null,
  created_at      timestamptz default now(),
  expires_at      timestamptz
);

create table jobs (                            -- fallback queue if Redis is unavailable
  id              uuid primary key default gen_random_uuid(),
  kind            text not null,
  payload         jsonb not null,
  status          text default 'queued',
  attempts        int default 0,
  progress        numeric default 0,
  error           text,
  run_after       timestamptz default now(),
  created_at      timestamptz default now()
);

-- ---------- hybrid search helper ----------
create or replace function match_chunks(p_creator uuid, p_query vector(768), p_query_text text, p_k int default 12)
returns table (id uuid, text text, source_id uuid, library_item_id uuid, start_s numeric, end_s numeric, score float)
language sql stable as $$
  with v as (
    select c.id, 1 - (c.embedding <=> p_query) as vscore
    from chunks c where c.creator_id = p_creator
    order by c.embedding <=> p_query limit p_k * 3
  ), t as (
    select c.id, ts_rank(c.tsv, plainto_tsquery('simple', p_query_text)) as tscore
    from chunks c where c.creator_id = p_creator and c.tsv @@ plainto_tsquery('simple', p_query_text)
    limit p_k * 3
  )
  select c.id, c.text, c.source_id, c.library_item_id, c.start_s, c.end_s,
         coalesce(v.vscore,0) * 0.75 + coalesce(t.tscore,0) * 0.25 as score
  from chunks c
  left join v on v.id = c.id
  left join t on t.id = c.id
  where c.id in (select id from v union select id from t)
  order by score desc limit p_k;
$$;

-- ---------- RLS (pattern — repeat for every creator-scoped table) ----------
alter table campaigns enable row level security;
create policy campaigns_owner on campaigns
  using (creator_id in (select id from creators where auth_user_id = auth.uid()))
  with check (creator_id in (select id from creators where auth_user_id = auth.uid()));
-- NOTE: the FastAPI backend connects with the service role and MUST filter by creator_id in every query
-- (enforced in the repository layer). RLS protects any direct-from-browser Supabase access.
