# Chatbot RAG com Llama 3 e PDFs

Projeto integrador baseado na orientação fornecida: lê PDFs, extrai texto por página, divide em chunks com sobreposição, gera embeddings, persiste os vetores no ChromaDB, recupera os trechos mais relevantes e envia o contexto ao Llama 3 via Ollama. As respostas apresentam as fontes e páginas utilizadas.

## Requisitos

- Python 3.10 a 3.12 recomendado.
- Ollama instalado e em execução: https://ollama.com/
- Modelo Llama 3 baixado no Ollama.

> O projeto não treina nem faz fine-tuning do Llama. Os PDFs são indexados separadamente e consultados por RAG.

## 1. Instalação

Abra o terminal na pasta do projeto e crie um ambiente virtual.

### Windows (PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Se você tiver apenas outra versão compatível do Python, substitua `py -3.12` por `python`.

## 2. Preparar o Llama 3

Com o Ollama instalado, execute:

```powershell
ollama pull llama3
ollama run llama3
```

Depois que o modelo responder, você pode sair do chat do Ollama. O serviço normalmente fica disponível em `http://localhost:11434`.

## 3. Adicionar PDFs

Coloque os documentos que deseja consultar em `data/pdfs/`. A pasta já contém um arquivo `.gitkeep` como marcador. PDFs digitalizados como imagens podem precisar de OCR; esta versão extrai texto selecionável.

## 4. Indexar a base de conhecimento

Execute a partir da pasta raiz:

```powershell
python main.py ingest
```

A primeira execução baixa o modelo de embeddings multilíngue `paraphrase-multilingual-MiniLM-L12-v2`; isso exige internet. O índice persistente será salvo em `vectorstore/`.

Para recriar o índice depois de alterar ou remover PDFs:

```powershell
python main.py ingest --rebuild
```

## 5. Conversar com os documentos

```powershell
python main.py chat
```

Digite suas perguntas. Para encerrar, digite `sair` ou `exit`.

Também é possível fazer uma pergunta única:

```powershell
python main.py ask "O que os documentos dizem sobre o assunto?"
```

## Configurações opcionais

As variáveis de ambiente abaixo alteram os padrões:

- `OLLAMA_URL` — padrão `http://localhost:11434`
- `OLLAMA_MODEL` — padrão `llama3`
- `EMBEDDING_MODEL` — padrão `paraphrase-multilingual-MiniLM-L12-v2`
- `CHUNK_SIZE` — padrão `900` caracteres
- `CHUNK_OVERLAP` — padrão `150` caracteres
- `TOP_K` — padrão `4`

No PowerShell, por exemplo:

```powershell
$env:OLLAMA_MODEL = "llama3"
$env:TOP_K = "5"
python main.py chat
```

## Estrutura

```text
chatbot-rag/
├── data/pdfs/                 # PDFs de entrada
├── vectorstore/                # Índice persistente (gerado)
├── src/
│   ├── ingestion/
│   │   ├── pdf_loader.py       # Extração com metadados de página
│   │   ├── chunker.py          # Chunking com overlap
│   │   └── ingestion_service.py
│   ├── embeddings/
│   │   └── embedding_service.py
│   ├── vectorstore/
│   │   └── vector_repository.py
│   ├── retrieval/
│   │   └── retriever.py
│   ├── llm/
│   │   └── llama_service.py
│   └── rag/
│       ├── prompt.py
│       └── rag_service.py
├── tests/
├── main.py
└── requirements.txt
```

## Como o RAG responde

1. O PDF é lido e o texto de cada página é extraído.
2. O texto é dividido em chunks com sobreposição.
3. Cada chunk é convertido em embedding.
4. Texto, vetor e metadados (arquivo, página e índice do chunk) são persistidos no ChromaDB.
5. A pergunta também é convertida em embedding e os chunks semanticamente próximos são recuperados (Top-K).
6. Os trechos recuperados são incluídos no prompt do Llama 3.
7. O modelo deve responder somente com base no contexto. Quando a recuperação não encontra evidência suficiente, o sistema informa que não encontrou a resposta na base.
8. A resposta lista os arquivos e as páginas dos trechos recuperados.

## Limitações conhecidas

- PDFs sem camada de texto (scans/fotos) não são lidos por OCR nesta versão.
- A qualidade depende da qualidade dos PDFs, dos chunks recuperados e do modelo.
- A resposta pode conter erros; avalie-a com perguntas dentro e fora da base, conforme a orientação do projeto.
- O Ollama precisa estar em execução e o modelo `llama3` disponível localmente.
