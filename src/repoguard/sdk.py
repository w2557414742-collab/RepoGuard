"""CLI、FastAPI 和 MCP 共用的仓库分析入口。"""

from __future__ import annotations

from functools import cached_property
from pathlib import Path

from .graph import CodeGraph
from .impact import ImpactReport, analyze
from .indexer import DEFAULT_OPTIONS, Indexer, IndexOptions
from .model import Edge, EdgeType, Snapshot, Symbol
from .repository import Repository
from .retrieval import Hit, Search
from .store import Store
from .test_selection import CoverageMap, Selection, select


class View:
    """面向固定快照的查询视图。图与检索目录按需构造并缓存。"""

    def __init__(self, snapshot: Snapshot) -> None:
        self.snapshot = snapshot

    @cached_property
    def graph(self) -> CodeGraph:
        return CodeGraph(self.snapshot)

    @cached_property
    def searcher(self) -> Search:
        return Search(self.snapshot.symbols)

    def find_definition(self, query: str) -> list[Symbol]:
        return self.searcher.exact(query)

    def search_symbols(self, query: str, limit: int = 20) -> list[Hit]:
        return self.searcher.hybrid(query, limit, self.graph)

    def find_references(self, symbol_id: str) -> list[Edge]:
        return self.graph.adjacent(
            symbol_id,
            reverse=True,
            kinds=(EdgeType.REFERENCES, EdgeType.IMPORTS),
        )

    def get_callers(self, symbol_id: str) -> list[Edge]:
        return self.graph.adjacent(symbol_id, reverse=True, kinds=(EdgeType.CALLS,))

    def get_callees(self, symbol_id: str) -> list[Edge]:
        return self.graph.adjacent(symbol_id, kinds=(EdgeType.CALLS,))

    def get_dependency_graph(
        self,
        symbol_id: str,
        *,
        depth: int = 2,
        limit: int = 100,
        reverse: bool = False,
        kinds: tuple[EdgeType, ...] | None = None,
    ) -> dict[str, object]:
        """对固定快照进行有界邻接遍历并返回路径证据。最多探测 limit+1 个节点以识别截断。"""
        if not 1 <= limit <= 1000 or not 0 <= depth <= 10:
            raise ValueError("limit must be 1–1,000 and depth 0–10")
        filters = {"kinds": kinds} if kinds is not None else {}
        paths = self.graph.walk(
            [symbol_id], depth=depth, reverse=reverse, max_nodes=limit + 1, **filters
        )
        return {
            "version": self.snapshot.version,
            "nodes": [
                {
                    "id": sid,
                    **self.graph.graph.nodes[sid],
                    "symbol": self.graph.symbols.get(sid),
                    "evidence": evidence,
                }
                for sid, evidence in list(paths.items())[:limit]
            ],
            "truncated": len(paths) > limit,
        }


class RepoGuard:
    """配置仓库、SQLite 和索引器，提供事务发布、只读视图和跨版本工作流。"""

    def __init__(
        self,
        repository: str | Path,
        database: str | Path,
        *,
        options: IndexOptions = DEFAULT_OPTIONS,
        workers: int = 4,
    ) -> None:
        self.repository = Repository(repository)
        self.indexer = Indexer(self.repository, Store(database), options, workers)

    def index(self, revision: str = "HEAD", *, base: str | None = None) -> View:
        """发布或复用固定提交的索引，返回受该快照限制的 View。"""
        return View(self.indexer.index(revision, base=base))

    def view(self, revision: str = "HEAD") -> View:
        """打开已发布的提交视图，快照未发布时给出明确错误。"""
        snapshot = self.indexer.load(revision)
        if snapshot is None:
            raise ValueError("commit has no published index")
        return View(snapshot)

    def analyze_change_impact(
        self,
        base: str,
        target: str,
        *,
        depth: int = 5,
        coverage: CoverageMap | None = None,
        environment: str = "",
    ) -> ImpactReport:
        """加载基线和目标快照，匹配可选覆盖环境，再把文件差异交给双版本影响分析。"""
        old, new = self.view(base), self.view(target)
        files = self.repository.changes(
            old.snapshot.commit,
            new.snapshot.commit,
            with_lines=True,
            max_bytes=self.indexer.options.max_file_bytes,
        )
        edges = coverage.evidence_edges(old.snapshot, environment) if coverage else ()
        return analyze(old.snapshot, new.snapshot, files, depth=depth, base_coverage_edges=edges)

    def select_related_tests(
        self,
        base: str,
        target: str,
        *,
        mode: str = "hybrid",
        coverage: CoverageMap | None = None,
        environment: str = "",
    ) -> Selection:
        """将影响报告、目标快照和可选覆盖交给选择器，返回用例和回退理由。"""
        return select(
            self.analyze_change_impact(
                base,
                target,
                coverage=coverage if mode == "hybrid" else None,
                environment=environment,
            ),
            self.view(target).snapshot,
            mode=mode,
            coverage=coverage,
            environment=environment,
        )

    def plan_refactoring(
        self,
        revision: str,
        symbol_id: str,
        name: str,
        *,
        operation: str = "rename",
        value: str | None = None,
    ):
        from .refactoring import plan

        return plan(
            self.repository,
            self.view(revision).snapshot,
            symbol_id,
            name,
            operation=operation,
            value=value,
        )

    def plan_import_migration(self, revision: str, source_module: str, destination_module: str):
        from .import_migration import plan_module_move

        return plan_module_move(
            self.repository, self.view(revision).snapshot, source_module, destination_module
        )

    def validate_patch(self, revision: str, patch: str):
        from .verification import validate_patch

        return validate_patch(self.repository, self.view(revision).snapshot, patch)
