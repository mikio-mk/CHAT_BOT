import argparse
import sys

from src.ingestion.ingestion_service import ingest_pdfs
from src.rag.rag_service import RagService
from src.vectorstore.vector_repository import VectorRepository


def print_result(result: dict) -> None:
    print("\nResposta:")
    print(result["answer"])
    if result.get("sources"):
        print("\nFontes recuperadas:")
        for source in result["sources"]:
            print(f"- {source['file']} — página {source['page']}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Chatbot RAG com Llama 3, PDFs, embeddings e ChromaDB."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Indexa os PDFs da pasta data/pdfs.")
    ingest_parser.add_argument(
        "--rebuild", action="store_true",
        help="Apaga a coleção atual e recria o índice a partir dos PDFs encontrados."
    )

    subparsers.add_parser("chat", help="Inicia o chat interativo.")
    ask_parser = subparsers.add_parser("ask", help="Faz uma única pergunta.")
    ask_parser.add_argument("question", help="Pergunta a ser respondida com base nos PDFs.")

    args = parser.parse_args()

    if args.command == "ingest":
        try:
            ingest_pdfs(rebuild=args.rebuild)
            return 0
        except Exception as exc:
            print(f"Erro durante a ingestão: {exc}", file=sys.stderr)
            return 1

    repository = VectorRepository()
    if repository.count() == 0:
        print("A base vetorial está vazia. Execute primeiro: python main.py ingest")
        return 1

    service = RagService()
    if args.command == "ask":
        try:
            print_result(service.answer(args.question))
            return 0
        except Exception as exc:
            print(f"Erro ao responder: {exc}", file=sys.stderr)
            return 1

    print("Chatbot RAG iniciado. Digite 'sair' para encerrar.")
    while True:
        try:
            question = input("\nVocê: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando.")
            break
        if question.lower() in {"sair", "exit", "quit"}:
            print("Até logo!")
            break
        if not question:
            continue
        try:
            print_result(service.answer(question))
        except Exception as exc:
            print(f"Erro ao responder: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
