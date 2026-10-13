from pathlib import Path
from pypdf import PdfReader


def load_pdf_pages(pdf_path: Path) -> list[dict]:
    """Extrai texto página a página e mantém a origem para citações."""
    documents = []
    reader = PdfReader(str(pdf_path))
    for page_number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            documents.append({
                "text": text,
                "metadata": {
                    "source": pdf_path.name,
                    "page": page_number,
                },
            })
    return documents
