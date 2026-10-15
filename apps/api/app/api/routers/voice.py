from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.auth import current_creator

router = APIRouter(prefix="/v1/voice_profiles", tags=["voice_profiles"])

class VoiceProfileRequest(BaseModel):
    brand_rules: dict[str, Any]

@router.get("/active")
async def get_active_profile(creator_id: str = Depends(current_creator)):
    # Stub: Return a hardcoded active voice profile
    return {
        "id": "123",
        "version": 1,
        "profile": {"tone": "authoritative", "style": "punchy"},
        "is_active": True
    }

@router.post("")
async def create_voice_profile(req: VoiceProfileRequest, creator_id: str = Depends(current_creator)):
    return {"status": "created", "version": 2}
