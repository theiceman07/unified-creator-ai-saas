import os


def write_file(path, content):
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")

# --- 1. Capability Implementations (Stubs) ---
write_file('app/capabilities/research.py', """
from app.capabilities._base import Capability
from app.capabilities._schemas.models import RunContext, CapabilityResult, Card
from typing import Dict, Any

class ResearchCapability(Capability):
    async def invoke(self, context: RunContext, input_data: Dict[str, Any]) -> CapabilityResult:
        # Stub implementation
        card = Card(kind="research_brief", data={"facts": ["AI agents are autonomous", "LangGraph simplifies orchestration"]})
        return CapabilityResult(cards=[card], assets=[{"kind": "research_brief", "content": card.data}])
""")

write_file('app/capabilities/hook.py', """
from app.capabilities._base import Capability
from app.capabilities._schemas.models import RunContext, CapabilityResult, Card
from typing import Dict, Any

class HookCapability(Capability):
    async def invoke(self, context: RunContext, input_data: Dict[str, Any]) -> CapabilityResult:
        # Stub implementation
        card = Card(kind="hook", data={"hooks": ["ChatGPT isn't an agent. Here's why."]})
        return CapabilityResult(cards=[card], assets=[{"kind": "hook", "content": card.data}])
""")

write_file('app/capabilities/script.py', """
from app.capabilities._base import Capability
from app.capabilities._schemas.models import RunContext, CapabilityResult, Card
from typing import Dict, Any

class ScriptCapability(Capability):
    async def invoke(self, context: RunContext, input_data: Dict[str, Any]) -> CapabilityResult:
        # Stub implementation
        script_text = "HOOK: ChatGPT isn't an agent.\\nBODY: Here is the difference..."
        card = Card(kind="script", data={"script": script_text})
        return CapabilityResult(cards=[card], assets=[{"kind": "script", "content": card.data}])
""")

# --- 2. Update Registry yaml (mocking it if it doesnt exist, or modifying it) ---
write_file('capability_registry.yaml', """
capabilities:
  - name: research
    class_path: app.capabilities.research.ResearchCapability
  - name: hook
    class_path: app.capabilities.hook.HookCapability
  - name: script
    class_path: app.capabilities.script.ScriptCapability
""")

# --- 3. Intent Router ---
write_file('app/orchestration/intent_router.py', """
from typing import Dict, Any
from pydantic import BaseModel

class IntentRoute(BaseModel):
    intent: str  # campaign | quick | brain | ingest
    confidence: float
    parameters: Dict[str, Any]

async def route_intent(text: str) -> IntentRoute:
    # Dummy router: just route to campaign
    return IntentRoute(
        intent="campaign",
        confidence=0.9,
        parameters={"topic": text}
    )
""")

write_file('app/api/routers/intents.py', """
from fastapi import APIRouter
from pydantic import BaseModel
from app.orchestration.intent_router import route_intent, IntentRoute

router = APIRouter(prefix="/v1/intents", tags=["intents"])

class IntentRequest(BaseModel):
    text: str

@router.post("", response_model=IntentRoute)
async def classify_intent(request: IntentRequest):
    return await route_intent(request.text)
""")

# --- 4. Director Graph (LangGraph Stub) ---
write_file('app/orchestration/director/graph.py', """
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from typing import TypedDict
from app.capabilities._schemas.models import RunContext
from app.orchestration.runner import run_capability

class CampaignState(TypedDict):
    run_id: str
    creator_id: str
    topic: str
    context: Dict[str, Any]
    research: Dict[str, Any]
    hook: Dict[str, Any]
    script: Dict[str, Any]

async def node_research(state: CampaignState):
    ctx = RunContext(run_id=state['run_id'], creator_id=state['creator_id'], mode="campaign")
    res = await run_capability("research", ctx, {"topic": state['topic']})
    return {"research": res.assets[0] if res.assets else {}}

async def node_hook(state: CampaignState):
    ctx = RunContext(run_id=state['run_id'], creator_id=state['creator_id'], mode="campaign")
    res = await run_capability("hook", ctx, {"research": state.get('research')})
    return {"hook": res.assets[0] if res.assets else {}}

async def node_script(state: CampaignState):
    ctx = RunContext(run_id=state['run_id'], creator_id=state['creator_id'], mode="campaign")
    res = await run_capability("script", ctx, {"hook": state.get('hook')})
    return {"script": res.assets[0] if res.assets else {}}

workflow = StateGraph(CampaignState)
workflow.add_node("research", node_research)
workflow.add_node("hook", node_hook)
workflow.add_node("script", node_script)

workflow.add_edge("research", "hook")
workflow.add_edge("hook", "script")
workflow.add_edge("script", END)

workflow.set_entry_point("research")
app = workflow.compile()
""")

print("Phase 3 scaffolding generated.")
