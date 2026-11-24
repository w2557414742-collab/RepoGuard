"""从快照构建有向多重图，提供位置证据、最短跳数与模块环查询。"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from itertools import islice

import networkx as nx

from .model import Confidence, Edge, EdgeType, Snapshot, identity

RELATIONS = frozenset(
    {
        EdgeType.CALLS,
        EdgeType.REFERENCES,
        EdgeType.IMPORTS,
        EdgeType.DEPENDS_ON,
        EdgeType.INHERITS,
        EdgeType.OVERRIDES,
        EdgeType.COVERS,
    }
)


class CodeGraph:
    """将 Snapshot 的文件、符号和边投影为 MultiDiGraph；无目标边另存作为诊断。"""

    def __init__(self, snapshot: Snapshot, extra_edges: Iterable[Edge] = ()) -> None:
        self.snapshot = snapshot
        self.symbols = snapshot.symbols
        self.graph = nx.MultiDiGraph()
        repo_id = snapshot.repository_id
        self.graph.add_node(repo_id, kind="repository")
        for path in snapshot.files:
            file_id = identity(repo_id, path, "file")
            self.graph.add_node(file_id, kind="file", path=path)
            self.graph.add_edge(
                repo_id,
                file_id,
                evidence=Edge(
                    repo_id,
                    file_id,
                    EdgeType.CONTAINS,
                    path,
                    1,
                    0,
                    Confidence.RESOLVED,
                    "git-inventory",
                ),
            )
        for sid, symbol in self.symbols.items():
            self.graph.add_node(sid, kind=symbol.kind, path=symbol.path)
        self.unresolved: list[Edge] = []
        for edges in snapshot.edges.values():
            for edge in edges:
                if edge.target is None:
                    self.unresolved.append(edge)
                else:
                    self.graph.add_edge(edge.source, edge.target, evidence=edge)
        for edge in extra_edges:
            if edge.source in self.graph and edge.target in self.graph:
                self.graph.add_edge(edge.source, edge.target, evidence=edge)

    def adjacent(
        self,
        sid: str,
        *,
        reverse: bool = False,
        kinds: Iterable[EdgeType] = RELATIONS,
    ) -> list[Edge]:
        """按邻接方向和边类型返回关系。空间取决于匹配边数，未知节点返回空列表。"""
        if sid not in self.graph:
            return []
        view = self.graph.in_edges if reverse else self.graph.out_edges
        allowed = set(kinds)
        return [edge for *_, edge in view(sid, data="evidence") if edge.kind in allowed]

    def walk(
        self,
        seeds: Iterable[str],
        *,
        reverse: bool = False,
        depth: int = 4,
        kinds: Iterable[EdgeType] = RELATIONS,
        max_nodes: int = 1000,
    ) -> dict[str, tuple[Edge, ...]]:
        """执行有深度和节点预算的多源 BFS。每节点保存首次到达的边序列，reverse 决定边的使用方向。

        队列和访问映射避免循环重复。除邻边排序外，遍历成本与可达图量相关，链复制额外占用 O(V·D)。
        """
        if not 0 <= depth <= 30 or max_nodes < 1:
            raise ValueError("depth must be 0–30 and max_nodes must be positive")
        walked: dict[str, tuple[Edge, ...]] = dict.fromkeys(
            islice((sid for sid in dict.fromkeys(seeds) if sid in self.graph), max_nodes),
            (),
        )
        queue = deque(walked)
        selected_kinds = frozenset(kinds)
        while queue:
            node = queue.popleft()
            if len(walked[node]) >= depth:
                continue
            neighbors = sorted(
                self.adjacent(node, reverse=reverse, kinds=selected_kinds),
                key=lambda e: (
                    e.confidence != Confidence.RESOLVED,
                    e.kind,
                    e.path,
                    e.line,
                    e.column,
                    e.source,
                    e.target or "",
                ),
            )
            for edge in neighbors:
                target = edge.source if reverse else edge.target
                if target is None or target in walked:
                    continue
                if len(walked) >= max_nodes:
                    return walked
                walked[target] = (*walked[node], edge)
                queue.append(target)
        return walked

    def shortest_path(
        self,
        source: str,
        target: str,
        kinds: Iterable[EdgeType] = RELATIONS,
        *,
        depth: int = 30,
    ) -> tuple[Edge, ...] | None:
        """从单源 BFS 取目标见证。路径度量为跳数，未在深度预算内到达返回 None。"""
        return self.walk([source], kinds=kinds, depth=depth, max_nodes=max(1, len(self.graph))).get(
            target
        )

    def cycles(self, kinds: Iterable[EdgeType] = (EdgeType.DEPENDS_ON,)) -> list[list[str]]:
        """筛选指定关系投影后取强连通分量，单节点只有自环时才报告为环。"""
        allowed = set(kinds)
        graph = nx.DiGraph(
            (left, right)
            for left, right, edge in self.graph.edges(data="evidence")
            if edge.kind in allowed
        )
        return sorted(
            sorted(component)
            for component in nx.strongly_connected_components(graph)
            if len(component) > 1 or any(graph.has_edge(node, node) for node in component)
        )
