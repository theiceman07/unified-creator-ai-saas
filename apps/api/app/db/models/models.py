import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Creator(Base):
    __tablename__ = 'creators'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    auth_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), unique=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    handle: Mapped[str | None] = mapped_column(Text)
    niche: Mapped[str | None] = mapped_column(Text)
    creator_types: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default='{}')
    platforms: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default='{}')
    goals: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default='{}')
    timezone: Mapped[str] = mapped_column(Text, server_default='Asia/Kolkata')
    languages: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default='{en}')
    is_demo: Mapped[bool] = mapped_column(Boolean, server_default='false')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

class VoiceProfile(Base):
    __tablename__ = 'voice_profiles'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('creators.id', ondelete='CASCADE'), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    profile: Mapped[dict] = mapped_column(JSONB, nullable=False)
    brand_rules: Mapped[dict | None] = mapped_column(JSONB, server_default='{}')
    example_ids: Mapped[list[uuid.UUID]] = mapped_column(ARRAY(UUID(as_uuid=True)), server_default='{}')
    is_active: Mapped[bool] = mapped_column(Boolean, server_default='true')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    __table_args__ = (UniqueConstraint('creator_id', 'version', name='uq_voice_profile_version'),)

class CreatorStrategy(Base):
    __tablename__ = 'creator_strategy'
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('creators.id', ondelete='CASCADE'), primary_key=True)
    audience: Mapped[dict | None] = mapped_column(JSONB, server_default='{}')
    pillars: Mapped[dict | None] = mapped_column(JSONB, server_default='[]')
    cadence: Mapped[dict | None] = mapped_column(JSONB, server_default='{}')
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

class Source(Base):
    __tablename__ = 'sources'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('creators.id', ondelete='CASCADE'), nullable=False)
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str | None] = mapped_column(Text)
    uri: Mapped[str | None] = mapped_column(Text)
    raw_text: Mapped[str | None] = mapped_column(Text)
    meta_data: Mapped[dict | None] = mapped_column("meta", JSONB, server_default='{}')
    ingest_status: Mapped[str | None] = mapped_column(Text, server_default='pending')
    ingest_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

class LibraryItem(Base):
    __tablename__ = 'library_items'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('creators.id', ondelete='CASCADE'), nullable=False)
    source_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('sources.id', ondelete='SET NULL'))
    asset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    platform: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(Text)
    body: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    topics: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default='{}')
    format: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

class Chunk(Base):
    __tablename__ = 'chunks'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('creators.id', ondelete='CASCADE'), nullable=False)
    source_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('sources.id', ondelete='CASCADE'))
    library_item_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('library_items.id', ondelete='CASCADE'))
    ord: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    start_s: Mapped[float | None] = mapped_column(Numeric)
    end_s: Mapped[float | None] = mapped_column(Numeric)
    embedding: Mapped[Any] = mapped_column(Vector(768), nullable=False)
    tsv: Mapped[Any] = mapped_column(TSVECTOR)
    meta_data: Mapped[dict | None] = mapped_column("meta", JSONB, server_default='{}')

class Campaign(Base):
    __tablename__ = 'campaigns'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('creators.id', ondelete='CASCADE'), nullable=False)
    code: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    topic: Mapped[str | None] = mapped_column(Text)
    objective: Mapped[str | None] = mapped_column(Text, server_default='audience_growth')
    origin: Mapped[str | None] = mapped_column(Text, server_default='idea')
    origin_ref: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    master_format: Mapped[str | None] = mapped_column(Text)
    primary_platform: Mapped[str | None] = mapped_column(Text)
    platforms: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default='{}')
    status: Mapped[str | None] = mapped_column(Text, server_default='idea')
    brief: Mapped[dict] = mapped_column(JSONB, server_default='{}')
    voice_profile_version: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

