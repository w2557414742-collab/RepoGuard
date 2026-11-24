"""以解析证据和 LibCST 生成可审查的 Python 重构补丁。"""

from __future__ import annotations

import ast
import difflib
import json
import keyword
from collections import Counter
from dataclasses import dataclass, replace

import libcst as cst
from libcst.metadata import MetadataWrapper, PositionProvider

from .model import Confidence, Edge, EdgeType, Snapshot, Symbol
from .parser import decode_python, parse
from .repository import Repository, safe_relative
from .resolution import Catalog, Resolver

Position = tuple[int, int]
SEMANTIC = {
    EdgeType.CALLS,
    EdgeType.REFERENCES,
    EdgeType.IMPORTS,
    EdgeType.INHERITS,
    EdgeType.OVERRIDES,
}


@dataclass(frozen=True, slots=True)
class Plan:
    """记录候选改动文件、阻塞原因、检查结果和统一差异；计划对象本身不写入项目。"""

    operation: str
    symbol: Symbol
    files: list[str]
    blockers: list[str]
    checks: dict[str, str]
    patch: str
    api_change: str


class Rewrite(cst.CSTTransformer):
    """根据可信位置改写 CST 名称、函数定义和调用，保留结构化格式和注释。"""

    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(
        self,
        target: Position | None,
        positions: set[Position],
        operation: str,
        name: str,
        value: cst.BaseExpression | None,
        original: str,
    ) -> None:
        self.target, self.positions, self.operation = target, positions, operation
        self.name, self.value, self.original = name, value, original
        self.changed: set[Position] = set()
        self.problems: list[str] = []

    def position(self, node: cst.CSTNode) -> Position:
        p = self.get_metadata(PositionProvider, node).start
        return p.line, p.column

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.Name:
        """仅在匹配的源码坐标上替换原标识符，将修改位置登记给规划器逐项核对。"""
        if (
            self.operation == "rename"
            and original_node.value == self.original
            and (position := self.position(original_node)) in self.positions
        ):
            self.changed.add(position)
            return updated_node.with_changes(value=self.name)
        return updated_node

    def leave_ImportAlias(
        self,
        original_node: cst.ImportAlias,
        updated_node: cst.ImportAlias,
    ) -> cst.ImportAlias:
        alias = updated_node.asname
        if (
            self.operation == "rename"
            and alias
            and isinstance(alias.name, cst.Name)
            and alias.name.value == self.original
            and original_node.name != updated_node.name
            and self.position(original_node.name) in self.changed
        ):
            return updated_node.with_changes(
                asname=alias.with_changes(
                    name=alias.name.with_changes(value=self.name),
                )
            )
        return updated_node

    def leave_Assign(self, original_node: cst.Assign, updated_node: cst.Assign) -> cst.Assign:
        if (
            self.operation != "rename"
            or not any(
                isinstance(t.target, cst.Name) and t.target.value == "__all__"
                for t in original_node.targets
            )
            or not isinstance(updated_node.value, (cst.List, cst.Tuple))
        ):
            return updated_node
        items = []
        for item in updated_node.value.elements:
            if (
                isinstance(item, cst.Element)
                and isinstance(item.value, cst.SimpleString)
                and item.value.evaluated_value == self.original
            ):
                text = item.value.value.replace(self.original, self.name)
                item = item.with_changes(value=item.value.with_changes(value=text))
            items.append(item)
        return updated_node.with_changes(value=updated_node.value.with_changes(elements=items))

    def leave_FunctionDef(
        self,
        original_node: cst.FunctionDef,
        updated_node: cst.FunctionDef,
    ) -> cst.FunctionDef:
        """按目标定义坐标重命名或添加仅关键字参数，保留原参数节点。"""
        if self.position(original_node) != self.target:
            return updated_node
        self.changed.add(self.target)
        if self.operation == "rename":
            return updated_node.with_changes(name=updated_node.name.with_changes(value=self.name))
        params = updated_node.params
        return updated_node.with_changes(
            params=params.with_changes(
                kwonly_params=(*params.kwonly_params, cst.Param(cst.Name(self.name))),
            )
        )

    def leave_ClassDef(
        self,
        original_node: cst.ClassDef,
        updated_node: cst.ClassDef,
    ) -> cst.ClassDef:
        if self.position(original_node) != self.target or self.operation != "rename":
            return updated_node
        self.changed.add(self.target)
        return updated_node.with_changes(name=updated_node.name.with_changes(value=self.name))

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        """在可确认的调用点补入用户提供的字面量。现有同名关键字或参数展开进入阻塞记录。"""
        if self.operation != "signature":
            return updated_node
        func = original_node.func
        position = self.position(func.attr if isinstance(func, cst.Attribute) else func)
        if position not in self.positions:
            return updated_node
        if any(
            arg.star or (arg.keyword and arg.keyword.value == self.name)
            for arg in original_node.args
        ):
            self.problems.append(
                f"call at line {position[0]} has unpacking or an existing {self.name} argument"
            )
            return updated_node
        self.changed.add(position)
        return updated_node.with_changes(
            args=(
                *updated_node.args,
                cst.Arg(self.value, keyword=cst.Name(self.name)),
            )
        )


