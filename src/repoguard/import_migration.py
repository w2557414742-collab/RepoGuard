"""为完整 Python 模块移动生成导入更新及统一差异。"""

from __future__ import annotations

import json
import keyword
from dataclasses import replace

import libcst as cst
from libcst.helpers import get_full_name_for_node
from libcst.metadata import MetadataWrapper, PositionProvider

from .model import Confidence, EdgeType, Snapshot, Unit
from .parser import decode_python, parse
from .refactoring import Plan, semantic_counts, unified_patch
from .repository import Repository, safe_relative
from .resolution import Catalog, Resolver


class ImportRewrite(cst.CSTTransformer):
    """根据旧、新模块名和源码位置更新直接或相对导入，保留适用的本地别名。"""

    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(
        self,
        unit: Unit,
        old: str,
        new: str,
        attributes: set[tuple[int, int]],
    ) -> None:
        self.unit, self.old, self.new = unit, old, new
        self.old_parent, _, self.old_leaf = old.rpartition(".")
        self.new_parent, _, self.new_leaf = new.rpartition(".")
        self.package = (
            unit.module if unit.path.endswith("/__init__.py") else unit.module.rpartition(".")[0]
        )
        self.attributes = attributes
        self.problems: list[str] = []

    def leave_Import(self, original_node: cst.Import, updated_node: cst.Import) -> cst.Import:
        names = []
        for alias in updated_node.names:
            if get_full_name_for_node(alias.name) == self.old:
                asname = alias.asname
                if not asname and not self.old_parent:
                    asname = cst.AsName(cst.Name(self.old_leaf))
                elif not asname and self.old_parent != self.new_parent:
                    self.problems.append(
                        "a dotted import without an alias crosses a package boundary"
                    )
                alias = alias.with_changes(name=cst.parse_expression(self.new), asname=asname)
            names.append(alias)
        return updated_node.with_changes(names=names)

    def leave_ImportFrom(
        self,
        original_node: cst.ImportFrom,
        updated_node: cst.ImportFrom,
    ) -> cst.BaseSmallStatement:
        module = get_full_name_for_node(updated_node.module) or ""
        if updated_node.relative:
            parts = self.package.split(".") if self.package else []
            level = len(updated_node.relative)
            if len(parts) < level:
                self.problems.append("relative import goes beyond its package")
                return updated_node
            module = ".".join([*parts[: len(parts) - level + 1], *([module] if module else [])])
        if module == self.old:
            if isinstance(updated_node.names, cst.ImportStar):
                self.problems.append("wildcard import of the moved module")
            return updated_node.with_changes(module=cst.parse_expression(self.new), relative=())
        if module == self.old_parent and not isinstance(updated_node.names, cst.ImportStar):
            old_alias = next(
                (
                    alias
                    for alias in updated_node.names
                    if get_full_name_for_node(alias.name) == self.old_leaf
                ),
                None,
            )
            if old_alias:
                if len(updated_node.names) != 1:
                    self.problems.append("the moved module shares a from-import with other names")
                    return updated_node
                if not self.new_parent:
                    self.problems.append(
                        "a package member cannot migrate to an unpackaged import here"
                    )
                    return updated_node
                alias = old_alias.with_changes(name=cst.Name(self.new_leaf))
                if not alias.asname and self.old_leaf != self.new_leaf:
                    alias = alias.with_changes(asname=cst.AsName(cst.Name(self.old_leaf)))
                return updated_node.with_changes(
                    module=cst.parse_expression(self.new_parent),
                    relative=(),
                    names=(alias,),
                )
        if (
            updated_node.relative
            and self.unit.module == self.old
            and self.new_parent != self.old_parent
        ):
            return updated_node.with_changes(module=cst.parse_expression(module), relative=())
        return updated_node

    def leave_Attribute(
        self,
        original_node: cst.Attribute,
        updated_node: cst.Attribute,
    ) -> cst.Attribute:
        position = self.get_metadata(PositionProvider, original_node.attr).start
        if (position.line, position.column) in self.attributes and get_full_name_for_node(
            original_node
        ) == self.old:
            if self.old_parent != self.new_parent:
                self.problems.append("a dotted module reference crosses a package boundary")
            else:
                return updated_node.with_changes(attr=cst.Name(self.new_leaf))
        return updated_node


