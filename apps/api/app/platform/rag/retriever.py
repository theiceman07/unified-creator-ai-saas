from typing import Any


class Retriever:
    async def search(self, creator_id: str, query: str, limit: int = 5) -> list[dict[str, Any]]:
        # Stub: return dummy chunks
        return [
            {"text": "Relevant fact 1", "score": 0.89},
            {"text": "Relevant fact 2", "score": 0.75}
        ]

retriever = Retriever()
