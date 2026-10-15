from typing import List, Optional

from pydantic import BaseModel, Field


class Hook(BaseModel):
    text: str
    style: str

class Script(BaseModel):
    title: str
    body: str
    hook_ref: str | None = None

class PlatformPost(BaseModel):
    platform: str
    body: str

class PlatformLimits(BaseModel):
    max_length: int

class ResearchBrief(BaseModel):
    topic: str
    summary: str
    sources: list[str]

class CreatorContext(BaseModel):
    creator_id: str
    display_name: str
    recent_ctas: list[str] = Field(default_factory=list)