def unified_patch(changed: dict[str, tuple[str | None, str | None]]) -> str:
    """将原旧与新内容映射生成统一差异，保留无末尾换行标记；拒绝不安全路径。"""
    output = []
    for path, (before, after) in sorted(changed.items()):
        if not safe_relative(path) or any(c in path for c in "\t\n\r"):
            raise ValueError("path cannot be represented safely in a unified patch")
        if before == after:
            continue
        old_name = (
            (f"a/{path}\t" if " " in path else f"a/{path}") if before is not None else "/dev/null"
        )
        new_name = (
            (f"b/{path}\t" if " " in path else f"b/{path}") if after is not None else "/dev/null"
        )
        for line in difflib.unified_diff(
            (before or "").splitlines(keepends=True),
            (after or "").splitlines(keepends=True),
            old_name,
            new_name,
        ):
            output.append(
                line if line.endswith("\n") else line + "\n\\ No newline at end of file\n"
            )
    return "".join(output)


def semantic_counts(
    symbols: dict[str, Symbol],
    edges: list[Edge],
    renamed: dict[str, str],
    moved_paths: dict[str, str] | None = None,
) -> Counter[tuple]:
    """按映射后的定义身份和边种类统计确定关系，供 before/after 对照。"""

    def label(sid: str) -> tuple[str, str, str]:
        symbol = symbols[sid]
        return (
            (moved_paths or {}).get(symbol.path, symbol.path),
            renamed.get(sid, symbol.qualified_name),
            symbol.kind,
        )

    return Counter(
        (label(edge.source), label(edge.target), edge.kind)
        for edge in edges
        if edge.kind in SEMANTIC
        and edge.confidence == Confidence.RESOLVED
        and edge.source in symbols
        and edge.target in symbols
    )


