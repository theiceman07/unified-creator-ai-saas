import os


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")

# --- 1. Repositories ---

write_file('app/db/repositories/creator_repo.py', """
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.models import Creator
import uuid
from typing import Optional

class CreatorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, creator_id: str) -> Optional[Creator]:
        result = await self.session.execute(
            select(Creator).where(Creator.id == uuid.UUID(creator_id))
        )
        return result.scalar_one_or_none()
""")

write_file('app/db/repositories/asset_repo.py', """
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.models.models import Asset, AssetVersion
import uuid
from typing import List, Optional
from app.core.errors import NotFoundError

class AssetRepository:
    def __init__(self, session: AsyncSession, creator_id: str):
        self.session = session
        self.creator_id = uuid.UUID(creator_id)

    async def get_by_id(self, asset_id: str) -> Asset:
        result = await self.session.execute(
            select(Asset).where(
                Asset.id == uuid.UUID(asset_id),
                Asset.creator_id == self.creator_id
            )
        )
        asset = result.scalar_one_or_none()
        if not asset:
            raise NotFoundError(f"Asset {asset_id} not found")
        return asset

    async def list_by_campaign(self, campaign_id: str) -> List[Asset]:
        result = await self.session.execute(
            select(Asset).where(
                Asset.campaign_id == uuid.UUID(campaign_id),
                Asset.creator_id == self.creator_id
            )
        )
        return list(result.scalars().all())
""")

# --- 2. Schemas ---
write_file('app/api/schemas/common.py', """
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class CreatorResponse(ORMModel):
    id: UUID
    display_name: str
    platforms: List[str]
    goals: List[str]
    is_demo: bool

class CampaignCreate(BaseModel):
    title: str
    topic: Optional[str] = None
    objective: Optional[str] = 'audience_growth'
    primary_platform: Optional[str] = None

class CampaignResponse(ORMModel):
    id: UUID
    title: str
    status: Optional[str]
    created_at: datetime

class AssetResponse(ORMModel):
    id: UUID
    kind: str
    content: Dict[str, Any]
    status: Optional[str]
    created_at: datetime
""")

# --- 3. Routers ---
write_file('app/api/routers/auth.py', """
from fastapi import APIRouter, Depends
from app.core.auth import current_creator, create_access_token
from app.db.session import get_session
from app.db.repositories.creator_repo import CreatorRepository
from app.api.schemas.common import CreatorResponse

router = APIRouter(prefix="/v1", tags=["auth"])

@router.post("/demo/login")
async def demo_login():
    # Hardcoded demo login returning a token for testing
    return {"access_token": "demo-token-123"}

@router.get("/me", response_model=CreatorResponse)
async def get_me(creator_id: str = Depends(current_creator), session = Depends(get_session)):
    repo = CreatorRepository(session)
    creator = await repo.get_by_id(creator_id)
    return creator
""")

write_file('app/api/routers/campaigns.py', """
from fastapi import APIRouter, Depends
from typing import List
from app.core.auth import current_creator
from app.db.session import get_session
from app.db.repositories.campaign_repo import CampaignRepository
from app.api.schemas.common import CampaignCreate, CampaignResponse

router = APIRouter(prefix="/v1/campaigns", tags=["campaigns"])

@router.get("", response_model=List[CampaignResponse])
async def list_campaigns(creator_id: str = Depends(current_creator), session = Depends(get_session)):
    repo = CampaignRepository(session, creator_id)
    return await repo.list_all()

@router.post("", response_model=CampaignResponse)
async def create_campaign(campaign: CampaignCreate, creator_id: str = Depends(current_creator), session = Depends(get_session)):
    repo = CampaignRepository(session, creator_id)
    return await repo.create(campaign.model_dump())
""")

write_file('app/api/routers/assets.py', """
from fastapi import APIRouter, Depends
from typing import List
from app.core.auth import current_creator
from app.db.session import get_session
from app.db.repositories.asset_repo import AssetRepository
from app.api.schemas.common import AssetResponse

router = APIRouter(prefix="/v1/assets", tags=["assets"])

@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: str, creator_id: str = Depends(current_creator), session = Depends(get_session)):
    repo = AssetRepository(session, creator_id)
    return await repo.get_by_id(asset_id)
""")

# --- 4. FakeLLM ---
write_file('app/platform/llm/gateway.py', """
from typing import Dict, Any, Type
from pydantic import BaseModel

class FakeLLM:
    async def generate_structured(self, prompt: str, schema: Type[BaseModel], **kwargs) -> BaseModel:
        # Returns a dummy populated model for testing
        dummy_data = {}
        for field_name, field in schema.model_fields.items():
            if field.annotation == str:
                dummy_data[field_name] = "dummy text"
            elif field.annotation == int:
                dummy_data[field_name] = 1
            elif field.annotation == list or getattr(field.annotation, '__origin__', None) == list:
                dummy_data[field_name] = []
            else:
                dummy_data[field_name] = None
        return schema(**dummy_data)

gateway = FakeLLM()
""")

print("Phase 1 files generated.")
