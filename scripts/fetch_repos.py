#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, parse, request


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_data" / "repos_live.json"


def github_get(url: str, token: str | None):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "go-eureka-site-repo-sync"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = request.Request(url, headers=headers, method="GET")
    with request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def normalize(items):
    normalized = []
    for item in items:
      normalized.append(
          {
              "name": item.get("full_name") or item.get("name"),
              "html_url": item.get("html_url"),
              "description": item.get("description"),
              "language": item.get("language"),
              "topics": item.get("topics") or [],
              "stargazers_count": item.get("stargazers_count", 0),
              "updated_at": item.get("updated_at"),
              "archived": bool(item.get("archived", False))
          }
      )
    return normalized


def fetch_all_repos(org: str, token: str | None):
    page = 1
    all_items = []
    while True:
        query = parse.urlencode(
            {"per_page": 100, "type": "public", "sort": "updated", "page": page}
        )
        url = f"https://api.github.com/orgs/{org}/repos?{query}"
        data = github_get(url, token)
        if not data:
            break
        if not isinstance(data, list):
            raise RuntimeError("Unexpected API response shape.")
        all_items.extend(data)
        if len(data) < 100:
            break
        page += 1
    return all_items


def main():
    org = os.getenv("ORG_LOGIN")
    token = os.getenv("GITHUB_TOKEN")
    if not org:
        print("ORG_LOGIN is required.", file=sys.stderr)
        return 1

    try:
        repos = fetch_all_repos(org, token)
    except (error.URLError, error.HTTPError, TimeoutError, RuntimeError) as exc:
        print(f"Repository sync skipped due to API error: {exc}", file=sys.stderr)
        print("Keeping existing _data/repos_live.json unchanged.")
        return 0

    payload = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source": "github-api",
        "repos": normalize(repos)
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(payload['repos'])} repositories to {OUTPUT}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
