from abc import ABC, abstractmethod
from typing import Any

from app.capabilities._schemas.models import CapabilityResult, RunContext


class Capability(ABC):
    @abstractmethod
    async def invoke(self, context: RunContext, input_data: dict[str, Any]) -> CapabilityResult:
        pass
