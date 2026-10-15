from fastapi import APIRouter, Depends

from app.api.schemas.common import CreatorResponse
from app.core.auth import current_creator
from app.db.repositories.creator_repo import CreatorRepository
from app.db.session import get_session

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
