"""从实际 Python AST 生成可验证的目录树和函数导航。"""

from __future__ import annotations

import argparse
import ast
import subprocess
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = {"FUNCTION_REFERENCE.md", "PROJECT_TREE.txt"}
PYTHON_ROOTS = {"src", "tests", "scripts", "benchmarks", "infra"}
Definition = ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef


def git_paths() -> list[str]:
    """列出已跟踪或可提交的路径，排除本地忽略项。首提交之前也可运行。"""
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    paths = {path for path in result.stdout.decode("utf-8").split("\0") if path}
    return sorted({path for path in paths if (ROOT / path).is_file()} | GENERATED)


def source_tree(paths: list[str]) -> str:
    """把按路径排序的候选清单转成文本树。目录字典按前缀共享。"""
    tree: dict = {}
    for path in paths:
        current = tree
        for part in path.split("/"):
            current = current.setdefault(part, {})

    def render(items: dict, prefix: str) -> Iterator[str]:
        entries = sorted(items.items(), key=lambda item: (not bool(item[1]), item[0].lower()))
        for index, (name, nested) in enumerate(entries):
            last = index == len(entries) - 1
            yield prefix + ("└── " if last else "├── ") + name + ("/" if nested else "")
            yield from render(nested, prefix + ("    " if last else "│   "))

    return "\n".join(["RepoGuard/", *render(tree, "")]) + "\n"


def definitions(node: ast.AST, parents: tuple[str, ...] = ()) -> Iterator[tuple[str, Definition]]:
    """按词法定义路径遍历 AST。局部定义用外层函数名限定。"""
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            path = (*parents, child.name)
            yield ".".join(path), child
            yield from definitions(child, path)
        else:
            yield from definitions(child, parents)


class Calls(ast.NodeVisitor):
    """收集函数体直接写出的调用点，跳过嵌套定义的作用域。"""

    def __init__(self) -> None:
        self.sites: list[tuple[str, int]] = []

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, (ast.Name, ast.Attribute)):
            expression = ast.unparse(node.func)
            if len(expression) <= 90:
                self.sites.append((expression, node.lineno))
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """嵌套函数有自己的参考条目。"""

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """由相应的类和方法条目记录内部调用。"""


def escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").replace("`", "'")


def reference(paths: list[str]) -> str:
    """输出定义、签名、行区间与调用点。调用链接仅描述语法位置。"""
    report = [
        "# Python 源码函数索引",
        "",
        "由 `python scripts/generate_source_guide.py` 从 AST 生成。调用列为函数体的前四个直接调用表达式，链接定位调用点。动态方法的运行时目标需要另外验证。",
        "",
    ]
    for file in paths:
        if not file.endswith(".py") or file.split("/")[0] not in PYTHON_ROOTS:
            continue
        tree = ast.parse((ROOT / file).read_text(encoding="utf-8-sig"), filename=file)
        rows = list(definitions(tree))
        if not rows:
            continue
        report.extend(
            [
                f"## [{file}]({file})",
                "",
                "| 定义和源码范围 | 签名 | 职责 | 调用点 |",
                "|---|---|---|---|",
            ]
        )
        for name, node in sorted(rows, key=lambda row: row[1].lineno):
            doc = ast.get_docstring(node)
            first_line = doc.splitlines()[0] if doc else ""
            visitor = Calls()
            if isinstance(node, ast.ClassDef):
                bases = ", ".join(ast.unparse(base) for base in node.bases)
                signature = f"class {node.name}({bases})" if bases else f"class {node.name}"
                first_line = first_line or "类型定义。成员职责见下方对应条目。"
            else:
                signature = f"({ast.unparse(node.args)})"
                if isinstance(node, ast.AsyncFunctionDef):
                    signature = f"async {node.name}{signature}"
                if node.returns is not None:
                    signature += " → " + ast.unparse(node.returns)
                for statement in node.body:
                    visitor.visit(statement)
                if not first_line and node.name.startswith("test_"):
                    first_line = "pytest 回归用例。验证目标见用例名与源文件中的断言。"
            calls = "、".join(
                f"[`{escape(expr)}`]({file}#L{line})"
                for expr, line in list(
                    dict.fromkeys(sorted(visitor.sites, key=lambda site: site[1]))
                )[:4]
            )
            report.append(
                f"| [`{name}`]({file}#L{node.lineno}-L{node.end_lineno}) "
                f"{node.lineno}–{node.end_lineno} | `{escape(signature)}` | "
                f"{escape(first_line) or '—'} | {calls or '—'} |"
            )
        report.append("")
    return "\n".join(report)


def main() -> int:
    """生成两份导航文件或在 CI 检查其内容是否与源码同步。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    options = parser.parse_args()
    paths = git_paths()
    outputs = {"PROJECT_TREE.txt": source_tree(paths), "FUNCTION_REFERENCE.md": reference(paths)}
    stale = []
    for file, content in outputs.items():
        destination = ROOT / file
        if options.check:
            if not destination.exists() or destination.read_text(encoding="utf-8") != content:
                stale.append(file)
        else:
            destination.write_text(content, encoding="utf-8", newline="\n")
    if stale:
        print("Out of date: " + ", ".join(stale))
    else:
        print("Verified source navigation" if options.check else "Generated source navigation")
    return int(bool(stale))


if __name__ == "__main__":
    raise SystemExit(main())
