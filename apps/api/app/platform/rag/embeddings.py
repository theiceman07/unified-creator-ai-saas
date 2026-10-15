
class EmbeddingService:
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        # Stub: return zero vectors
        dim = 768
        return [[0.0] * dim for _ in texts]
        
    async def chunk_document(self, text: str) -> list[str]:
        # Very basic stub chunker
        return text.split("\n\n")

embedding_service = EmbeddingService()
