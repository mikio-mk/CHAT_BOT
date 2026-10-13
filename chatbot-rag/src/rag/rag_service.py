import os
from src.retrieval.retriever import Retriever
from src.llm.llama_service import LlamaService
from src.rag.prompt import build_prompt


class RagService:
    def __init__(self):
        self.top_k = int(os.getenv("TOP_K", "4"))
        self.retriever = Retriever(top_k=self.top_k)
        self.llm = LlamaService()

    def answer(self, question: str) -> dict:
        question = question.strip()
        if not question:
            raise ValueError("A pergunta não pode estar vazia.")

        chunks = self.retriever.retrieve(question)
        if not chunks:
            return {
                "answer": "Não encontrei informações suficientes na base de conhecimento. Verifique se os PDFs foram indexados.",
                "sources": [],
            }

        # Distância cosseno: valores menores indicam maior proximidade.
        # Este limite é uma proteção simples, não uma garantia universal de relevância.
        best_distance = chunks[0]["distance"]
        if best_distance > 0.65:
            return {
                "answer": "Não encontrei informações suficientes sobre esse assunto na base de conhecimento.",
                "sources": self._sources(chunks),
            }

        prompt = build_prompt(question, chunks)
        answer = self.llm.generate(prompt)
        return {"answer": answer, "sources": self._sources(chunks)}

    @staticmethod
    def _sources(chunks: list[dict]) -> list[dict]:
        seen = set()
        sources = []
        for item in chunks:
            metadata = item["metadata"]
            key = (metadata.get("source"), metadata.get("page"))
            if key not in seen:
                seen.add(key)
                sources.append({
                    "file": metadata.get("source", "desconhecido"),
                    "page": metadata.get("page", "?"),
                })
        return sources
