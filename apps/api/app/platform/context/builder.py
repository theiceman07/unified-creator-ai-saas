from app.capabilities._schemas import CreatorContext


async def build_creator_context(creator_id: str) -> CreatorContext:
    """Constructs the CreatorContext containing pillars, voice, etc."""
    return CreatorContext(
        creator_id=creator_id,
        display_name="Demo Creator",
        recent_ctas=["Subscribe for more!", "Drop a comment below!"]
    )
