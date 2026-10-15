from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class Card(BaseModel):
    kind: str
    data: dict[str, Any]

class Citation(BaseModel):
    source_id: str
    text_snippet: str
    timestamp_s: float | None = None

class CapabilityResult(BaseModel):
    cards: list[Card] = Field(default_factory=list)
    assets: list[dict[str, Any]] = Field(default_factory=list)
    state_updates: dict[str, Any] = Field(default_factory=dict)

class RunContext(BaseModel):
    run_id: UUID
    creator_id: UUID
    campaign_id: UUID | None = None
    mode: str