class Asset(Base):
    __tablename__ = 'assets'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('creators.id', ondelete='CASCADE'), nullable=False)
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('campaigns.id', ondelete='CASCADE'))
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    platform: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(Text)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str | None] = mapped_column(Text, server_default='draft')
    current_version: Mapped[int | None] = mapped_column(Integer, server_default='1')
    produced_by: Mapped[str | None] = mapped_column(Text)
    run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    judge_overall: Mapped[float | None] = mapped_column(Numeric)
    position: Mapped[int | None] = mapped_column(Integer, server_default='0')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

class AssetVersion(Base):
    __tablename__ = 'asset_versions'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('assets.id', ondelete='CASCADE'), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    edited_by: Mapped[str] = mapped_column(Text, nullable=False)
    edit_note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    __table_args__ = (UniqueConstraint('asset_id', 'version', name='uq_asset_version'),)

class Opportunity(Base):
    __tablename__ = 'opportunities'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('creators.id', ondelete='CASCADE'), nullable=False)
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[dict | None] = mapped_column(JSONB, server_default='[]')
    score: Mapped[float | None] = mapped_column(Numeric)
    evidence: Mapped[dict | None] = mapped_column(JSONB, server_default='{}')
    status: Mapped[str | None] = mapped_column(Text, server_default='new')
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('campaigns.id'))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

class Comment(Base):
    __tablename__ = 'comments'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('creators.id', ondelete='CASCADE'), nullable=False)
    library_item_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('library_items.id', ondelete='CASCADE'))
    author: Mapped[str | None] = mapped_column(Text)
    text_content: Mapped[str] = mapped_column("text", Text, nullable=False)
    likes: Mapped[int | None] = mapped_column(Integer, server_default='0')
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sentiment: Mapped[str | None] = mapped_column(Text)
    intent: Mapped[str | None] = mapped_column(Text)
    cluster_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

class CommentCluster(Base):
    __tablename__ = 'comment_clusters'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('creators.id', ondelete='CASCADE'), nullable=False)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    size: Mapped[int | None] = mapped_column(Integer, server_default='0')
    representative: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

class PerformanceMetric(Base):
    __tablename__ = 'performance_metrics'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('creators.id', ondelete='CASCADE'), nullable=False)
    library_item_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('library_items.id', ondelete='CASCADE'))
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    views: Mapped[int | None] = mapped_column(BigInteger)
    likes: Mapped[int | None] = mapped_column(BigInteger)
    comments: Mapped[int | None] = mapped_column(BigInteger)
    shares: Mapped[int | None] = mapped_column(BigInteger)
    saves: Mapped[int | None] = mapped_column(BigInteger)
    watch_time_s: Mapped[int | None] = mapped_column(BigInteger)
    avg_view_duration_s: Mapped[float | None] = mapped_column(Numeric)
    retention_3s: Mapped[float | None] = mapped_column(Numeric)
    ctr: Mapped[float | None] = mapped_column(Numeric)
    followers_gained: Mapped[int | None] = mapped_column(Integer)
    raw: Mapped[dict | None] = mapped_column(JSONB, server_default='{}')

class Insight(Base):
    __tablename__ = 'insights'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('creators.id', ondelete='CASCADE'), nullable=False)
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[dict | None] = mapped_column(JSONB, server_default='{}')
    confidence: Mapped[float | None] = mapped_column(Numeric)
    applied_count: Mapped[int | None] = mapped_column(Integer, server_default='0')
    active: Mapped[bool] = mapped_column(Boolean, server_default='true')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

class CalendarEntry(Base):
    __tablename__ = 'calendar_entries'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('creators.id', ondelete='CASCADE'), nullable=False)
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('campaigns.id', ondelete='CASCADE'))
    asset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('assets.id', ondelete='SET NULL'))
    platform: Mapped[str] = mapped_column(Text, nullable=False)
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str | None] = mapped_column(Text, server_default='planned')
    note: Mapped[str | None] = mapped_column(Text)

