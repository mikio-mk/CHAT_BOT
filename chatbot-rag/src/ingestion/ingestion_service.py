import hashlib
import os
from pathlib import Path

from src.ingestion.pdf_loader import load_pdf_pages
from src.ingestion.chunker import chunk_text
from src.embeddings.embedding_service import EmbeddingService
from src.vectorstore.vector_repository import VectorRepository


def ingest_pdfs(pdf_dir: str = "data/pdfs", rebuild: bool = False) -> int:
    directory = Path(pdf_dir)
    directory.mkdir(parents=True, exist_ok=True)
    pdf_files = sorted(directory.glob("*.pdf"))
    if not pdf_files:
        print(f"Nenhum PDF encontrado em: {directory.resolve()}")
        print("Adicione arquivos PDF à pasta data/pdfs e execute novamente.")
        return 0

    chunk_size = int(os.getenv("CHUNK_SIZE", "900"))
    overlap = int(os.getenv("CHUNK_OVERLAP", "150"))
    repository = VectorRepository()
    if rebuild:
        repository.reset()

    all_chunks = []
    for pdf_path in pdf_files:
        pages = load_pdf_pages(pdf_path)
        if not pages:
            print(f"Aviso: não foi possível extrair texto de {pdf_path.name}.")
            continue
        for page_doc in pages:
            page_chunks = chunk_text(page_doc["text"], chunk_size, overlap)
            for index, chunk in enumerate(page_chunks):
                identity = f"{pdf_path.name}|{page_doc['metadata']['page']}|{index}"
                chunk_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()
                all_chunks.append({
                    "id": chunk_id,
                    "text": chunk,
                    "metadata": {
                        **page_doc["metadata"],
                        "chunk": index + 1,
                    },
                })

    if not all_chunks:
        print("Nenhum texto extraível foi encontrado nos PDFs.")
        return 0

    embedding_service = EmbeddingService()
    batch_size = 64
    total = 0
    for start in range(0, len(all_chunks), batch_size):
        batch = all_chunks[start:start + batch_size]
        vectors = embedding_service.encode_documents([item["text"] for item in batch])
        total += repository.add_chunks(batch, vectors)

    print(f"Ingestão concluída: {total} chunks indexados de {len(pdf_files)} PDF(s).")
    print(f"Total de chunks no banco vetorial: {repository.count()}")
    return total
