from uuid import UUID
from typing import Any, TypedDict
from langgraph.graph import END, StateGraph

from app.capabilities._schemas.models import RunContext
from app.orchestration.runner import run_capability


class CampaignState(TypedDict):
    run_id: UUID
    creator_id: UUID
    topic: str
    context: dict[str, Any]
    research: dict[str, Any]
    hook: dict[str, Any]
    script: dict[str, Any]

async def node_research(state: CampaignState):
    ctx = RunContext(run_id=UUID(str(state['run_id'])), creator_id=UUID(str(state['creator_id'])), mode="campaign")
    res = await run_capability("research", ctx, {"topic": state['topic']})
    return {"research": res.assets[0] if res.assets else {}}

async def node_hook(state: CampaignState):
    ctx = RunContext(run_id=UUID(str(state['run_id'])), creator_id=UUID(str(state['creator_id'])), mode="campaign")
    res = await run_capability("hook", ctx, {"research": state.get('research')})
    return {"hook": res.assets[0] if res.assets else {}}

async def node_script(state: CampaignState):
    ctx = RunContext(run_id=UUID(str(state['run_id'])), creator_id=UUID(str(state['creator_id'])), mode="campaign")
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
