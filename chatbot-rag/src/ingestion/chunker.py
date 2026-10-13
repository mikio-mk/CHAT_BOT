import re


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    """Divide texto em partes com sobreposição; parâmetros medidos em caracteres."""
    if chunk_size < 1:
        raise ValueError("chunk_size precisa ser maior que zero.")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap deve ser >= 0 e menor que chunk_size.")

    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []

    chunks = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        if end < len(normalized):
            # Tenta encerrar em um espaço para não cortar palavras no meio.
            boundary = normalized.rfind(" ", start, end)
            if boundary > start + int(chunk_size * 0.6):
                end = boundary
        piece = normalized[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(normalized):
            break
        start = max(end - overlap, start + 1)
    return chunks
