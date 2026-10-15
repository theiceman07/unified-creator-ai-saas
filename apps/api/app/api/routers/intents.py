from fastapi import APIRouter
from pydantic import BaseModel

from app.orchestration.intent_router import IntentRoute, route_intent

router = APIRouter(prefix="/v1/intents", tags=["intents"])

class IntentRequest(BaseModel):
    text: str

@router.post("", response_model=IntentRoute)
async def classify_intent(request: IntentRequest):
    return await route_intent(request.text)
