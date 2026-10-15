
from fastapi import APIRouter, Depends

from app.api.schemas.common import CampaignCreate, CampaignResponse
from app.core.auth import current_creator
from app.db.repositories.campaign_repo import CampaignRepository
from app.db.session import get_session

router = APIRouter(prefix="/v1/campaigns", tags=["campaigns"])

@router.get("", response_model=list[CampaignResponse])
async def list_campaigns(creator_id: str = Depends(current_creator), session = Depends(get_session)):
    repo = CampaignRepository(session, creator_id)
    return await repo.list_all()

@router.post("", response_model=CampaignResponse)
async def create_campaign(campaign: CampaignCreate, creator_id: str = Depends(current_creator), session = Depends(get_session)):
    repo = CampaignRepository(session, creator_id)
    return await repo.create(campaign.model_dump())
