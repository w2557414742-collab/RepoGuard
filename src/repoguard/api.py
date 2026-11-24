"""FastAPI 路由和请求模型，分析使用共用 SDK。"""

from __future__ import annotations

import json
import os
import secrets
from dataclasses import asdict
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .architecture import compare, load_rules
from .model import EdgeType
from .parser import decode_python
from .repository import RepositoryError, safe_relative
from .sdk import RepoGuard


class IndexRequest(BaseModel):
    target: str = Field(default="HEAD", min_length=1, max_length=200)
    base: str | None = Field(default=None, min_length=1, max_length=200)


class RefactorRequest(BaseModel):
    revision: str = Field(default="HEAD", min_length=1, max_length=200)
    symbol_id: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=100)
    operation: str = Field(default="rename", pattern="^(rename|signature)$")
    value: str | None = Field(default=None, max_length=2000)


def create_app(
    repository: str | Path,
    database: str | Path,
    *,
    write_token: str = "",
    rules: Path | None = None,
    benchmark: Path | None = None,
) -> FastAPI:
    """为一个仓库和索引地址装配 HTTP 应用。对索引写入校验令牌，查询从已发布快照读取。"""
    engine = RepoGuard(repository, database)
    app = FastAPI(title="RepoGuard", version="0.1.0")

    @app.exception_handler(ValueError)
    @app.exception_handler(RepositoryError)
    async def invalid_input(_request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.get("/v1/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.post("/v1/index")
    def index(body: IndexRequest, x_repoguard_token: str = Header(default="")) -> dict:
        if not write_token:
            raise HTTPException(403, "index publication is disabled")
        if not secrets.compare_digest(write_token.encode(), x_repoguard_token.encode()):
            raise HTTPException(403, "invalid index publication token")
        return engine.index(body.target, base=body.base).snapshot.metadata

    @app.get("/v1/snapshot")
    def snapshot(revision: str = "HEAD") -> dict:
        current = engine.view(revision).snapshot
        return {
            "metadata": current.metadata,
            "files": [asdict(file) for file in current.files.values() if file.status == "indexed"],
        }

    @app.get("/v1/symbols")
    def symbols(q: str, revision: str = "HEAD", limit: int = Query(20, ge=1, le=100)):
        return [asdict(hit) for hit in engine.view(revision).search_symbols(q, limit)]

    @app.get("/v1/definition")
    def definitions(q: str, revision: str = "HEAD"):
        return [asdict(symbol) for symbol in engine.view(revision).find_definition(q)]

    @app.get("/v1/references/{symbol_id}")
    def references(symbol_id: str, revision: str = "HEAD"):
        return [asdict(edge) for edge in engine.view(revision).find_references(symbol_id)]

    @app.get("/v1/graph/{symbol_id}")
    def graph(
        symbol_id: str,
        revision: str = "HEAD",
        depth: int = Query(2, ge=0, le=10),
        limit: int = Query(60, ge=1, le=200),
        reverse: bool = True,
        kinds: Annotated[list[EdgeType] | None, Query()] = None,
    ):
        return engine.view(revision).get_dependency_graph(
            symbol_id,
            depth=depth,
            limit=limit,
            reverse=reverse,
            kinds=tuple(kinds) if kinds else None,
        )

    @app.get("/v1/file")
    def file(path: str, revision: str = "HEAD"):
        if not safe_relative(path):
            raise HTTPException(400, "invalid repository path")
        snapshot = engine.view(revision).snapshot
        entry = snapshot.files.get(path)
        if entry is None or entry.status != "indexed":
            raise HTTPException(404, "file has no Python index")
        source, encoding = decode_python(next(engine.repository.blobs([entry])))
        return {"path": path, "commit": snapshot.commit, "source": source, "encoding": encoding}

    @app.get("/v1/impact")
    def impact(base: str, target: str, depth: int = Query(5, ge=0, le=15)):
        return asdict(engine.analyze_change_impact(base, target, depth=depth))

    @app.get("/v1/diff")
    def diff(base: str, target: str, path: str):
        if not safe_relative(path):
            raise HTTPException(400, "invalid repository path")
        old, new = engine.view(base).snapshot, engine.view(target).snapshot
        changes = engine.repository.changes(old.commit, new.commit)
        changed = next((item for item in changes if path in {item.old_path, item.new_path}), None)
        if changed is None:
            raise HTTPException(404, "file is outside the commit diff")
        path_specs: list[str] = []
        for snapshot, candidate in ((old, changed.old_path), (new, changed.new_path)):
            if candidate is None:
                continue
            entry = snapshot.files[candidate]
            if not safe_relative(candidate) or entry.size > 1_000_000:
                raise HTTPException(413, "diff is unavailable for this path or file size")
            path_specs.append(f":(literal){candidate}")
        content = engine.repository.git(
            "diff",
            "--no-ext-diff",
            "--no-textconv",
            "--no-color",
            "-M",
            old.commit,
            new.commit,
            "--",
            *dict.fromkeys(path_specs),
        )
        return {"path": path, "diff": content.decode("utf-8", "replace")}

    @app.get("/v1/tests")
    def tests(base: str, target: str, mode: str = "hybrid"):
        return asdict(engine.select_related_tests(base, target, mode=mode))

    @app.get("/v1/architecture")
    def architecture(base: str, target: str):
        if rules is None:
            raise HTTPException(404, "architecture rules were not configured")
        return compare(engine.view(base).snapshot, engine.view(target).snapshot, load_rules(rules))

    @app.post("/v1/refactoring/plan")
    def refactor(body: RefactorRequest):
        return asdict(
            engine.plan_refactoring(
                body.revision,
                body.symbol_id,
                body.name,
                operation=body.operation,
                value=body.value,
            )
        )

    @app.get("/v1/benchmark")
    def benchmark_summary():
        if benchmark is None or not benchmark.is_file():
            raise HTTPException(404, "benchmark artifacts were not configured")
        data = json.loads(benchmark.read_text(encoding="utf-8"))
        return {
            "repository": data["repository"],
            "base": data["base"],
            "target": data["target"],
            "index": data["B_release_incremental"],
        }

    return app


def from_environment() -> FastAPI:
    return create_app(
        os.environ["REPOGUARD_REPOSITORY"],
        os.environ.get("REPOGUARD_DATABASE", ".repoguard/index.sqlite"),
        write_token=os.environ.get("REPOGUARD_WRITE_TOKEN", ""),
        rules=Path(path) if (path := os.environ.get("REPOGUARD_RULES")) else None,
        benchmark=Path(path) if (path := os.environ.get("REPOGUARD_BENCHMARK")) else None,
    )
