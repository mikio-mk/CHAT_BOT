from pathlib import Path
import chromadb


class VectorRepository:
    def __init__(self, persist_dir: str = "vectorstore", collection_name: str = "pdfs"):
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def reset(self) -> None:
        name = self.collection.name
        self.client.delete_collection(name)
        self.collection = self.client.get_or_create_collection(
            name=name, metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: list[dict], embeddings: list[list[float]]) -> int:
        if not chunks:
            return 0
        # IDs determinísticos por arquivo/página/posição ajudam a evitar duplicatas.
        ids = [item["id"] for item in chunks]
        self.collection.upsert(
            ids=ids,
            documents=[item["text"] for item in chunks],
            embeddings=embeddings,
            metadatas=[item["metadata"] for item in chunks],
        )
        return len(chunks)

    def query(self, embedding: list[float], top_k: int = 4) -> list[dict]:
        if self.collection.count() == 0:
            return []
        result = self.collection.query(
            query_embeddings=[embedding],
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )
        found = []
        for i, document in enumerate(result["documents"][0]):
            found.append({
                "text": document,
                "metadata": result["metadatas"][0][i],
                "distance": result["distances"][0][i],
            })
        return found

    def count(self) -> int:
        return self.collection.count()
