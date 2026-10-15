from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.core.auth import current_creator
from app.orchestration.events import event_manager

router = APIRouter(prefix="/v1/runs", tags=["runs"])

@router.get("/{run_id}/events")
async def get_run_events(run_id: str, request: Request, creator_id: str = Depends(current_creator)):
    last_event_id: str | None = request.headers.get('Last-Event-ID')
    
    return StreamingResponse(
        event_manager.stream_events(run_id, last_event_id),
        media_type="text/event-stream"
    )
