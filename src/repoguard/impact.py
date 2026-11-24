"""基于两版符号、反向依赖和可信度证据分析 Git 变更。"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import PurePosixPath

from .graph import RELATIONS, CodeGraph
from .model import Confidence, Edge, EdgeType, FileChange, Snapshot, Symbol

CONFIG = re.compile(
    r"^(?:pyproject\.toml|pytest\.ini|tox\.ini|setup\.(?:py|cfg)|conftest\.py|"
    r"(?:uv|poetry|Pipfile)\.lock|Pipfile|requirements.*\.(?:txt|in)|"
    r"Dockerfile(?:\..*)?|(?:docker-)?compose.*\.ya?ml|\.python-version|"
    r".+\.(?:toml|ini|ya?ml|lock|cfg))$",
    re.IGNORECASE,
)
PUBLIC_KINDS = {"function", "method", "class"}
RISK = {
    "signature": 5.0,
    "removal": 5.0,
    "configuration": 5.0,
    "dependency": 4.0,
    "rename": 4.0,
    "unknown": 3.0,
    "implementation": 2.0,
    "addition": 1.5,
}
WEIGHTS = {
    EdgeType.CALLS: 1.0,
    EdgeType.REFERENCES: 0.82,
    EdgeType.IMPORTS: 0.88,
    EdgeType.DEPENDS_ON: 0.65,
    EdgeType.INHERITS: 0.9,
    EdgeType.OVERRIDES: 0.88,
    EdgeType.COVERS: 0.95,
    EdgeType.DEFINES: 0.7,
}


@dataclass(frozen=True, slots=True)
class SymbolChange:
    kind: str
    path: str
    before: Symbol | None
    after: Symbol | None
    public_api: bool = False


@dataclass(frozen=True, slots=True)
class Finding:
    symbol: Symbol
    seed: str
    version: str
    classification: str
    confidence: Confidence
    risk: float
    evidence: tuple[Edge, ...]


@dataclass(frozen=True, slots=True)
class ImpactReport:
    """变更、排序风险、循环关系、不确定边和回退条件的报告。"""

    base: str
    target: str
    files: list[FileChange]
    changes: list[SymbolChange]
    impacts: list[Finding]
    cycles: list[list[str]]
    uncertain: list[Edge]
    fallback_reasons: list[str]


def is_public(symbol: Symbol | None) -> bool:
    if not symbol or symbol.kind not in PUBLIC_KINDS or symbol.name.startswith("_"):
        return False
    return not any(
        part.startswith("_")
        for part in symbol.qualified_name.removeprefix(symbol.module + ".").split(".")
    )


def is_config(path: str) -> bool:
    return bool(CONFIG.fullmatch(PurePosixPath(path).name) or path.startswith(".github/workflows/"))


def risk_step(score: float, weight: float, uncertain: bool) -> float:
    """对单条关系按类型权重、固定距离衰减和可信度折扣更新风险。"""
    return score * 0.86 * weight * (0.55 if uncertain else 1.0)


def _imports(snapshot: Snapshot, path: str) -> set[tuple[str, str]]:
    unit = snapshot.units.get(path)
    if unit:
        return {(u.module, u.name) for u in unit.usages if u.kind == "IMPORTS"}
    return set()


def classify(base: Snapshot, target: Snapshot, files: list[FileChange]) -> list[SymbolChange]:
    """比较双侧 Unit 的符号 ID、签名、内容摘要及导入事实。分类包括签名、实现、增删、配置和未知变更。

    缺失解析事实时保留未知信号。每个改动路径的处理开销与其符号数量和排序成本有关。
    """
    result: list[SymbolChange] = []
    for file in files:
        old_path, new_path = file.old_path or "", file.new_path or ""
        path = new_path or old_path
        old, new = base.units.get(old_path), target.units.get(new_path)
        old_module = old.symbols[old.root_scope] if old else None
        new_module = new.symbols[new.root_scope] if new else None
        if is_config(path) or is_config(old_path):
            result.append(SymbolChange("configuration", path, old_module, new_module))
        if not (old or new):
            if not is_config(path):
                result.append(SymbolChange("unknown", path, None, None))
            continue
        if (old_path in base.files and old is None) or (new_path in target.files and new is None):
            result.append(SymbolChange("unknown", path, old_module, new_module))
            continue
        if file.status == "R":
            result.append(SymbolChange("rename", path, old_module, new_module))
        if _imports(base, old_path) != _imports(target, new_path):
            result.append(SymbolChange("dependency", path, old_module, new_module))
        before = (
            {s.id: s for s in old.symbols.values() if s.kind not in {"module", "parameter"}}
            if old
            else {}
        )
        after = (
            {s.id: s for s in new.symbols.values() if s.kind not in {"module", "parameter"}}
            if new
            else {}
        )
        local_changes = []
        for sid in sorted(before.keys() | after.keys()):
            left, right = before.get(sid), after.get(sid)
            if left is None:
                kind = "addition"
            elif right is None:
                kind = "removal"
            elif left.signature != right.signature:
                kind = "signature"
            elif left.content_hash != right.content_hash:
                kind = "implementation"
            else:
                continue
            local_changes.append(
                SymbolChange(
                    kind,
                    path,
                    left,
                    right,
                    kind in {"addition", "removal", "signature"}
                    and (is_public(left) or is_public(right)),
                )
            )
        if old_module is None or new_module is None or not local_changes:
            result.append(
                SymbolChange(
                    "addition"
                    if old_module is None
                    else "removal"
                    if new_module is None
                    else "implementation",
                    path,
                    old_module,
                    new_module,
                )
            )
        result.extend(local_changes)
    return result


def analyze(
    base: Snapshot,
    target: Snapshot,
    files: list[FileChange],
    *,
    depth: int = 5,
    kinds: Iterable[EdgeType] = RELATIONS,
    max_nodes: int = 2000,
    base_coverage_edges: Iterable[Edge] = (),
) -> ImpactReport:
    """接受基线、目标、文件改动与遍历参数，进行两版反向 BFS，并按证据与衰减排序。

    先使用变化符号和模块播种，在基线图保留已删除节点的调用者，最后合并风险较高的见证。
    路径是有界 BFS 的一个证据，风险用于排序，动态未知和遍历预算会触发保守回退。
    """
    if base.repository_id != target.repository_id or base.options != target.options:
        raise ValueError("impact requires matching repository and index options")
    if not 0 <= depth <= 30 or not 1 <= max_nodes <= 50_000:
        raise ValueError("depth must be 0–30 and max_nodes must be 1–50,000")
    changes = classify(base, target, files)
    old_graph, new_graph = CodeGraph(base, base_coverage_edges), CodeGraph(target)
    selected = frozenset(kinds)
    fallback = {
        f"{change.kind}: {change.path}"
        for change in changes
        if change.kind in {"configuration", "unknown"}
    }
    findings: dict[str, Finding] = {}
    uncertainty: dict[tuple[str, int, int, str], Edge] = {}
    for graph, before in ((old_graph, True), (new_graph, False)):
        seeds: dict[str, float] = {}
        for change in changes:
            symbol = change.before if before else change.after
            if symbol:
                seeds[symbol.id] = max(seeds.get(symbol.id, 0), RISK[change.kind])
                module = graph.snapshot.units[symbol.path].root_scope
                seeds[module] = max(seeds.get(module, 0), RISK[change.kind] * 0.55)
        paths = graph.walk(
            sorted(seeds, key=lambda sid: (-seeds[sid], sid)),
            reverse=True,
            depth=depth,
            kinds=selected,
            max_nodes=max_nodes,
        )
        if len(paths) >= max_nodes:
            fallback.add("impact traversal reached its node budget")
        affected = set(paths)
        for sid, chain in paths.items():
            if not chain or sid not in graph.symbols:
                continue
            certainty = Confidence.RESOLVED
            score = seeds[chain[0].target]
            for edge in chain:
                uncertain = edge.confidence != Confidence.RESOLVED
                score = risk_step(score, WEIGHTS.get(edge.kind, 0.6), uncertain)
                if uncertain:
                    certainty = Confidence.POSSIBLE
            candidate = Finding(
                graph.symbols[sid],
                chain[0].target,
                graph.snapshot.version,
                "potential"
                if certainty == Confidence.POSSIBLE
                else "direct"
                if len(chain) == 1
                else "indirect",
                certainty,
                round(score, 6),
                chain,
            )
            if sid not in findings or candidate.risk >= findings[sid].risk:
                findings[sid] = candidate
        for path in {graph.symbols[sid].path for sid in affected if sid in graph.symbols}:
            for edge in graph.snapshot.edges.get(path, ()):
                if edge.confidence == Confidence.RESOLVED or edge.kind not in selected:
                    continue
                if edge.kind not in {EdgeType.CALLS, EdgeType.IMPORTS, EdgeType.INHERITS}:
                    continue
                if edge.source in affected or edge.kind == EdgeType.IMPORTS:
                    uncertainty[(edge.path, edge.line, edge.column, edge.expression)] = edge
    if any(edge.kind == EdgeType.CALLS and edge.target is None for edge in uncertainty.values()):
        fallback.add("unresolved calls in the impact subgraph")
    if any(change.public_api and change.kind in {"signature", "removal"} for change in changes):
        fallback.add("public API signature or removal")
    candidate_paths = {c.path for c in changes} | {f.symbol.path for f in findings.values()}
    cycles = [
        group
        for group in new_graph.cycles()
        if any(new_graph.symbols[sid].path in candidate_paths for sid in group)
    ]
    return ImpactReport(
        base.commit,
        target.commit,
        files,
        changes,
        sorted(findings.values(), key=lambda f: (-f.risk, f.symbol.path, f.symbol.line)),
        cycles,
        list(uncertainty.values()),
        sorted(fallback),
    )


def markdown(report: ImpactReport) -> str:
    """把结构化影响报告转换为可审查 Markdown，列出位置、边证据、不确定性及验证建议。"""

    def escaped(value: str) -> str:
        return value.replace("|", "\\|").replace("\n", " ")

    lines = [
        "# RepoGuard change review",
        "",
        f"`{report.base}` → `{report.target}`",
        "",
        "## Changes",
        "",
        "| Kind | Symbol or file | Public API |",
        "|---|---|---|",
    ]
    for change in report.changes:
        symbol = change.after or change.before
        label = symbol.qualified_name if symbol else change.path
        lines.append(
            f"| {change.kind} | {escaped(label)} | {'yes' if change.public_api else '—'} |"
        )
    lines.extend(
        [
            "",
            "## Impact evidence",
            "",
            "| Location | Classification | Risk | Evidence |",
            "|---|---|---:|---|",
        ]
    )
    for item in report.impacts:
        chain = " ← ".join(f"{e.kind} {e.path}:{e.line} ({e.confidence})" for e in item.evidence)
        lines.append(
            f"| {escaped(item.symbol.path)}:{item.symbol.line} | {item.classification} | "
            f"{item.risk:.3f} | {escaped(chain)} |"
        )
    lines.extend(["", "## Validation"])
    if report.fallback_reasons:
        lines.extend(
            ["", "Run the full suite.", "", *[f"- {escaped(r)}" for r in report.fallback_reasons]]
        )
    else:
        lines.extend(["", "Run related tests and review coverage freshness."])
    lines += [
        "",
        f"- Cyclic dependency components: {len(report.cycles)}",
        f"- Uncertain relationships: {len(report.uncertain)}",
    ]
    for edge in report.uncertain:
        lines.append(f"  - {escaped(edge.path)}:{edge.line} {edge.kind} {escaped(edge.expression)}")
    return "\n".join(lines) + "\n"
