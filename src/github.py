import base64
import httpx

BASE_URL = "https://api.github.com"


class GitHubClient:
    def __init__(self, owner: str, repo: str):
        self.owner = owner
        self.repo = repo
        self._http = httpx.Client(
            base_url=BASE_URL,
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=15.0,
        )

    def get_contents(self, path: str = "") -> dict | list:
        r = self._http.get(f"/repos/{self.owner}/{self.repo}/contents/{path}")
        r.raise_for_status()
        return r.json()

    def get_repo(self) -> dict:
        r = self._http.get(f"/repos/{self.owner}/{self.repo}")
        r.raise_for_status()
        return r.json()

    def get_languages(self) -> dict:
        r = self._http.get(f"/repos/{self.owner}/{self.repo}/languages")
        r.raise_for_status()
        return r.json()

    def get_latest_commit(self) -> dict:
        r = self._http.get(
            f"/repos/{self.owner}/{self.repo}/commits", params={"per_page": 1}
        )
        r.raise_for_status()
        return r.json()[0]

    def decode_file(self, content_json: dict) -> str:
        return base64.b64decode(content_json["content"]).decode("utf-8", errors="replace")

    def close(self):
        self._http.close()
