import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.models import Creator


class CreatorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, creator_id: str) -> Creator | None:
        result = await self.session.execute(
            select(Creator).where(Creator.id == uuid.UUID(creator_id))
        )
        return result.scalar_one_or_none()
