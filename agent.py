import argparse
import json
import os
import sys
from urllib.parse import urlparse

from dotenv import load_dotenv
from groq import Groq

from src.github import GitHubClient
from src.tools import TOOLS_SCHEMA, dispatch

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    print("Error: GROQ_API_KEY no está definida. Crea un archivo .env con tu clave.")
    sys.exit(1)

SYSTEM_PROMPT = (
    "Eres un asistente experto en análisis de código.\n"
    "Tienes acceso a las tools para leer el repositorio.\n"
    "SIEMPRE usa las tools para responder — nunca inventes contenido de archivos.\n"
    "Responde de forma concisa y técnica.\n"
    "Si algo no está en el repositorio, dilo claramente."
)


def parse_repo_url(url: str) -> tuple[str, str]:
    parts = urlparse(url).path.strip("/").split("/")
    if len(parts) < 2:
        print("URL inválida. Usa: https://github.com/owner/repo")
        sys.exit(1)
    return parts[0], parts[1].removesuffix(".git")


def tool_label(name: str, args: dict) -> str:
    if name == "read_file":
        return f"[Leyendo {args.get('path', '')}...]"
    if name == "list_files":
        path = args.get("path") or "/"
        return f"[Listando {path}...]"
    if name == "search_code":
        return f"[Buscando '{args.get('query', '')}'...]"
    return "[Obteniendo info del repo...]"


MAX_TOOL_ROUNDS = 10


def run_agent(
    question: str,
    messages: list,
    client: Groq,
    github: GitHubClient,
    cache: dict,
) -> str:
    messages.append({"role": "user", "content": question})

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            answer = msg.content or ""
            messages.append({"role": "assistant", "content": answer})
            return answer

        messages.append(msg)
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments)
            print(tool_label(name, args))
            result = dispatch(name, args, github, cache)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    return "Error: se alcanzó el límite de llamadas a tools sin obtener respuesta."


def main():
    parser = argparse.ArgumentParser(
        description="askgit — pregunta sobre cualquier repo público de GitHub"
    )
    parser.add_argument(
        "repo_url", help="URL del repositorio (ej: https://github.com/owner/repo)"
    )
    args = parser.parse_args()

    owner, repo = parse_repo_url(args.repo_url)
    github = GitHubClient(owner, repo)
    groq_client = Groq()
    file_cache: dict[str, str] = {}
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    print(f"Conectado a {owner}/{repo}. Escribe tus preguntas (exit para salir).\n")

    try:
        while True:
            try:
                question = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nHasta luego.")
                break

            if not question:
                continue
            if question.lower() in ("exit", "quit", "salir"):
                print("Hasta luego.")
                break

            try:
                answer = run_agent(question, messages, groq_client, github, file_cache)
                print(answer)
            except Exception as e:
                print(f"Error: {e}")
    finally:
        github.close()


if __name__ == "__main__":
    main()
