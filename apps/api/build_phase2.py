import os


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")

# --- 1. Schemas & Base Capability ---
write_file('app/capabilities/_schemas/models.py', """
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from uuid import UUID

class Card(BaseModel):
    kind: str
    data: Dict[str, Any]

class Citation(BaseModel):
    source_id: str
    text_snippet: str
    timestamp_s: Optional[float] = None

class CapabilityResult(BaseModel):
    cards: List[Card] = Field(default_factory=list)
    assets: List[Dict[str, Any]] = Field(default_factory=list)
    state_updates: Dict[str, Any] = Field(default_factory=dict)

class RunContext(BaseModel):
    run_id: UUID
    creator_id: UUID
    campaign_id: Optional[UUID] = None
    mode: str
""")

write_file('app/capabilities/_base.py', """
from abc import ABC, abstractmethod
from typing import Any, Dict
from app.capabilities._schemas.models import RunContext, CapabilityResult

class Capability(ABC):
    @abstractmethod
    async def invoke(self, context: RunContext, input_data: Dict[str, Any]) -> CapabilityResult:
        pass
""")

# --- 2. Registry ---
write_file('app/orchestration/registry.py', """
import yaml
import os
from typing import Dict, Any, Type
from app.capabilities._base import Capability

class Registry:
    def __init__(self):
        self.capabilities = {}
    
    def load(self, registry_path: str):
        with open(registry_path, 'r') as f:
            data = yaml.safe_load(f)
        for cap in data.get('capabilities', []):
            name = cap['name']
            self.capabilities[name] = {"config": cap, "class": None}

    def get_capability(self, name: str) -> Capability:
        if name not in self.capabilities:
            raise ValueError(f"Capability {name} not found in registry")
        cap_class = self.capabilities[name].get('class')
        if not cap_class:
            raise NotImplementedError(f"Capability {name} is defined in registry but not implemented yet")
        return cap_class()

registry = Registry()
# Assuming registry is loaded on app startup
""")

# --- 3. Runner ---
write_file('app/orchestration/runner.py', """
from app.capabilities._schemas.models import RunContext, CapabilityResult
from app.orchestration.registry import registry
from typing import Dict, Any

async def run_capability(capability_name: str, context: RunContext, input_data: Dict[str, Any]) -> CapabilityResult:
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
""")

# --- 4. Tracing ---
write_file('app/platform/tracing.py', """
import os

def set_langsmith_tags(mode: str, capability: str, origin: str):
    # Setup tags for LangSmith trace
    tags = [f"mode:{mode}", f"cap:{capability}"]
    if origin:
        tags.append(f"origin:{origin}")
    os.environ["LANGCHAIN_TAGS"] = ",".join(tags)

def get_trace_url(run_id: str) -> str:
    # Helper to build a LangSmith trace URL
    return f"https://smith.langchain.com/o/default/projects/p/creatoros-demo?run_id={run_id}"
""")

print("Phase 2 scaffolding generated.")
