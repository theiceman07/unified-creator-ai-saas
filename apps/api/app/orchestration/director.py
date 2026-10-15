import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, StateGraph

from app.capabilities._schemas import CreatorContext


def merge_dicts(a: dict, b: dict) -> dict:
    c = a.copy()
    c.update(b)
    return c

class CampaignState(TypedDict, total=False):
    run_id: str
    campaign_id: str
    creator_id: str
    request: dict
    context: CreatorContext
    research: dict
    library_hits: list
    audience_signals: dict
    angles: list
    chosen_angle: dict
    brief: dict
    hooks: list
    top_hooks: list
    script: dict
    script_attempts: int
    production: dict
    thumbnails: list
    copy: dict
    platform_posts: list
    schedule: list
    scores: Annotated[dict, merge_dicts]
    errors: Annotated[list, operator.add]

def build_director_graph():
    workflow = StateGraph(CampaignState)
    
    # 1. load_context
    def load_context(state: CampaignState):
        print("Loading context...")
        return {"context": CreatorContext(creator_id=state.get("creator_id", "demo"), display_name="Demo", recent_ctas=[])}
        
    workflow.add_node("load_context", load_context)
    workflow.set_entry_point("load_context")
    
    # In a full implementation, we'd add research, library, audience, ideation, etc.
    # For Phase 3 stub, we just go to END.
    workflow.add_edge("load_context", END)
    
    return workflow.compile()