class BrandPitch(Base):
    __tablename__ = 'brand_pitches'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('creators.id', ondelete='CASCADE'), nullable=False)
    brand_name: Mapped[str] = mapped_column(Text, nullable=False)
    brand_info: Mapped[dict | None] = mapped_column(JSONB, server_default='{}')
    proposal: Mapped[dict | None] = mapped_column(JSONB, server_default='{}')
    alignment_score: Mapped[float | None] = mapped_column(Numeric)
    status: Mapped[str | None] = mapped_column(Text, server_default='draft')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

class CollaboratorProfile(Base):
    __tablename__ = 'collaborator_profiles'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name: Mapped[str] = mapped_column(Text, nullable=False)
    niche: Mapped[str | None] = mapped_column(Text)
    platforms: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default='{}')
    audience_size: Mapped[int | None] = mapped_column(Integer)
    location: Mapped[str | None] = mapped_column(Text)
    topics: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default='{}')
    embedding: Mapped[Any | None] = mapped_column(Vector(768))

class StoryBible(Base):
    __tablename__ = 'story_bibles'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('creators.id', ondelete='CASCADE'), nullable=False)
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('campaigns.id', ondelete='CASCADE'))
    characters: Mapped[dict | None] = mapped_column(JSONB, server_default='[]')
    locations: Mapped[dict | None] = mapped_column(JSONB, server_default='[]')
    timeline: Mapped[dict | None] = mapped_column(JSONB, server_default='[]')
    rules: Mapped[dict | None] = mapped_column(JSONB, server_default='[]')
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

class AgentRun(Base):
    __tablename__ = 'agent_runs'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('creators.id', ondelete='CASCADE'), nullable=False)
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('campaigns.id', ondelete='CASCADE'))
    mode: Mapped[str] = mapped_column(Text, nullable=False)
    capability: Mapped[str | None] = mapped_column(Text)
    input: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str | None] = mapped_column(Text, server_default='queued')
    langsmith_run_id: Mapped[str | None] = mapped_column(Text)
    thread_id: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    tokens_in: Mapped[int | None] = mapped_column(Integer, server_default='0')
    tokens_out: Mapped[int | None] = mapped_column(Integer, server_default='0')
    cost_usd: Mapped[float | None] = mapped_column(Numeric, server_default='0')
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

class RunEvent(Base):
    __tablename__ = 'run_events'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('agent_runs.id', ondelete='CASCADE'), nullable=False)
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    __table_args__ = (UniqueConstraint('run_id', 'seq', name='uq_run_event'),)

class JudgeScore(Base):
    __tablename__ = 'judge_scores'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    asset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('assets.id', ondelete='CASCADE'))
    run_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('agent_runs.id', ondelete='CASCADE'))
    capability: Mapped[str] = mapped_column(Text, nullable=False)
    rubric_id: Mapped[str] = mapped_column(Text, nullable=False)
    rubric_version: Mapped[str] = mapped_column(Text, nullable=False)
    judge_model: Mapped[str] = mapped_column(Text, nullable=False)
    scores: Mapped[dict] = mapped_column(JSONB, nullable=False)
    overall: Mapped[float] = mapped_column(Numeric, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    critique: Mapped[str | None] = mapped_column(Text)
    deterministic: Mapped[dict | None] = mapped_column(JSONB, server_default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

class Feedback(Base):
    __tablename__ = 'feedback'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('creators.id', ondelete='CASCADE'), nullable=False)
    asset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('assets.id', ondelete='CASCADE'))
    run_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('agent_runs.id', ondelete='CASCADE'))
    signal: Mapped[str] = mapped_column(Text, nullable=False)
    value: Mapped[float | None] = mapped_column(Numeric)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

class LlmCache(Base):
    __tablename__ = 'llm_cache'
    key: Mapped[str] = mapped_column(Text, primary_key=True)
    response: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

class Job(Base):
    __tablename__ = 'jobs'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str | None] = mapped_column(Text, server_default='queued')
    attempts: Mapped[int | None] = mapped_column(Integer, server_default='0')
    progress: Mapped[float | None] = mapped_column(Numeric, server_default='0')
    error: Mapped[str | None] = mapped_column(Text)
    run_after: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
