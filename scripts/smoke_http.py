from __future__ import annotations

import argparse
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8080")
    args = parser.parse_args()

    def fetch(route: str, body: dict | None = None, **params: str):
        url = args.url.rstrip("/") + route
        if params:
            url += "?" + urlencode(params)
        request = Request(
            url,
            data=json.dumps(body).encode() if body else None,
            headers={"Content-Type": "application/json"} if body else {},
        )
        with urlopen(request, timeout=15) as response:
            raw = response.read()
            return json.loads(raw) if route.startswith("/v1/") else raw.decode()

    assert "RepoGuard" in fetch("/")
    assert fetch("/v1/health") == {"status": "ok"}
    snap = fetch("/v1/snapshot")
    assert snap["metadata"]["file_status"]["indexed"] == 70
    matches = fetch("/v1/symbols", q="click.formatting.iter_rows")
    target = matches[0]["symbol"]
    assert target["qualified_name"] == "click.formatting.iter_rows"
    assert any(e["line"] == 231 for e in fetch(f"/v1/references/{target['id']}"))
    assert fetch(f"/v1/graph/{target['id']}", kinds="CALLS", reverse="true")["nodes"]
    assert "def iter_rows" in fetch("/v1/file", path=target["path"])["source"]
    revisions = {"base": "HEAD~1", "target": "HEAD"}
    assert fetch("/v1/impact", **revisions)["files"]
    assert "+__version__" in fetch("/v1/diff", path="src/click/__init__.py", **revisions)["diff"]
    assert fetch("/v1/tests", **revisions)["run_all"]
    assert "introduced" in fetch("/v1/architecture", **revisions)
    plan = fetch(
        "/v1/refactoring/plan",
        body={
            "symbol_id": target["id"],
            "name": "aligned_rows",
        },
    )
    assert not plan["blockers"] and "def aligned_rows" in plan["patch"]
    assert fetch("/v1/benchmark")["index"]["dependency"]["parsed_files"] == 1
    print(
        "Click snapshot, search, source, graph, diff, selection, architecture, patch and benchmark passed"
    )


if __name__ == "__main__":
    main()
