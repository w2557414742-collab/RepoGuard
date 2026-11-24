"""从版本化图检查 YAML 模块边界规则，并区分新增、已有和解除。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .graph import CodeGraph
from .model import Edge, EdgeType, Snapshot, Symbol


@dataclass(frozen=True, slots=True)
class Rule:
    """架构约束的数据结构，包括来源、目标限制、白名单和耦合数。"""

    name: str
    source: str = ""
    forbidden_dependency: str = ""
    allowed_dependencies: tuple[str, ...] | None = None
    kind: str = "dependency"
    max_dependencies: int = 0


@dataclass(frozen=True, slots=True)
class Violation:
    """用规则和模块身份描述一个架构关系，并保存影响地点。"""

    rule: str
    source: str
    target: str
    evidence: tuple[Edge, ...]


def load_rules(path: Path) -> list[Rule]:
    """用安全 YAML 载入大小受限的规则文件，转换为明确的数据结构并检查名称及参数。"""
    import yaml

    with path.open(encoding="utf-8") as stream:
        raw = stream.read(128 * 1024 + 1)
    if len(raw) > 128 * 1024:
        raise ValueError("architecture configuration is limited to 128 KiB")
    data = yaml.safe_load(raw)
    if not isinstance(data, dict) or not isinstance(data.get("rules"), list):
        raise TypeError("expected a rules list")
    rules = []
    for item in data["rules"]:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not item["name"]:
            raise ValueError("every rule must have a name")
        allowed = item.get("allowed_dependencies")
        if allowed is not None and (
            not isinstance(allowed, list) or not all(isinstance(value, str) for value in allowed)
        ):
            raise ValueError("allowed_dependencies must be a list of module prefixes")
        actual = {key: value for key, value in item.items() if key != "allowed_dependencies"}
        rule = Rule(**actual, allowed_dependencies=tuple(allowed) if allowed is not None else None)
        if rule.kind not in {
            "dependency",
            "layer",
            "cycles",
            "public_api",
            "coupling",
            "new_dependency",
        }:
            raise ValueError(f"unknown architecture rule kind {rule.kind}")
        if not isinstance(rule.source, str) or not isinstance(rule.forbidden_dependency, str):
            raise TypeError("source and forbidden_dependency must be strings")
        if not isinstance(rule.max_dependencies, int) or rule.max_dependencies < 0:
            raise ValueError("max_dependencies must be a nonnegative integer")
        rules.append(rule)
    if len({rule.name for rule in rules}) != len(rules):
        raise ValueError("rule names must be unique")
    return rules


def matches(module: str, prefix: str) -> bool:
    return not prefix or module == prefix or module.startswith(prefix + ".")


def dependencies(snapshot: Snapshot) -> list[tuple[Symbol, Symbol, Edge]]:
    symbols = snapshot.symbols
    return [
        (symbols[edge.source], symbols[edge.target], edge)
        for edges in snapshot.edges.values()
        for edge in edges
        if edge.kind == EdgeType.DEPENDS_ON and edge.source in symbols and edge.target in symbols
    ]


def evaluate(snapshot: Snapshot, rules: list[Rule]) -> dict[tuple[str, str, str], Violation]:
    """对单个快照应用依赖、边界、环和耦合规则，返回与源码行独立的违规键。"""
    graph = CodeGraph(snapshot)
    edges = dependencies(snapshot)
    found = {}
    for rule in rules:
        if rule.kind == "cycles":
            for group in graph.cycles():
                group_set = set(group)
                modules = sorted({graph.symbols[sid].module for sid in group})
                if not any(matches(module, rule.source) for module in modules):
                    continue
                evidence = tuple(e for a, b, e in edges if a.id in group_set and b.id in group_set)
                key = (rule.name, ", ".join(modules), "")
                found[key] = Violation(*key, evidence)
            continue
        if rule.kind == "public_api":
            for part in snapshot.edges.values():
                for edge in part:
                    if edge.kind != EdgeType.IMPORTS or edge.target not in graph.symbols:
                        continue
                    source, dest = graph.symbols[edge.source], graph.symbols[edge.target]
                    relative = dest.qualified_name.removeprefix(dest.module + ".")
                    restricted = (dest.kind != "module" and relative.startswith("_")) or any(
                        p.startswith("_") for p in dest.module.split(".")
                    )
                    if (
                        source.module != dest.module
                        and matches(source.module, rule.source)
                        and matches(dest.module, rule.forbidden_dependency)
                        and restricted
                    ):
                        key = rule.name, source.module, dest.qualified_name
                        found[key] = Violation(*key, (edge,))
            continue
        grouped: dict[tuple[str, str], list[Edge]] = {}
        for source, dest, edge in edges:
            if not matches(source.module, rule.source):
                continue
            grouped.setdefault((source.module, dest.module), []).append(edge)
        if rule.kind == "coupling":
            for module in {source for source, _ in grouped}:
                outgoing = {
                    dest: values for (source, dest), values in grouped.items() if source == module
                }
                if len(outgoing) > rule.max_dependencies:
                    key = rule.name, module, ""
                    found[key] = Violation(
                        *key, tuple(e for values in outgoing.values() for e in values)
                    )
            continue
        for (source, target), evidence in grouped.items():
            forbidden = bool(rule.forbidden_dependency) and matches(
                target, rule.forbidden_dependency
            )
            outside = rule.allowed_dependencies is not None and not any(
                matches(target, prefix) for prefix in rule.allowed_dependencies
            )
            if forbidden or outside or rule.kind == "new_dependency":
                key = rule.name, source, target
                found[key] = Violation(*key, tuple(evidence))
    return found


def compare(base: Snapshot, target: Snapshot, rules: list[Rule]) -> dict[str, list[Violation]]:
    """分别评估基线和目标，按违规键计算差集和交集。new_dependency 只关注引入项。"""
    old, new = evaluate(base, rules), evaluate(target, rules)
    additions_only = {rule.name for rule in rules if rule.kind == "new_dependency"}
    return {
        "introduced": [new[key] for key in sorted(new.keys() - old.keys())],
        "existing": [
            new[key] for key in sorted(new.keys() & old.keys()) if key[0] not in additions_only
        ],
        "resolved": [
            old[key] for key in sorted(old.keys() - new.keys()) if key[0] not in additions_only
        ],
    }
