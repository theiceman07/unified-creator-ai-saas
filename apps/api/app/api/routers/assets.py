
from fastapi import APIRouter, Depends

from app.api.schemas.common import AssetResponse
from app.core.auth import current_creator
from app.db.repositories.asset_repo import AssetRepository
from app.db.session import get_session

router = APIRouter(prefix="/v1/assets", tags=["assets"])

@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: str, creator_id: str = Depends(current_creator), session = Depends(get_session)):
    repo = AssetRepository(session, creator_id)
    return await repo.get_by_id(asset_id)
