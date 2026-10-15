import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.db.models.models import Campaign


class CampaignRepository:
    def __init__(self, session: AsyncSession, creator_id: str):
        self.session = session
        self.creator_id = uuid.UUID(creator_id)

    async def get_by_id(self, campaign_id: str) -> Campaign:
        result = await self.session.execute(
            select(Campaign).where(
                Campaign.id == uuid.UUID(campaign_id),
                Campaign.creator_id == self.creator_id
            )
        )
        campaign = result.scalar_one_or_none()
        if not campaign:
            raise NotFoundError(f"Campaign {campaign_id} not found")
        return campaign

    async def list_all(self) -> list[Campaign]:
        result = await self.session.execute(
            select(Campaign).where(Campaign.creator_id == self.creator_id)
        )
        return list(result.scalars().all())

    async def create(self, campaign_data: dict) -> Campaign:
        campaign = Campaign(creator_id=self.creator_id, **campaign_data)
        self.session.add(campaign)
        await self.session.commit()
        await self.session.refresh(campaign)
        return campaign
