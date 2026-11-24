"""通过 MCP SDK 暴露固定版本的 RepoGuard 查询和补丁预检。"""

from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .cli import encode
from .sdk import RepoGuard


def create_server(engine: RepoGuard, revision: str) -> FastMCP:
    """创建 FastMCP 适配层并固定一个已发布的仓库版本，工具将 SDK 记录转为结构化响应。"""
    server = FastMCP("RepoGuard")
    view = engine.view(revision)
    commit = view.snapshot.commit

    @server.tool()
    def search_symbols(query: str, limit: int = 20) -> dict[str, object]:
        """Search a pinned commit using exact names, BM25 and dependency evidence."""
        return {
            "commit": commit,
            "hits": [asdict(hit) for hit in view.search_symbols(query, limit)],
        }

    @server.tool()
    def find_definition(query: str) -> dict[str, object]:
        """Return matching definitions at the pinned commit with path and line range."""
        return {
            "commit": commit,
            "symbols": [asdict(symbol) for symbol in view.find_definition(query)],
        }

    @server.tool()
    def find_references(symbol_id: str) -> dict[str, object]:
        """Return import and lexical references to a known symbol."""
        return {
            "commit": commit,
            "edges": [asdict(edge) for edge in view.find_references(symbol_id)],
        }

    @server.tool()
    def get_callers(symbol_id: str) -> dict[str, object]:
        """Return statically known and possible incoming calls."""
        return {"commit": commit, "edges": [asdict(edge) for edge in view.get_callers(symbol_id)]}

    @server.tool()
    def get_callees(symbol_id: str) -> dict[str, object]:
        """Return statically known and possible outgoing calls."""
        return {"commit": commit, "edges": [asdict(edge) for edge in view.get_callees(symbol_id)]}

    @server.tool()
    def get_dependency_graph(symbol_id: str, depth: int = 2, limit: int = 100) -> dict[str, object]:
        """Return a bounded subgraph with confidence and source evidence."""
        result = view.get_dependency_graph(symbol_id, depth=depth, limit=limit)
        for node in result["nodes"]:
            node["symbol"] = encode(node["symbol"]) if node["symbol"] else None
            node["evidence"] = [asdict(edge) for edge in node["evidence"]]
        return result

    @server.tool()
    def analyze_change_impact(base_commit: str, depth: int = 5) -> dict[str, object]:
        """Compare a published base snapshot with this server's pinned commit."""
        return asdict(engine.analyze_change_impact(base_commit, commit, depth=depth))

    @server.tool()
    def select_related_tests(base_commit: str) -> dict[str, object]:
        """Return static test evidence and conservative fallback information."""
        return asdict(engine.select_related_tests(base_commit, commit))

    @server.tool()
    def plan_refactoring(symbol_id: str, new_name: str) -> dict[str, object]:
        """Preview a symbol rename and report validation without writing repository files."""
        return asdict(engine.plan_refactoring(commit, symbol_id, new_name))

    @server.tool()
    def validate_patch(patch: str) -> dict[str, object]:
        """Check a unified Python diff against the pinned commit in memory."""
        return asdict(engine.validate_patch(commit, patch))

    return server


def main() -> None:
    parser = argparse.ArgumentParser(prog="repoguard-mcp")
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--revision", default="HEAD")
    args = parser.parse_args()
    create_server(RepoGuard(args.repo, args.db), args.revision).run(transport="stdio")


if __name__ == "__main__":
    main()
