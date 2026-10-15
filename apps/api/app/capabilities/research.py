from typing import Any

from app.capabilities._base import Capability
from app.capabilities._schemas.models import CapabilityResult, Card, RunContext


class ResearchCapability(Capability):
    async def invoke(self, context: RunContext, input_data: dict[str, Any]) -> CapabilityResult:
        # Stub implementation
        card = Card(kind="research_brief", data={"facts": ["AI agents are autonomous", "LangGraph simplifies orchestration"]})
        return CapabilityResult(cards=[card], assets=[{"kind": "research_brief", "content": card.data}])
