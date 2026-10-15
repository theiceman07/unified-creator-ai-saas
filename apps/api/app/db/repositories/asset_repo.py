import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.db.models.models import Asset


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

    async def list_by_campaign(self, campaign_id: str) -> list[Asset]:
        result = await self.session.execute(
            select(Asset).where(
                Asset.campaign_id == uuid.UUID(campaign_id),
                Asset.creator_id == self.creator_id
            )
        )
        return list(result.scalars().all())
