import os


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")

# --- 1. Validators ---
write_file('app/platform/validators/basic.py', r"""
import re
from typing import List, Dict, Any, Optional

class Validator:
    def validate_word_budget(self, text: str, max_words: int) -> bool:
        words = len(re.findall(r'\w+', text))
        return words <= max_words

    def validate_banned_words(self, text: str, banned_words: List[str]) -> List[str]:
        found = [word for word in banned_words if word.lower() in text.lower()]
        return found

    def check_platform_limits(self, platform: str, text: str) -> bool:
        limits = {
            'x': 280,
            'linkedin': 3000,
            'youtube_shorts': 100
        }
        if platform in limits:
            return len(text) <= limits[platform]
        return True

validator = Validator()
""")

# --- 2. Judge ---
write_file('app/platform/judge.py', """
import yaml
import os
import uuid
from typing import Dict, Any

class Judge:
    def __init__(self):
        self.rubrics = {}
    
    def load_rubrics(self, directory: str):
        if not os.path.exists(directory):
            return
        for filename in os.listdir(directory):
            if filename.endswith(".yaml"):
                path = os.path.join(directory, filename)
                with open(path, 'r') as f:
                    data = yaml.safe_load(f)
                    self.rubrics[data.get('id', filename)] = data

    async def judge_asset(self, asset_id: str, capability: str, content: str) -> Dict[str, Any]:
        # Dummy implementation of the judge
        # In a real scenario, this would use a fast LLM to grade the output against a rubric
        return {
            "overall": 4.5,
            "passed": True,
            "critique": "Good hook, clear value proposition.",
            "scores": {"clarity": 5, "engagement": 4}
        }

    async def pairwise_tournament(self, candidates: List[str]) -> str:
        # Dummy implementation: just pick the first one
        if not candidates:
            return None
        return candidates[0]

judge = Judge()
""")

# --- 3. Events & SSE ---
write_file('app/orchestration/events.py', """
import json
import asyncio
from typing import AsyncGenerator, Any

class EventManager:
    def __init__(self):
        self.listeners = {}
    
    def subscribe(self, run_id: str):
        queue = asyncio.Queue()
        if run_id not in self.listeners:
            self.listeners[run_id] = []
        self.listeners[run_id].append(queue)
        return queue

    def unsubscribe(self, run_id: str, queue: asyncio.Queue):
        if run_id in self.listeners:
            self.listeners[run_id].remove(queue)
            if not self.listeners[run_id]:
                del self.listeners[run_id]

    async def publish(self, run_id: str, event_type: str, payload: dict):
        event = {"type": event_type, "payload": payload}
        if run_id in self.listeners:
            for queue in self.listeners[run_id]:
                await queue.put(event)

    async def stream_events(self, run_id: str, last_event_id: str = None) -> AsyncGenerator[str, None]:
        queue = self.subscribe(run_id)
        try:
            # Yield a heartbeat every 15s to keep connection alive
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"event: {event['type']}\\ndata: {json.dumps(event['payload'])}\\n\\n"
                except asyncio.TimeoutError:
                    yield f": heartbeat\\n\\n"
        finally:
            self.unsubscribe(run_id, queue)

event_manager = EventManager()
""")

write_file('app/api/routers/runs.py', """
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from app.core.auth import current_creator
from app.orchestration.events import event_manager

router = APIRouter(prefix="/v1/runs", tags=["runs"])

@router.get("/{run_id}/events")
async def get_run_events(run_id: str, request: Request, creator_id: str = Depends(current_creator)):
    last_event_id = request.headers.get('Last-Event-ID')
    
    return StreamingResponse(
        event_manager.stream_events(run_id, last_event_id),
        media_type="text/event-stream"
    )
""")

print("Phase 2 part 2 scaffolding generated.")
