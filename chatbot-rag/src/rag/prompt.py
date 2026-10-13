def build_prompt(question: str, retrieved_chunks: list[dict]) -> str:
    context_parts = []
    for index, item in enumerate(retrieved_chunks, start=1):
        metadata = item["metadata"]
        source = metadata.get("source", "arquivo desconhecido")
        page = metadata.get("page", "?")
        context_parts.append(
            f"[Trecho {index} | Fonte: {source} | Página: {page}]\\n{item['text']}"
        )
    context = "\\n\\n".join(context_parts)

    return f"""Você é um assistente que responde perguntas com base em documentos PDF.
Use exclusivamente as informações do CONTEXTO para responder.
Não invente fatos nem complete lacunas com conhecimento externo.
Se o contexto não contiver evidências suficientes para responder, diga:
"Não encontrei informações suficientes sobre esse assunto na base de conhecimento."
Responda em português, de forma clara e objetiva.
Ao final, mencione os arquivos e páginas usados quando houver informação suficiente.

CONTEXTO:
{context}

PERGUNTA:
{question}

RESPOSTA:
"""