def plan(
    repo: Repository,
    snapshot: Snapshot,
    symbol_id: str,
    name: str,
    *,
    operation: str = "rename",
    value: str | None = None,
) -> Plan:
    """输入仓库快照、符号 ID 与重构选项，输出候选补丁及逐项检查状态。

    在可信引用位置改写 CST，重解析文件，再比较前后确定边的计数；存在阻塞则输出原因。变换仅支持声明的模块级场景。
    主要开销来自受影响 CST 及重建语义目录和解析边。静态一致性不能覆盖所有运行时行为。
    """
    symbols = snapshot.symbols
    if snapshot.repository_id != repo.id or symbol_id not in symbols:
        raise ValueError("target symbol must belong to the selected repository snapshot")
    if (
        operation not in {"rename", "signature"}
        or not name.isidentifier()
        or keyword.iskeyword(name)
    ):
        raise ValueError("provide a valid operation and Python identifier")
    symbol = symbols[symbol_id]
    title = (
        f"{symbol.qualified_name} → {symbol.module}.{name}"
        if operation == "rename"
        else (f"{symbol.qualified_name} requires keyword argument {name}")
    )
    blockers = []
    positions: dict[str, set[Position]] = {symbol.path: set()}
    checks = {
        "syntax": "pending",
        "reference_consistency": "pending",
        "types": "not_run",
        "tests": "not_run",
        "api_compatibility": "breaking_change",
    }
    literal: cst.BaseExpression | None = None
    if operation == "signature":
        if value is None:
            raise ValueError("signature migration requires an explicit Python literal")
        ast.literal_eval(value)
        literal = cst.parse_expression(value)
    if symbol.kind not in ({"function", "class"} if operation == "rename" else {"function"}) or (
        symbol.parent is None or symbols[symbol.parent].kind != "module"
    ):
        blockers.append("choose a module-level function or class supported by this transformation")
    if symbol.intrinsically_uncertain:
        blockers.append("the target has runtime decorators")
    if operation == "rename" and symbol.name == name:
        blockers.append("the new name matches the original")
    if (
        operation == "signature"
        and name
        in snapshot.units[symbol.path]
        .scopes.get(symbol.id, snapshot.units[symbol.path].scopes[symbol.scope_id])
        .bindings
    ):
        blockers.append(f"{name} is already bound in the target function")
    before_edges = [edge for edges in snapshot.edges.values() for edge in edges]
    calls = {
        (e.path, e.line, e.column)
        for e in before_edges
        if e.kind == EdgeType.CALLS
        and e.target == symbol_id
        and e.confidence == Confidence.RESOLVED
    }
    for edge in before_edges:
        location = edge.path, edge.line, edge.column
        if edge.target == symbol_id and edge.confidence == Confidence.POSSIBLE:
            blockers.append(f"{edge.path}:{edge.line} has a possible target ({edge.expression})")
        if edge.target is None and edge.expression.rsplit(".", 1)[-1].split(":")[-1] == symbol.name:
            blockers.append(f"{edge.path}:{edge.line} has an unresolved use ({edge.expression})")
        if edge.target != symbol_id or edge.confidence != Confidence.RESOLVED:
            continue
        if operation == "rename":
            if (
                edge.kind in SEMANTIC
                and edge.expression.rsplit(".", 1)[-1].split(":")[-1] == symbol.name
            ):
                positions.setdefault(edge.path, set()).add(location[1:])
        elif edge.kind == EdgeType.CALLS:
            positions.setdefault(edge.path, set()).add(location[1:])
        elif edge.kind == EdgeType.REFERENCES and location not in calls:
            blockers.append(f"{edge.path}:{edge.line} passes the function as a value")
    for path, unit in snapshot.units.items():
        for use in unit.usages:
            if use.kind == "IMPORTS" and use.name == "*" and use.module == symbol.module:
                blockers.append(f"{path}:{use.line} imports the target module with a wildcard")
    if any(
        f.status in {"parse_error", "too_large", "binary", "unsafe_path"}
        for f in snapshot.files.values()
        if f.path.endswith(".py")
    ):
        blockers.append("one or more Python files could not be analyzed")

    def result(patch: str = "") -> Plan:
        return Plan(
            operation, symbol, sorted(positions), sorted(set(blockers)), checks, patch, title
        )

    if blockers:
        return result()
    if operation == "rename":
        for path in positions:
            if any(name in scope.bindings for scope in snapshot.units[path].scopes.values()):
                blockers.append(f"{path} already binds {name}")
    if blockers:
        return result()

    changes: dict[str, tuple[str | None, str | None]] = {}
    updated_units = dict(snapshot.units)
    roots = tuple(json.loads(snapshot.options)[2]["roots"])
    for file, raw in zip(
        (snapshot.files[p] for p in positions),
        repo.blobs(snapshot.files[p] for p in positions),
        strict=True,
    ):
        source, encoding = decode_python(raw)
        if encoding not in {"utf-8", "ascii"}:
            blockers.append(f"{file.path} uses {encoding}, unsupported for patch output")
            continue
        definition = (symbol.line, symbol.column) if file.path == symbol.path else None
        transform = Rewrite(definition, positions[file.path], operation, name, literal, symbol.name)
        try:
            rewritten = MetadataWrapper(cst.parse_module(source)).visit(transform).code
        except (cst.ParserSyntaxError, cst.CSTValidationError) as exc:
            blockers.append(f"{file.path} could not be rewritten: {exc}")
            continue
        missing = (
            positions[file.path] | ({definition} if definition else set())
        ) - transform.changed
        if missing:
            blockers.append(f"{file.path} has unmatched source locations {sorted(missing)}")
        blockers.extend(f"{file.path}: {message}" for message in transform.problems)
        parsed, unit = parse(
            replace(file, size=len(rewritten.encode(encoding))),
            rewritten.encode(encoding),
            repo.id,
            roots,
        )
        if unit is None:
            blockers.append(f"{file.path} failed syntax validation: {parsed.detail}")
        else:
            updated_units[file.path] = unit
            changes[file.path] = (source, rewritten)
    if blockers:
        checks["syntax"] = "failed_or_incomplete"
        return result()
    checks["syntax"] = "passed"
    renamed = {}
    if operation == "rename":
        for sid, item in symbols.items():
            if item.path == symbol.path and (
                item.qualified_name == symbol.qualified_name
                or item.qualified_name.startswith(symbol.qualified_name + ".")
            ):
                renamed[sid] = f"{symbol.module}.{name}" + item.qualified_name.removeprefix(
                    symbol.qualified_name
                )
    catalog = Catalog(updated_units)
    actual_edges = [
        edge for unit in updated_units.values() for edge in Resolver(catalog).resolve(unit)[0]
    ]
    actual_symbols = {sid: s for unit in updated_units.values() for sid, s in unit.symbols.items()}
    expected = semantic_counts(symbols, before_edges, renamed)
    actual = semantic_counts(actual_symbols, actual_edges, {})
    if expected != actual:
        missing, introduced = sum((expected - actual).values()), sum((actual - expected).values())
        blockers.append(
            f"reference check found {missing} missing and {introduced} new resolved edges"
        )
        checks["reference_consistency"] = "failed"
        return result()
    checks["reference_consistency"] = "passed"
    return result(unified_patch(changes))
