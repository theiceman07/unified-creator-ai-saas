from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class CreatorResponse(ORMModel):
    id: UUID
    display_name: str
    platforms: list[str]
    goals: list[str]
    is_demo: bool

class CampaignCreate(BaseModel):
    title: str
    topic: str | None = None
    objective: str | None = 'audience_growth'
    primary_platform: str | None = None

class CampaignResponse(ORMModel):
    id: UUID
    title: str
    status: str | None
    created_at: datetime

class AssetResponse(ORMModel):
    id: UUID
    kind: str
    content: dict[str, Any]
    status: str | None
    created_at: datetime
