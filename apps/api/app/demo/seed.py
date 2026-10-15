import asyncio
import uuid

from app.db.models.models import Campaign, Creator, VoiceProfile
from app.db.session import SessionLocal


async def seed_db():
    async with SessionLocal() as session:
        # Create demo creator
        creator_id = uuid.uuid4()
        creator = Creator(
            id=creator_id,
            display_name="Demo Creator",
            is_demo=True,
            platforms=["youtube", "x"],
            goals=["audience_growth"]
        )
        session.add(creator)
        
        # Create voice profile
        voice = VoiceProfile(
            creator_id=creator_id,
            version=1,
            profile={"tone": "casual", "format": "hook_first"},
            is_active=True
        )
        session.add(voice)
        
        # Create test campaign
        campaign = Campaign(
            creator_id=creator_id,
            title="AI Agents for Beginners",
            topic="AI Agents",
            status="idea"
        )
        session.add(campaign)
        
        await session.commit()
        print("Database seeded with Demo Creator.")

if __name__ == "__main__":
    asyncio.run(seed_db())
