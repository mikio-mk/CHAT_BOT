import os
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or os.getenv(
            "EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.model = SentenceTransformer(self.model_name)

    def encode_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(
            texts, normalize_embeddings=True, show_progress_bar=len(texts) > 16
        )
        return vectors.tolist()

    def encode_query(self, text: str) -> list[float]:
        vector = self.model.encode([text], normalize_embeddings=True)
        return vector[0].tolist()
