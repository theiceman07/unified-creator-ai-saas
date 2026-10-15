from typing import Any


async def dummy_task(ctx: dict[str, Any]) -> None:
    pass

class WorkerSettings:
    redis_settings = None # Can be configured to connect to Redis
    functions = [dummy_task] # Add background task functions here
    
    @staticmethod
    async def on_startup(ctx: dict[str, Any]) -> None:
        print("Worker starting up...")
        
    @staticmethod
    async def on_shutdown(ctx: dict[str, Any]) -> None:
        print("Worker shutting down...")
