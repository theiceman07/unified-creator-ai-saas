import asyncio
import json
from collections.abc import AsyncGenerator
from typing import Any, TypedDict

class Event(TypedDict):
    type: str
    payload: dict[str, Any]

Queue = asyncio.Queue[Event]


class EventManager:
    def __init__(self) -> None:
        self.listeners: dict[str, list[Queue]] = {}
    
    def subscribe(self, run_id: str) -> Queue:
        queue: Queue = asyncio.Queue()
        self.listeners.setdefault(run_id, []).append(queue)
        return queue

    def unsubscribe(self, run_id: str, queue: Queue) -> None:
        if run_id in self.listeners:
            self.listeners[run_id].remove(queue)
            if not self.listeners[run_id]:
                del self.listeners[run_id]

    async def publish(self, run_id: str, event_type: str, payload: dict[str, Any]) -> None:
        event: Event = {"type": event_type, "payload": payload}
        for queue in self.listeners.get(run_id, []):
            await queue.put(event)

    async def stream_events(self, run_id: str, last_event_id: str | None = None) -> AsyncGenerator[str, None]:
        queue = self.subscribe(run_id)
        try:
            # Yield a heartbeat every 15s to keep connection alive
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"event: {event['type']}\ndata: {json.dumps(event['payload'])}\n\n"
                except TimeoutError:
                    yield ": heartbeat\n\n"
        finally:
            self.unsubscribe(run_id, queue)

event_manager = EventManager()
