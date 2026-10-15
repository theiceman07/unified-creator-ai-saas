from typing import Any

from app.capabilities._schemas.models import CapabilityResult, RunContext
from app.orchestration.registry import registry


async def run_capability(capability_name: str, context: RunContext, input_data: dict[str, Any]) -> CapabilityResult:
    # 1. Tracing start
    print(f"Running capability: {capability_name} in mode: {context.mode}")
    
    # 2. Load capability
    cap = registry.get_capability(capability_name)
    
    # 3. Execute
    try:
        result = await cap.invoke(context, input_data)
        return result
    except Exception as e:
        # 4. Tracing error & fail event
        print(f"Error in {capability_name}: {e}")
        raise