def plan_module_move(repo: Repository, snapshot: Snapshot, old: str, new: str) -> Plan:
    """预览普通模块的跨文件迁移。验证路径与导入形态、运行 LibCST 写出补丁草稿，再验证重解析和确定引用计数。

    遇到通配、二义或索引不足时阻塞。成本主要为变更文件 CST 与重建关系。
    """
    if snapshot.repository_id != repo.id or any(
        not part.isidentifier() or keyword.iskeyword(part)
        for module in (old, new)
        for part in module.split(".")
    ):
        raise ValueError("provide valid dotted modules in the selected repository")
    sources = [unit for unit in snapshot.units.values() if unit.module == old]
    if len(sources) != 1:
        raise ValueError("old module must match one indexed source file")
    original = sources[0]
    symbol = original.symbols[original.root_scope]
    suffix = old.replace(".", "/") + ".py"
    checks = {
        "syntax": "pending",
        "reference_consistency": "pending",
        "types": "not_run",
        "tests": "not_run",
        "api_compatibility": "breaking_change",
    }
    blockers: list[str] = []
    files: set[str] = {original.path}

    def result(patch: str = "") -> Plan:
        return Plan(
            "import-move",
            symbol,
            sorted(files),
            sorted(set(blockers)),
            checks,
            patch,
            f"{old} → {new}",
        )

    if not original.path.endswith(suffix) or original.path.endswith("/__init__.py"):
        blockers.append("this migration moves ordinary Python modules")
        return result()
    dest = original.path.removesuffix(suffix) + new.replace(".", "/") + ".py"
    files.add(dest)
    if not safe_relative(dest) or dest in snapshot.files:
        blockers.append("the requested destination already exists or is invalid")
    new_parent = new.rpartition(".")[0]
    if new_parent and not any(
        unit.path != original.path
        and (unit.module == new_parent or unit.module.startswith(new_parent + "."))
        for unit in snapshot.units.values()
    ):
        blockers.append("the destination package is not indexed")
    if any(
        entry.path.endswith(".py")
        and entry.status in {"binary", "parse_error", "too_large", "unsafe_path"}
        for entry in snapshot.files.values()
    ):
        blockers.append("one or more Python files could not be analyzed")
    if blockers:
        return result()
    attributes: dict[str, set[tuple[int, int]]] = {}
    old_parent, _, old_leaf = old.rpartition(".")
    for path, unit in snapshot.units.items():
        for use in unit.usages:
            if use.kind == "IMPORTS" and (
                use.module == old or (use.module == old_parent and use.name in {old_leaf, "*"})
            ):
                files.add(path)
                if use.name == "*":
                    blockers.append(f"{path}:{use.line} has a wildcard import")
        for edge in snapshot.edges[path]:
            if (
                edge.kind == EdgeType.REFERENCES
                and edge.expression == old
                and edge.target == symbol.id
            ):
                if edge.confidence == Confidence.POSSIBLE:
                    blockers.append(f"{path}:{edge.line} has an ambiguous module reference")
                elif "." in old:
                    files.add(path)
                    attributes.setdefault(path, set()).add((edge.line, edge.column))
    if blockers:
        return result()
    updated_units = dict(snapshot.units)
    changes: dict[str, tuple[str | None, str | None]] = {}
    roots = tuple(json.loads(snapshot.options)[2]["roots"])
    to_read = [snapshot.files[path] for path in sorted(files - {dest})]
    for file, raw in zip(to_read, repo.blobs(to_read), strict=True):
        source, encoding = decode_python(raw)
        if encoding not in {"ascii", "utf-8"} or not source:
            blockers.append(
                f"{file.path} has an encoding or empty content unsupported by this patch"
            )
            continue
        transformer = ImportRewrite(
            snapshot.units[file.path], old, new, attributes.get(file.path, set())
        )
        try:
            updated = MetadataWrapper(cst.parse_module(source)).visit(transformer).code
        except (cst.ParserSyntaxError, cst.CSTValidationError) as exc:
            blockers.append(f"{file.path}: {exc}")
            continue
        blockers.extend(f"{file.path}: {issue}" for issue in transformer.problems)
        path = dest if file.path == original.path else file.path
        raw = updated.encode(encoding)
        parsed, unit = parse(replace(file, path=path, size=len(raw)), raw, repo.id, roots)
        if unit is None:
            blockers.append(f"{file.path}: {parsed.detail}")
            continue
        updated_units[path] = unit
        if path == dest:
            del updated_units[file.path]
            changes[file.path] = (source, None)
            changes[dest] = (None, updated)
        elif source != updated:
            changes[path] = (source, updated)
    if blockers:
        checks["syntax"] = "failed_or_incomplete"
        return result()
    checks["syntax"] = "passed"
    renamed = {s.id: new + s.qualified_name.removeprefix(old) for s in original.symbols.values()}
    expected = semantic_counts(
        snapshot.symbols,
        [edge for group in snapshot.edges.values() for edge in group],
        renamed,
        {original.path: dest},
    )
    catalog = Catalog(updated_units)
    actual_edges = [
        edge for unit in updated_units.values() for edge in Resolver(catalog).resolve(unit)[0]
    ]
    actual_symbols = {sid: s for unit in updated_units.values() for sid, s in unit.symbols.items()}
    if expected != semantic_counts(actual_symbols, actual_edges, {}):
        blockers.append("module move changes resolved reference counts")
        checks["reference_consistency"] = "failed"
        return result()
    checks["reference_consistency"] = "passed"
    return result(unified_patch(changes))
