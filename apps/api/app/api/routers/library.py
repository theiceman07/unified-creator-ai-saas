from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.auth import current_creator

router = APIRouter(prefix="/v1/library", tags=["library"])

class SourceRequest(BaseModel):
    url: str

@router.post("/ingest")
async def ingest_source(req: SourceRequest, creator_id: str = Depends(current_creator)):
    # Stub: Queues an ingestion job
    return {"status": "queued", "source_id": "abc-123"}
