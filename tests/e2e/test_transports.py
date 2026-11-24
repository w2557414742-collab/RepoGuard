from pathlib import Path
from sys import executable

import anyio
from fastapi.testclient import TestClient
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from repoguard.api import create_app
from repoguard.sdk import RepoGuard


def test_api_paths_and_read_only_index_policy(history, tmp_path):
    repo, base, target = history
    database = tmp_path / "db"
    sdk = RepoGuard(repo.root, database)
    sdk.index(base)
    sdk.index(target, base=base)
    with TestClient(create_app(repo.root, database)) as client:
        assert client.post("/v1/index", json={"target": target}).status_code == 403
        definitions = client.get("/v1/definition", params={"q": "app.core.verify"})
        assert definitions.status_code == 200
        sid = definitions.json()[0]["id"]
        result = client.get(f"/v1/graph/{sid}", params={"limit": 1}).json()
        assert result["truncated"] and len(result["nodes"]) == 1
        file = client.get("/v1/file", params={"path": "src/app/core.py"})
        assert file.status_code == 200 and "audience" in file.json()["source"]
        assert client.get("/v1/file", params={"path": "../private.py"}).status_code == 400
        assert client.get("/v1/impact", params={"base": base, "target": target}).status_code == 200
        diff = client.get(
            "/v1/diff", params={"base": base, "target": target, "path": "src/app/core.py"}
        )
        assert diff.status_code == 200 and "+def verify(token, audience" in diff.json()["diff"]
    with TestClient(create_app(repo.root, database, write_token="local-test")) as client:
        assert (
            client.post(
                "/v1/index", json={"target": target}, headers={"X-RepoGuard-Token": "local-test"}
            ).status_code
            == 200
        )


def test_mcp_stdio_protocol(history, tmp_path):
    repo, base, _ = history
    database = tmp_path / "db"
    RepoGuard(repo.root, database).index(base)

    async def exchange():
        command = StdioServerParameters(
            command=str(Path(executable)),
            args=[
                "-m",
                "repoguard.mcp_server",
                "--repo",
                str(repo.root),
                "--db",
                str(database),
                "--revision",
                base,
            ],
        )
        async with stdio_client(command) as (read, write), ClientSession(read, write) as session:
            initialized = await session.initialize()
            assert initialized.serverInfo.name == "RepoGuard"
            names = {tool.name for tool in (await session.list_tools()).tools}
            assert "find_definition" in names and "run_tests" not in names
            response = await session.call_tool("find_definition", {"query": "app.core.verify"})
            assert not response.isError
            assert response.structuredContent["symbols"][0]["module"] == "app.core"

    anyio.run(exchange)
