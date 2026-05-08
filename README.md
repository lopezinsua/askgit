# askgit

A command-line agent that accepts a public GitHub repository URL and answers natural language questions about the code using function calling. The agent reads real files from the repo — it never hallucinates file content.

## How it works

```
user question
      |
      v
  Groq LLM   ──── decides to call tool ────>  GitHub API
      |                                              |
      |  <─────────── tool result ──────────────────┘
      |
      v
  final answer
      |
      v
   terminal
```

The agent loop runs until the model produces a text response with no pending tool calls. Conversation history is kept in memory for the duration of the session.

## Quickstart

```bash
git clone https://github.com/lopezinsua/askgit
cd askgit
pip install -r requirements.txt
cp .env.example .env          # add your GROQ_API_KEY (free at console.groq.com)
python agent.py https://github.com/lopezinsua/rag-cli
```

## Example session

```
Conectado a lopezinsua/rag-cli. Escribe tus preguntas (exit para salir).

> ¿Qué hace el archivo indexer.py?
[Leyendo src/indexer.py...]
indexer.py carga un PDF con pypdf, lo divide en chunks de 500 tokens con
solapamiento de 50, genera embeddings con sentence-transformers (local, sin API) y los almacena en un índice FAISS.

> ¿Qué dependencias tiene el proyecto?
[Leyendo requirements.txt...]
Las dependencias principales son: langchain-community, faiss-cpu, pypdf,
sentence-transformers.

> ¿Hay alguna función que maneje errores de red?
[Buscando 'error de red'...]
No encuentro manejo explícito de errores de red en los archivos leídos.

> exit
Hasta luego.
```

## Tools available

| Tool | Description |
|------|-------------|
| `list_files(path)` | List files and folders at a path |
| `read_file(path)` | Read and decode a file's content |
| `search_code(query)` | Grep over files already read in-session |
| `get_repo_info()` | Repo description, languages, stars, latest commit |
