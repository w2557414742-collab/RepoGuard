"""解析本地命令、驱动 SDK 和隔离测试，并格式化 JSON 或 Markdown 输出。"""

from __future__ import annotations

import argparse
import gzip
import json
import subprocess
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from .impact import markdown
from .indexer import IndexOptions
from .repository import RepositoryError
from .sdk import RepoGuard
from .test_selection import CoverageMap


def load_coverage(path: Path) -> CoverageMap:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        text = stream.read(16 * 1024 * 1024 + 1)
    if len(text) > 16 * 1024 * 1024:
        raise ValueError("coverage input exceeds 16 MiB")
    return CoverageMap(**json.loads(text))


def output(value: Any) -> None:
    print(json.dumps(value, indent=2, default=encode))


def encode(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    raise TypeError(f"cannot encode {type(value).__name__}")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="repoguard")
    root.add_argument("--repo", default=".", type=Path)
    root.add_argument("--db", default=Path(".repoguard/index.sqlite"), type=Path)
    root.add_argument("--root", action="append", dest="roots")
    root.add_argument("--workers", default=4, type=int)
    sub = root.add_subparsers(dest="command", required=True)
    indexing = sub.add_parser("index", help="build or load a commit index")
    indexing.add_argument("--target", default="HEAD")
    indexing.add_argument("--base")
    for name in ("search", "definition", "references", "callers", "callees", "graph", "plan"):
        operation = sub.add_parser(name)
        operation.add_argument("query")
        operation.add_argument("--target", default="HEAD")
        if name == "search":
            operation.add_argument("--limit", type=int, default=20)
        if name == "graph":
            operation.add_argument("--depth", type=int, default=2)
            operation.add_argument("--reverse", action="store_true")
        if name == "plan":
            operation.add_argument("new_name")
            operation.add_argument("--operation", choices=("rename", "signature"), default="rename")
            operation.add_argument("--value")
            operation.add_argument("--patch-only", action="store_true")
    for name in ("impact", "select-tests", "architecture"):
        operation = sub.add_parser(name)
        operation.add_argument("base")
        operation.add_argument("target")
        if name == "impact":
            operation.add_argument("--depth", type=int, default=5)
            operation.add_argument("--format", choices=("json", "markdown"), default="json")
        if name == "select-tests":
            operation.add_argument(
                "--mode", choices=("file", "static", "coverage", "hybrid"), default="hybrid"
            )
            operation.add_argument("--coverage", type=Path)
            operation.add_argument("--environment", default="")
        if name == "architecture":
            operation.add_argument("rules", type=Path)
    runner = sub.add_parser("run-tests", help="run an explicit isolated pytest session")
    runner.add_argument("--target", default="HEAD")
    runner.add_argument("--image", required=True)
    runner.add_argument("--timeout", type=int, default=120)
    runner.add_argument("--coverage", action="store_true")
    runner.add_argument("nodeids", nargs="*")
    move = sub.add_parser("move-module", help="preview a module move and import rewrite")
    move.add_argument("source_module")
    move.add_argument("destination_module")
    move.add_argument("--target", default="HEAD")
    validation = sub.add_parser("validate-patch")
    validation.add_argument("patch", type=Path)
    validation.add_argument("--target", default="HEAD")
    return root


def require_id(view, query: str) -> str:
    matches = view.find_definition(query)
    if len(matches) != 1:
        raise ValueError(
            f"{query!r} matched {len(matches)} symbols. Use a qualified name or symbol ID."
        )
    return matches[0].id


def dispatch(engine: RepoGuard, args: argparse.Namespace) -> int:
    """把解析后的命令交给一个 RepoGuard 实例。需要 Git 差异、补丁或测试时委派给相应适配器。"""
    command = args.command
    if command == "index":
        output(engine.index(args.target, base=args.base).snapshot.metadata)
        return 0
    if command == "impact":
        report = engine.analyze_change_impact(args.base, args.target, depth=args.depth)
        if args.format == "markdown":
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
            print(markdown(report), end="")
        else:
            output(report)
        return 0
    if command == "select-tests":
        coverage = load_coverage(args.coverage) if args.coverage else None
        output(
            engine.select_related_tests(
                args.base,
                args.target,
                mode=args.mode,
                coverage=coverage,
                environment=args.environment,
            )
        )
        return 0
    if command == "architecture":
        from .architecture import compare, load_rules

        diff = compare(
            engine.view(args.base).snapshot,
            engine.view(args.target).snapshot,
            load_rules(args.rules),
        )
        output(diff)
        return 1 if diff["introduced"] else 0
    if command == "run-tests":
        from .sandbox import run_tests

        result = run_tests(
            engine.repository,
            args.target,
            image=args.image,
            nodeids=args.nodeids,
            timeout=args.timeout,
            collect_coverage=args.coverage,
        )
        output(result)
        return 0 if result.status == "passed" else 1
    if command == "move-module":
        plan = engine.plan_import_migration(
            args.target, args.source_module, args.destination_module
        )
        output(plan)
        return 1 if plan.blockers else 0
    if command == "validate-patch":
        if args.patch.stat().st_size > 2 * 1024 * 1024:
            raise ValueError("patch exceeds 2 MiB")
        result = engine.validate_patch(args.target, args.patch.read_bytes().decode("utf-8"))
        output(result)
        return 1 if result.diagnostics else 0
    view = engine.view(args.target)
    if command == "search":
        output(view.search_symbols(args.query, args.limit))
    elif command == "definition":
        output(view.find_definition(args.query))
    else:
        sid = require_id(view, args.query)
        if command == "plan":
            plan = engine.plan_refactoring(
                args.target, sid, args.new_name, operation=args.operation, value=args.value
            )
            if args.patch_only and plan.patch:
                sys.stdout.buffer.write(plan.patch.encode("utf-8"))
            else:
                output(plan)
            return 1 if plan.blockers else 0
        if command == "graph":
            output(view.get_dependency_graph(sid, depth=args.depth, reverse=args.reverse))
        else:
            output(
                {
                    "references": view.find_references,
                    "callers": view.get_callers,
                    "callees": view.get_callees,
                }[command](sid)
            )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        options = IndexOptions(tuple(args.roots)) if args.roots else IndexOptions()
        engine = RepoGuard(args.repo, args.db, options=options, workers=args.workers)
        return dispatch(engine, args)
    except (RepositoryError, OSError, ValueError, TypeError, subprocess.TimeoutExpired) as exc:
        print(f"repoguard: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
