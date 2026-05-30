import logging
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import settings
from app.stream_b.exceptions import EmbeddingError

logger = logging.getLogger(__name__)

COLLECTION_NAME = "news_chunks"

TEXT_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
    separators=["\n\n", "\n", ". ", " "],
)

OPENAI_MODEL = "text-embedding-3-small"
LOCAL_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

EMBEDDING_DIM_LOCAL = 384
EMBEDDING_DIM_OPENAI = 1536


class Embedder:
    def __init__(self, qdrant_client: QdrantClient | None = None):
        self._qdrant = qdrant_client or QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
        )
        self._openai_client: OpenAI | None = None
        self._sentence_model = None
        self._embedding_dim: int = 0

    def _init_openai(self) -> None:
        if self._openai_client is None:
            self._openai_client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
            )

    def _init_sentence_transformers(self) -> None:
        if self._sentence_model is None:
            from sentence_transformers import SentenceTransformer
            self._sentence_model = SentenceTransformer(LOCAL_MODEL)

    @property
    def embedding_dim(self) -> int:
        if self._embedding_dim == 0:
            self._embedding_dim = self._resolve_dim()
        return self._embedding_dim

    def _resolve_dim(self) -> int:
        if settings.EMBEDDING_MODEL == "openai" and settings.OPENAI_API_KEY:
            return EMBEDDING_DIM_OPENAI
        return EMBEDDING_DIM_LOCAL

    def ensure_collection(self) -> None:
        try:
            self._qdrant.get_collection(COLLECTION_NAME)
            logger.info("[Embedder] Collection '%s' already exists", COLLECTION_NAME)
        except Exception:
            logger.info("[Embedder] Creating collection '%s' with dim=%d", COLLECTION_NAME, self.embedding_dim)
            self._qdrant.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE,
                ),
            )

    def embed_and_upsert(
        self,
        articles: list[dict[str, Any]],
    ) -> int:
        self.ensure_collection()

        points: list[PointStruct] = []
        for article in articles:
            url = article.get("url", "")
            title = article.get("title", "")
            symbols = article.get("symbols", [])
            source_id = article.get("source_id")
            content = article.get("content", "")
            raw_chunks = TEXT_SPLITTER.split_text(content or title)

            if not raw_chunks:
                raw_chunks = [title or "No content"]

            vectors = self._embed_batch(raw_chunks)

            for idx, (chunk, vector) in enumerate(zip(raw_chunks, vectors)):
                point_id = self._make_point_id(url, idx)
                points.append(
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={
                            "title": title,
                            "content": chunk,
                            "url": url,
                            "symbols": symbols,
                            "source_id": str(source_id) if source_id else None,
                            "chunk_index": idx,
                        },
                    )
                )

        if not points:
            return 0

        try:
            self._qdrant.upsert(
                collection_name=COLLECTION_NAME,
                points=points,
            )
            logger.info(
                "[Embedder] Upserted %d chunks (%d articles)",
                len(points), len(articles),
            )
        except Exception as exc:
            raise EmbeddingError(f"Qdrant upsert failed: {exc}") from exc

        return len(points)

    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        if settings.EMBEDDING_MODEL == "openai" and settings.OPENAI_API_KEY:
            return self._embed_openai(texts)
        return self._embed_local(texts)

    def _embed_openai(self, texts: list[str]) -> list[list[float]]:
        self._init_openai()
        try:
            response = self._openai_client.embeddings.create(
                model=OPENAI_MODEL,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except Exception as exc:
            raise EmbeddingError(f"OpenAI embedding failed: {exc}") from exc

    def _embed_local(self, texts: list[str]) -> list[list[float]]:
        self._init_sentence_transformers()
        try:
            return self._sentence_model.encode(texts, convert_to_numpy=True).tolist()
        except Exception as exc:
            raise EmbeddingError(f"sentence-transformers embedding failed: {exc}") from exc

    @staticmethod
    def _make_point_id(url: str, chunk_index: int) -> str:
        import hashlib
        suffix = f"{url}:{chunk_index}"
        return hashlib.sha256(suffix.encode()).hexdigest()[:32]
