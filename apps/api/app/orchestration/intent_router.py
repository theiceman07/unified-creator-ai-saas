from typing import Any

from pydantic import BaseModel


class IntentRoute(BaseModel):
    intent: str  # campaign | quick | brain | ingest
    confidence: float
    parameters: dict[str, Any]

async def route_intent(text: str) -> IntentRoute:
    # Dummy router: just route to campaign
    return IntentRoute(
        intent="campaign",
        confidence=0.9,
        parameters={"topic": text}
    )
