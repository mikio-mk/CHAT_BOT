from src.embeddings.embedding_service import EmbeddingService
from src.vectorstore.vector_repository import VectorRepository


class Retriever:
    def __init__(self, top_k: int = 4):
        self.embeddings = EmbeddingService()
        self.repository = VectorRepository()
        self.top_k = top_k

    def retrieve(self, question: str) -> list[dict]:
        query_vector = self.embeddings.encode_query(question)
        return self.repository.query(query_vector, top_k=self.top_k)
