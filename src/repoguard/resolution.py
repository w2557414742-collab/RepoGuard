"""把语法事实解析为有证据的仓库关系，并记录依赖探测以驱动增量失效。"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import PurePosixPath

from .model import Binding, Confidence, Edge, EdgeType, Scope, Symbol, Unit, Usage, identity


@dataclass(frozen=True, slots=True)
class Candidate:
    """解析中的候选目标及不确定性标记，可能表示符号、模块或命名空间。"""

    kind: str
    key: str
    uncertain: bool = False


def mutations(units: Iterable[Unit]) -> set[str]:
    return {use.name for unit in units for use in unit.usages if use.kind == "DYNAMIC_WRITE"}


def mutation_key(name: str) -> str:
    return f"!member:{name}"


class Catalog:
    """按模块、符号 ID、基类和动态写入组织全部文件事实，为 Resolver 提供查找目录。"""

    def __init__(self, units: dict[str, Unit]) -> None:
        self.modules: dict[str, list[Unit]] = defaultdict(list)
        self.namespaces: set[str] = set()
        self.owners: dict[str, Unit] = {}
        self.bases: dict[str, list[Usage]] = defaultdict(list)
        self.runtime_writes: dict[str, set[str]] = {}
        self.nonlocal_writes: dict[str, set[str]] = {}
        self.mutated_members = mutations(units.values())
        for unit in units.values():
            self.modules[unit.module].append(unit)
            parts = unit.module.split(".")
            self.namespaces.update(".".join(parts[:i]) for i in range(1, len(parts)))
            self.owners.update(dict.fromkeys(unit.symbols, unit))
            self.runtime_writes[unit.path] = {
                name
                for s in unit.scopes.values()
                if s.kind != "module"
                for name in s.globals
                if name in s.bindings
            }
            self.nonlocal_writes[unit.path] = {
                name for s in unit.scopes.values() for name in s.nonlocals if name in s.bindings
            }
            for use in unit.usages:
                if use.kind == "INHERITS":
                    self.bases[use.owner].append(use)

    def symbol(self, sid: str) -> Symbol:
        return self.owners[sid].symbols[sid]


class Resolver:
    """解析单个文件的词法与模块关系，同时收集命中和未命中探测。"""

    def __init__(self, catalog: Catalog) -> None:
        self.catalog = catalog
        self.footprint: set[str] = set()
        self._export_depth = 0

    def modules(self, name: str) -> list[Candidate]:
        """按模块名查目录，已存在、命名空间和未命中均登记探测。同名模块保留多个候选。"""
        if not name:
            return []
        self.footprint.add(name)
        units = self.catalog.modules.get(name, ())
        if units:
            return [Candidate("module", u.root_scope, len(units) > 1) for u in units]
        if name in self.catalog.namespaces:
            return [Candidate("namespace", name)]
        return []

    def imported(self, module: str, name: str, seen: frozenset[tuple[str, str]]) -> list[Candidate]:
        """查找模块导出、别名和子模块，递归追踪重导出。递归链用 seen 和深度上限截断。

        时间和空间与已追踪的候选及递归栈有关；外部模块、星号导入或循环路径可以返回空候选。
        """
        if not module or name == "*" or (module, name) in seen or self._export_depth >= 60:
            return []
        parents = self.modules(module)
        exports: list[Candidate] = []
        for parent in parents:
            if parent.kind == "namespace":
                continue
            unit = self.catalog.owners[parent.key]
            scope = unit.scopes[unit.root_scope]
            self._export_depth += 1
            try:
                values = self.bindings(
                    scope.bindings.get(name, ()),
                    unit,
                    scope,
                    name,
                    seen | {(module, name)},
                )
            finally:
                self._export_depth -= 1
            exports.extend(self.mark(values, parent.uncertain))
        self.footprint.add(mutation_key(name))
        if exports and not any(c.uncertain for c in exports):
            return self.mark(exports, name in self.catalog.mutated_members)
        members = self.modules(f"{module}.{name}")
        return self.mark(exports + members, bool(exports) or name in self.catalog.mutated_members)

    @staticmethod
    def mark(values: list[Candidate], uncertain: bool) -> list[Candidate]:
        if not uncertain:
            return values
        return [Candidate(c.kind, c.key, True) for c in values]

    def bindings(
        self,
        options: list[Binding] | tuple[()],
        unit: Unit,
        scope: Scope,
        name: str,
        seen: frozenset[tuple[str, str]] = frozenset(),
    ) -> list[Candidate]:
        """把同名绑定解释为若干候选；分支、多个赋值或运行时写入使候选降级。"""
        values: list[Candidate] = []
        # Preserve competing definitions without approximating branch joins as exact.
        uncertain = len(options) > 1 or any(o.conditional for o in options)
        uncertain |= "*" in scope.bindings
        if scope.kind == "module":
            uncertain |= name in self.catalog.runtime_writes[unit.path]
        else:
            uncertain |= name in self.catalog.nonlocal_writes[unit.path]
        for option in options:
            if option.kind == "module":
                values.extend(self.modules(option.module))
            elif option.kind == "from":
                values.extend(self.imported(option.module, option.name, seen))
            elif option.kind == "receiver":
                values.append(Candidate("receiver", option.target, True))
            elif option.kind == "symbol":
                symbol = unit.symbols[option.target]
                values.append(Candidate("symbol", option.target, symbol.intrinsically_uncertain))
        return self.mark(values, uncertain)

    def lookup(self, unit: Unit, use: Usage, name: str) -> list[Candidate]:
        """由引用位置往外查词法作用域。优先处理 global、nonlocal 与绑定生效位置，再查绑定候选。

        在类体和函数闭包之间按既有 Python 规则跳过部分 class 作用域。成本随作用域深度和同名绑定数增长。
        """
        scope = unit.scopes[use.scope]
        own, deferred = True, False
        while True:
            if name in scope.globals and scope.kind != "module":
                if name in scope.bindings:
                    return []
                deferred |= scope.kind == "function"
                scope = unit.scopes[unit.root_scope]
                own = False
            options = scope.bindings.get(name)
            if name in scope.nonlocals and options:
                return []
            if options:
                if own or not deferred:
                    options = [
                        binding
                        for binding in options
                        if (
                            binding.available_line or binding.line,
                            binding.available_column or binding.column,
                        )
                        <= (use.line, use.column)
                    ]
                if options or scope.kind not in {"module", "class"}:
                    return self.bindings(options, unit, scope, name)
            if "*" in scope.bindings or scope.parent is None:
                return []
            parent = unit.scopes[scope.parent]
            deferred |= scope.kind == "function"
            while parent.kind == "class" and parent.parent:
                parent = unit.scopes[parent.parent]
            scope, own = parent, False

    def member(
        self,
        value: Candidate,
        name: str,
        visited: frozenset[str] = frozenset(),
    ) -> list[Candidate]:
        """解析模块、类和方法接收者的成员，递归查询基类并限制访问次数。

        动态接收者、多基类及运行期赋值会降低可信度。完整 MRO 和类型窄化未实现。
        """
        self.footprint.add(mutation_key(name))
        mutated = name in self.catalog.mutated_members
        if value.kind == "namespace":
            return self.mark(self.modules(f"{value.key}.{name}"), mutated)
        if value.kind == "module":
            unit = self.catalog.owners[value.key]
            return self.mark(self.imported(unit.module, name, frozenset()), value.uncertain)
        symbol = self.catalog.symbol(value.key)
        if symbol.kind != "class" or symbol.id in visited or len(visited) >= 60:
            return []
        unit = self.catalog.owners[symbol.id]
        self.footprint.add(unit.module)
        scope = unit.scopes[symbol.id]
        direct = self.bindings(scope.bindings.get(name, ()), unit, scope, name)
        if direct and not any(c.uncertain for c in direct):
            return self.mark(direct, value.uncertain or mutated)
        bases = self.catalog.bases[symbol.id]
        inherited: list[Candidate] = []
        uncertain = len(bases) > 1 or bool(direct) or value.uncertain or mutated
        for use in bases:
            parents = self.expression(unit, use, visited | {symbol.id})
            inherited.extend(
                member
                for parent in parents
                for member in self.member(parent, name, visited | {symbol.id})
            )
        return self.mark(direct + inherited, uncertain)

    def expression(
        self,
        unit: Unit,
        use: Usage,
        visited: frozenset[str] = frozenset(),
    ) -> list[Candidate]:
        """分解限定名，先查根绑定，再逐段解析成员。高分支的候选会放大查找量。"""
        if not use.text:
            return []
        name, *members = use.text.split(".")
        values = self.lookup(unit, use, name)
        for member in members:
            values = [found for value in values for found in self.member(value, member, visited)]
        return values

    def edge_for(self, unit: Unit, use: Usage, values: list[Candidate]) -> list[Edge]:
        """按用途将候选转成边。无候选时输出没有目标的 UNRESOLVED 边，保留调用点。"""
        kind = EdgeType(use.kind)
        if kind == EdgeType.INHERITS:
            values = [
                v
                for v in values
                if v.kind == "symbol" and self.catalog.symbol(v.key).kind == "class"
            ]
        if kind == EdgeType.CALLS:
            values = [
                v
                for v in values
                if v.kind == "symbol"
                and self.catalog.symbol(v.key).kind in {"function", "test", "class", "method"}
            ]
        candidates: dict[str, bool] = {}
        for candidate in values:
            if candidate.kind == "namespace":
                continue
            candidates[candidate.key] = candidates.get(candidate.key, False) or candidate.uncertain
        method = {
            EdgeType.IMPORTS: "import-binding",
            EdgeType.INHERITS: "class-base",
            EdgeType.OVERRIDES: "inherited-member",
        }.get(kind, "lexical-scope")
        expression = use.text or use.name or "<computed>"
        if not candidates:
            return [
                Edge(
                    use.owner,
                    None,
                    kind,
                    unit.path,
                    use.line,
                    use.column,
                    Confidence.UNRESOLVED,
                    method,
                    expression,
                )
            ]
        return [
            Edge(
                use.owner,
                sid,
                kind,
                unit.path,
                use.line,
                use.column,
                Confidence.POSSIBLE if uncertain or len(candidates) > 1 else Confidence.RESOLVED,
                method,
                expression,
            )
            for sid, uncertain in sorted(candidates.items())
        ]

    def resolve(self, unit: Unit) -> tuple[list[Edge], set[str]]:
        """把文件 Unit 转成关系边和依赖探测集合。输出定义、引用、导入、调用及类关系。

        结果供 Indexer 持久化；依赖查询失败仍进入探测集合，因此添加此前缺失的模块也能失效旧结果。
        """
        edges: list[Edge] = []
        module_id = unit.root_scope
        file_id = identity(unit.symbols[module_id].repository_id, unit.path, "file")
        edges.append(
            Edge(
                file_id,
                module_id,
                EdgeType.CONTAINS,
                unit.path,
                1,
                0,
                Confidence.RESOLVED,
                "git-inventory",
            )
        )
        for symbol in unit.symbols.values():
            if symbol.parent:
                edges.append(
                    Edge(
                        symbol.parent,
                        symbol.id,
                        EdgeType.DEFINES,
                        unit.path,
                        symbol.line,
                        symbol.column,
                        Confidence.RESOLVED,
                        "ast-definition",
                    )
                )
            if symbol.kind in {"method", "test"} and symbol.parent in self.catalog.bases:
                for base in self.catalog.bases[symbol.parent]:
                    parents = self.expression(unit, base)
                    members = [
                        m
                        for parent in parents
                        if parent.kind == "symbol"
                        for m in self.member(parent, symbol.name)
                    ]
                    if members:
                        use = Usage(
                            symbol.scope_id,
                            symbol.id,
                            "OVERRIDES",
                            symbol.name,
                            symbol.line,
                            symbol.column,
                        )
                        edges.extend(self.edge_for(unit, use, members))
        for use in unit.usages:
            if use.kind == "DYNAMIC_WRITE":
                continue
            if use.kind == "IMPORTS":
                modules = self.modules(use.module)
                namespaces = {v.key for v in modules if v.kind == "namespace"}
                if use.name:
                    values = self.imported(use.module, use.name, frozenset())
                else:
                    values = modules
                edges.extend(self.edge_for(unit, use, values))
                targets = [v for v in modules + values if v.kind == "module"]
                for target in targets:
                    if target.key != module_id:
                        edges.append(
                            Edge(
                                module_id,
                                target.key,
                                EdgeType.DEPENDS_ON,
                                unit.path,
                                use.line,
                                use.column,
                                Confidence.POSSIBLE if target.uncertain else Confidence.RESOLVED,
                                "module-import",
                                use.module,
                            )
                        )
                if namespaces:
                    self.footprint.update(namespaces)
            else:
                values = self.expression(unit, use)
                edges.extend(self.edge_for(unit, use, values))
        return list(dict.fromkeys(edges)), self.footprint


def module_prefixes(module: str) -> set[str]:
    parts = module.split(".")
    return {".".join(parts[:length]) for length in range(1, len(parts) + 1)}


def test_nodeid(symbol: Symbol) -> str:
    package = symbol.qualified_name.removeprefix(symbol.module + ".")
    return str(PurePosixPath(symbol.path)) + "::" + package.replace(".", "::")
