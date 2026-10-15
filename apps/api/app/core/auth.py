from typing import Annotated

import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.core.config import settings
from app.core.errors import UnauthorizedError

security = HTTPBearer(auto_error=False)

class CreatorContext(BaseModel):
    creator_id: str
    is_demo: bool = False

async def current_creator(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]
) -> CreatorContext:
    if settings.DEMO_MODE and credentials and credentials.credentials.startswith("demo-"):
        # Simulated demo token
        return CreatorContext(creator_id="00000000-0000-0000-0000-000000000000", is_demo=True)
        
    if not credentials:
        if settings.DEMO_MODE:
             return CreatorContext(creator_id="00000000-0000-0000-0000-000000000000", is_demo=True)
        raise UnauthorizedError("Missing authentication token")
        
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, 
            settings.SUPABASE_JWT_SECRET, 
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        creator_id = payload.get("sub")
        if not creator_id:
            raise UnauthorizedError("Invalid token payload")
        return CreatorContext(creator_id=creator_id)
    except jwt.PyJWTError:
        raise UnauthorizedError("Invalid authentication token")
