from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import (
    assets,
    auth,
    campaigns,
    health,
    intents,
    library,
    runs,
    voice,
)

app = FastAPI(title="CreatorOS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router)
app.include_router(campaigns.router)
app.include_router(assets.router)
app.include_router(runs.router)
app.include_router(intents.router)
app.include_router(voice.router)
app.include_router(library.router)
