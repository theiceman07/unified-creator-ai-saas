from typing import Any

from app.capabilities._base import Capability
from app.capabilities._schemas.models import CapabilityResult, Card, RunContext


class ScriptCapability(Capability):
    async def invoke(self, context: RunContext, input_data: dict[str, Any]) -> CapabilityResult:
        # Stub implementation
        script_text = "HOOK: ChatGPT isn't an agent.\nBODY: Here is the difference..."
        card = Card(kind="script", data={"script": script_text})
        return CapabilityResult(cards=[card], assets=[{"kind": "script", "content": card.data}])
