from typing import Any

from app.capabilities._base import Capability
from app.capabilities._schemas.models import CapabilityResult, Card, RunContext


class HookCapability(Capability):
    async def invoke(self, context: RunContext, input_data: dict[str, Any]) -> CapabilityResult:
        # Stub implementation
        card = Card(kind="hook", data={"hooks": ["ChatGPT isn't an agent. Here's why."]})
        return CapabilityResult(cards=[card], assets=[{"kind": "hook", "content": card.data}])
