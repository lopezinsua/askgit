import json
from .github import GitHubClient

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and folders at a given path in the repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path relative to repo root. Use '' for root.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the full content of a file from the repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to repo root.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_code",
            "description": "Search for text across files already read in this session.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text string to search for in source files.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_repo_info",
            "description": "Get repository metadata: description, languages, stars, and latest commit.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def dispatch(name: str, args: dict, client: GitHubClient, cache: dict) -> str:
    if name == "list_files":
        return _list_files(args.get("path", ""), client)
    if name == "read_file":
        return _read_file(args["path"], client, cache)
    if name == "search_code":
        return _search_code(args["query"], cache)
    if name == "get_repo_info":
        return _get_repo_info(client)
    return f"Unknown tool: {name}"


def _list_files(path: str, client: GitHubClient) -> str:
    try:
        items = client.get_contents(path)
        if isinstance(items, list):
            return "\n".join(f"[{i['type']}] {i['name']}" for i in items)
        return f"[{items['type']}] {items['name']}"
    except Exception as e:
        return f"Error listing files: {e}"


def _read_file(path: str, client: GitHubClient, cache: dict) -> str:
    try:
        data = client.get_contents(path)
        if isinstance(data, list):
            return "Path is a directory. Use list_files to explore it."
        content = client.decode_file(data)
        cache[path] = content
        return content
    except Exception as e:
        return f"Error reading file: {e}"


def _search_code(query: str, cache: dict) -> str:
    if not cache:
        return "No files have been read yet. Use read_file first."
    results = []
    q = query.lower()
    for path, content in cache.items():
        for i, line in enumerate(content.splitlines(), 1):
            if q in line.lower():
                results.append(f"{path}:{i}: {line.strip()}")
    return "\n".join(results[:30]) if results else f"No matches for '{query}' in read files."


def _get_repo_info(client: GitHubClient) -> str:
    try:
        repo = client.get_repo()
        langs = client.get_languages()
        commit = client.get_latest_commit()
        return json.dumps(
            {
                "name": repo.get("full_name"),
                "description": repo.get("description"),
                "stars": repo.get("stargazers_count"),
                "forks": repo.get("forks_count"),
                "languages": list(langs.keys()),
                "latest_commit": {
                    "sha": commit["sha"][:7],
                    "message": commit["commit"]["message"].splitlines()[0],
                    "author": commit["commit"]["author"]["name"],
                    "date": commit["commit"]["author"]["date"],
                },
            },
            indent=2,
        )
    except Exception as e:
        return f"Error fetching repo info: {e}"
