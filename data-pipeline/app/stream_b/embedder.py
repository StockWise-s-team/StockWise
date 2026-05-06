from typing import List, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config import settings

class Embedder:
    def __init__(self):
        self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)

    def ensure_collection(self):
        try:
            self.client.get_collection("news_chunks")
        except Exception:
            self.client.create_collection(
                collection_name="news_chunks",
                vectors_config=VectorParams(size=768, distance=Distance.COSINE)
            )

    def embed_and_upsert(self, chunks: List[Any]):
        self.ensure_collection()
        pass
