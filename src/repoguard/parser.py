"""用 CPython AST 提取文件级语法事实，保留后续符号链接所需的位置和作用域。"""

from __future__ import annotations

import ast
import io
import re
import tokenize
from dataclasses import replace

from .model import Binding, File, Scope, Symbol, Unit, Usage, digest, identity
from .repository import module_name

Function = ast.FunctionDef | ast.AsyncFunctionDef
Comprehension = ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp


def decode_python(raw: bytes) -> tuple[str, str]:
    encoding, _ = tokenize.detect_encoding(io.BytesIO(raw).readline)
    return raw.decode(encoding), encoding


def physical_lines(text: str) -> list[str]:
    if not text:
        return []
    lines = re.split(r"\r\n|\r|\n", text)
    return lines[:-1] if text.endswith(("\r", "\n")) else lines


def dotted(node: ast.AST) -> str | None:
    names: list[str] = []
    while isinstance(node, ast.Attribute):
        names.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    return ".".join((node.id, *reversed(names)))


def parse(
    file: File,
    raw: bytes,
    repository_id: str,
    roots: tuple[str, ...],
) -> tuple[File, Unit | None]:
    """解析一个 Git 文件。输入包含原始字节、文件信息、仓库 ID 和源码根，输出带状态的 File 与可选 Unit。

    依次计算内容摘要、检测源编码、解析和编译 AST，再由 Collector 访问。编译产出的字节码不执行。
    失败转为文件诊断。成本主要为源码字节和 AST 节点数，内存包含 AST 与待持久化事实。
    """
    file = replace(file, content_hash=digest(raw))
    if b"\0" in raw:
        return replace(file, status="binary", detail="NUL byte"), None
    try:
        text, encoding = decode_python(raw)
        file = replace(file, encoding=encoding, lines=len(physical_lines(text)))
        tree = ast.parse(text, filename=file.path)
        # The AST parser accepts syntax whose scope declarations fail compilation.
        compile(tree, file.path, "exec", dont_inherit=True)
        collector = Collector(repository_id, file.path, module_name(file.path, roots), text)
        collector.visit(tree)
    except (SyntaxError, UnicodeError, LookupError, ValueError, RecursionError) as exc:
        line = getattr(exc, "lineno", None)
        detail = f"{type(exc).__name__}: {getattr(exc, 'msg', str(exc))}"
        if line:
            detail += f" (line {line})"
        return replace(file, status="parse_error", detail=detail), None
    return replace(file, status="indexed"), collector.unit


class Collector(ast.NodeVisitor):
    """在 AST 遍历中维护当前 Scope，将定义、绑定、引用和导入拆成可序列化的 Unit 事实。"""

    def __init__(self, repo: str, path: str, module: str, text: str) -> None:
        self.repo, self.path, self.module = repo, path, module
        self.lines = [line.encode() for line in physical_lines(text)]
        self.symbols: dict[str, Symbol] = {}
        self.scopes: dict[str, Scope] = {}
        self.usages: list[Usage] = []
        self.counts: dict[tuple[str, str, str], int] = {}
        self.guard = 0
        module_id = identity(repo, path, "module")
        self.scope = Scope(module_id, "module", None, module_id)
        self.scopes[module_id] = self.scope
        self.symbols[module_id] = Symbol(
            module_id,
            repo,
            module,
            module.rsplit(".", 1)[-1],
            module,
            "module",
            module_id,
            path,
            1,
            max(1, len(self.lines)),
            0,
            "",
            None,
            digest(text.encode()),
        )
        self.unit = Unit(path, module, module_id, self.symbols, self.scopes, self.usages)

    def column(self, line: int, offset: int) -> int:
        """把 CPython UTF-8 字节列偏移转换为 Unicode 字符列，供 LibCST 和界面使用。"""
        return len(self.lines[line - 1][:offset].decode())

    def add_symbol(
        self,
        name: str,
        kind: str,
        node: ast.expr | ast.stmt | ast.arg,
        signature: str = "",
        uncertain: bool = False,
    ) -> Symbol:
        """用仓库、文件、作用域、名字、种类与同名序号派生符号 ID。

        行号用于定位而不参与身份，多重同名定义序号变化仍可能改变标识。定义内容摘要覆盖源码行，供变化分类使用。
        """
        key = (self.scope.id, name, kind)
        ordinal = self.counts.get(key, 0)
        self.counts[key] = ordinal + 1
        sid = identity(self.repo, self.path, *key, str(ordinal))
        parent = self.symbols[self.scope.owner]
        start = node.lineno
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = min([start, *(dec.lineno for dec in node.decorator_list)])
        symbol = Symbol(
            sid,
            self.repo,
            self.module,
            name,
            f"{parent.qualified_name}.{name}",
            kind,
            self.scope.id,
            self.path,
            node.lineno,
            node.end_lineno or node.lineno,
            self.column(node.lineno, node.col_offset),
            signature,
            parent.id,
            digest(b"\n".join(self.lines[start - 1 : node.end_lineno])),
            intrinsically_uncertain=uncertain,
        )
        self.symbols[sid] = symbol
        return symbol

    def bind(self, local: str, binding: Binding) -> None:
        self.scope.bindings.setdefault(local, []).append(
            replace(binding, conditional=bool(self.guard) or binding.conditional),
        )

    def bind_symbol(self, symbol: Symbol, available: ast.AST | None = None) -> None:
        """记录绑定位置和赋值或定义结束后的可用位置，供模块或类体中的按行查找。"""
        position = (0, 0)
        if available is not None and (line := getattr(available, "end_lineno", None)):
            position = (line, self.column(line, available.end_col_offset))
        self.bind(
            symbol.name,
            Binding(
                "symbol",
                symbol.line,
                symbol.column,
                target=symbol.id,
                available_line=position[0],
                available_column=position[1],
            ),
        )

    def use(
        self,
        kind: str,
        node: ast.AST,
        text: str,
        *,
        module: str = "",
        name: str = "",
        owner: str | None = None,
    ) -> None:
        """把 AST 引用转换为位置明确的 Usage，不在本阶段决定目标。"""
        line = node.lineno
        offset = node.col_offset
        if isinstance(node, ast.Attribute):
            line = node.end_lineno
            offset = node.end_col_offset - len(node.attr.encode())
        self.usages.append(
            Usage(
                self.scope.id,
                owner or self.scope.owner,
                kind,
                text,
                line,
                self.column(line, offset),
                module,
                name,
            )
        )

    def enter(self, sid: str, kind: str, owner: str) -> tuple[Scope, int]:
        old = self.scope, self.guard
        self.scope = Scope(sid, kind, self.scope.id, owner)
        self.scopes[sid] = self.scope
        self.guard = 0
        return old

    def visit_Global(self, node: ast.Global) -> None:
        self.scope.globals.extend(node.names)

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        self.scope.nonlocals.extend(node.names)

    def arguments(self, args: ast.arguments) -> list[ast.arg]:
        return [
            *args.posonlyargs,
            *args.args,
            *args.kwonlyargs,
            *(arg for arg in (args.vararg, args.kwarg) if arg is not None),
        ]

    def defaults(self, args: ast.arguments) -> None:
        for expr in (*args.defaults, *args.kw_defaults):
            if expr is not None:
                self.visit(expr)
        for arg in self.arguments(args):
            if arg.annotation is not None:
                self.visit(arg.annotation)

    def visit_FunctionDef(self, node: Function) -> None:
        """先在外层采集装饰器、默认值与注解，再建立函数定义并进入参数和函数体作用域。

        识别模块级 pytest 测试及受支持的测试类方法，避免把普通嵌套函数视为可运行用例。
        """
        for expr in node.decorator_list:
            self.visit(expr)
        self.defaults(node.args)
        if node.returns is not None:
            self.visit(node.returns)
        kind = "method" if self.scope.kind == "class" else "function"
        filename = self.path.rsplit("/", 1)[-1]
        if (
            node.name.startswith("test_")
            and (filename.startswith("test_") or filename.endswith("_test.py"))
            and (
                self.scope.kind == "module"
                or (
                    self.scope.kind == "class"
                    and self.scope.parent == self.unit.root_scope
                    and self.symbols[self.scope.owner].name.startswith("Test")
                )
            )
        ):
            kind = "test"
        signature = f"{'async ' if isinstance(node, ast.AsyncFunctionDef) else ''}({ast.unparse(node.args)})"
        if node.returns is not None:
            signature += f" -> {ast.unparse(node.returns)}"
        type_parameters = getattr(node, "type_params", ())
        if type_parameters:
            signature = f"[{', '.join(ast.unparse(p) for p in type_parameters)}]{signature}"
        symbol = self.add_symbol(node.name, kind, node, signature, bool(node.decorator_list))
        self.bind_symbol(symbol, node)
        old = self.enter(symbol.id, "function", symbol.id)
        positional = [*node.args.posonlyargs, *node.args.args]
        decorations = {dotted(d) for d in node.decorator_list}
        for arg in self.arguments(node.args):
            parameter = self.add_symbol(arg.arg, "parameter", arg)
            if (
                old[0].kind == "class"
                and positional
                and arg is positional[0]
                and "staticmethod" not in decorations
            ):
                self.bind(arg.arg, Binding("receiver", 0, target=old[0].owner))
            else:
                self.bind(arg.arg, Binding("symbol", 0, target=parameter.id))
        for stmt in node.body:
            self.visit(stmt)
        self.scope, self.guard = old

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """在外层记录类基类和装饰器，切入类体作用域后记录成员。"""
        for expr in (*node.decorator_list, *node.bases, *node.keywords):
            self.visit(expr)
        signature = ast.unparse(ast.Tuple(elts=[*node.bases], ctx=ast.Load()))
        if node.keywords:
            signature += f" {', '.join(ast.unparse(k) for k in node.keywords)}"
        symbol = self.add_symbol(node.name, "class", node, signature, bool(node.decorator_list))
        self.bind_symbol(symbol, node)
        for base in node.bases:
            expression = base.value if isinstance(base, ast.Subscript) else base
            self.use("INHERITS", expression, dotted(expression) or "", owner=symbol.id)
        old = self.enter(symbol.id, "class", symbol.id)
        for stmt in node.body:
            self.visit(stmt)
        self.scope, self.guard = old

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self.defaults(node.args)
        sid = identity(self.scope.id, "lambda", str(node.lineno), str(node.col_offset))
        old = self.enter(sid, "function", self.scope.owner)
        for arg in self.arguments(node.args):
            self.bind(arg.arg, Binding("unknown", 0))
        self.visit(node.body)
        self.scope, self.guard = old

    def visit_ListComp(self, node: Comprehension) -> None:
        """在外层访问推导式第一个迭代对象，再建立推导式作用域记录后续绑定。"""
        first, *rest = node.generators
        self.visit(first.iter)
        sid = identity(self.scope.id, "comprehension", str(node.lineno), str(node.col_offset))
        old = self.enter(sid, "comprehension", self.scope.owner)
        self.visit(first.target)
        for predicate in first.ifs:
            self.visit(predicate)
        for generator in rest:
            self.visit(generator.iter)
            self.visit(generator.target)
            for predicate in generator.ifs:
                self.visit(predicate)
        # Comprehension targets bind before the result expression, regardless of text order.
        for name, bindings in self.scope.bindings.items():
            self.scope.bindings[name] = [replace(binding, line=0, column=0) for binding in bindings]
        if isinstance(node, ast.DictComp):
            self.visit(node.key)
            self.visit(node.value)
        else:
            self.visit(node.elt)
        self.scope, self.guard = old

    visit_SetComp = visit_DictComp = visit_GeneratorExp = visit_ListComp

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self.use("REFERENCES", node, node.id)
        elif isinstance(node.ctx, ast.Store):
            self.bind_symbol(self.add_symbol(node.id, "variable", node))
        elif isinstance(node.ctx, ast.Del):
            self.bind(
                node.id, Binding("unknown", node.lineno, self.column(node.lineno, node.col_offset))
            )

    def visit_Assign(self, node: ast.Assign) -> None:
        self.visit(node.value)
        for target in node.targets:
            self.assignment(target, node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.visit(node.annotation)
        if node.value is not None:
            self.visit(node.value)
            self.assignment(node.target, node)
        elif isinstance(node.target, ast.Name) and self.scope.kind != "module":
            self.bind(node.target.id, Binding("unknown", node.lineno))

    def assignment(self, target: ast.expr, statement: ast.AST) -> None:
        if isinstance(target, ast.Name):
            self.bind_symbol(self.add_symbol(target.id, "variable", target), statement)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for element in target.elts:
                self.assignment(element, statement)
        elif isinstance(target, ast.Starred):
            self.assignment(target.value, statement)
        else:
            self.visit(target)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        self.visit(node.value)
        scope = self.scope
        while self.scope.kind == "comprehension" and self.scope.parent:
            self.scope = self.scopes[self.scope.parent]
        self.guard += int(scope is not self.scope)
        self.assignment(node.target, node)
        self.guard -= int(scope is not self.scope)
        self.scope = scope

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.ctx, ast.Load):
            self.use("REFERENCES", node, dotted(node) or "")
        elif (name := dotted(node)) and name.split(".", 1)[0] not in {"self", "cls", "mcs"}:
            self.use("DYNAMIC_WRITE", node, name, name=node.attr)
        self.visit(node.value)

    def visit_Call(self, node: ast.Call) -> None:
        """为调用保存点分表达式，反射和无法表示的调用保留动态事实供解析器降级。"""
        expression = dotted(node.func)
        if expression in {
            "getattr",
            "setattr",
            "delattr",
            "eval",
            "exec",
            "__import__",
            "importlib.import_module",
            "super",
        }:
            attribute = node.args[1] if len(node.args) >= 2 else None
            if (
                expression in {"getattr", "setattr", "delattr"}
                and isinstance(attribute, ast.Constant)
                and isinstance(attribute.value, str)
                and attribute.value.isidentifier()
            ):
                self.use("CALLS", node.func, "", name=f"{expression}:{attribute.value}")
                if expression in {"setattr", "delattr"}:
                    self.use("DYNAMIC_WRITE", node.func, "", name=attribute.value)
            else:
                self.use("CALLS", node.func, "", name=expression)
        else:
            self.use("CALLS", node.func, expression or "")
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            local = alias.asname or alias.name.split(".")[0]
            bound = alias.name if alias.asname else local
            self.bind(local, Binding("module", alias.lineno, module=bound))
            self.use("IMPORTS", alias, alias.name, module=alias.name)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """依据当前模块的包路径和相对导入级别记录绝对模块猜测，别名独立保存在绑定表。"""
        package = self.module.split(".")
        if not self.path.endswith("/__init__.py"):
            package.pop()
        if not node.level:
            target = node.module or ""
        elif node.level <= len(package):
            target = ".".join(
                [*package[: len(package) - node.level + 1], *([node.module] if node.module else [])]
            )
        else:
            target = ""
        for alias in node.names:
            self.bind(
                alias.asname or alias.name,
                Binding(
                    "from",
                    alias.lineno,
                    module=target,
                    name=alias.name,
                ),
            )
            self.use(
                "IMPORTS",
                alias,
                f"{'.' * node.level}{node.module or ''}:{alias.name}",
                module=target,
                name=alias.name,
            )

    def guarded(self, node: ast.AST) -> None:
        """在条件、循环和异常等结构内部标记可能执行的绑定，随后恢复外层条件层级。"""
        self.guard += 1
        self.generic_visit(node)
        self.guard -= 1

    visit_If = visit_IfExp = visit_For = visit_AsyncFor = visit_While = guarded
    visit_Try = visit_TryStar = visit_With = visit_AsyncWith = visit_Match = guarded

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.name:
            self.bind(node.name, Binding("unknown", node.lineno, conditional=True))
        self.generic_visit(node)

    def visit_MatchAs(self, node: ast.MatchAs) -> None:
        if node.name:
            self.bind(node.name, Binding("unknown", node.lineno, conditional=True))
        self.generic_visit(node)

    visit_MatchStar = visit_MatchAs

    def visit_MatchMapping(self, node: ast.MatchMapping) -> None:
        if node.rest:
            self.bind(node.rest, Binding("unknown", node.lineno, conditional=True))
        self.generic_visit(node)
