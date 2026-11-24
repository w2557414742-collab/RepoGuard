from __future__ import annotations

import argparse
import ast
import gzip
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import tracemalloc
from dataclasses import asdict
from pathlib import Path
from statistics import median
from time import perf_counter

from repoguard.impact import analyze, markdown
from repoguard.model import Confidence, EdgeType
from repoguard.refactoring import plan
from repoguard.repository import Repository
from repoguard.sandbox import TestRun, run_tests
from repoguard.sdk import RepoGuard, View
from repoguard.test_selection import select

MANIFEST = Path(__file__).parent / "ground_truth/click-8.1.8.json"
IMPORTS = {EdgeType.IMPORTS, EdgeType.DEPENDS_ON}
CALLS = {EdgeType.CALLS}


def score(found: set, expected: set) -> dict:
    hits = len(found & expected)
    precision = hits / len(found) if found else None
    recall = hits / len(expected) if expected else None
    return {
        "precision": precision,
        "recall": recall,
        "f1": 2 * precision * recall / (precision + recall) if precision and recall else 0.0,
        "false_negatives": sorted(expected - found),
        "false_positives": sorted(found - expected),
    }


def dump(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def snapshot_sources(repo: Repository, snap) -> dict[str, str]:
    files = [snap.files[path] for path in snap.units]
    return {
        item.path: blob.decode(item.encoding)
        for item, blob in zip(files, repo.blobs(files), strict=True)
    }


def navigation(view: View, sources: dict[str, str], manifest: dict) -> dict:
    data = {}
    trees = {path: ast.parse(text) for path, text in sources.items()}
    for case in manifest["navigation"]:
        query = case["query"]
        expected = {tuple(case["definition"])}
        leaf = query.rsplit(".", 1)[-1]
        exact_time = perf_counter()
        matches = view.find_definition(query)
        exact_time = perf_counter() - exact_time
        start = perf_counter()
        grep_defs = {
            (path, i)
            for path, text in sources.items()
            for i, line in enumerate(text.splitlines(), 1)
            if re.match(rf"\s*(?:async\s+)?(?:def|class)\s+{re.escape(leaf)}\b", line)
        }
        grep_seconds = perf_counter() - start
        start = perf_counter()
        ast_defs = {
            (path, node.lineno)
            for path, tree in trees.items()
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and node.name == leaf
        }
        ast_seconds = perf_counter() - start
        record = {
            "definition": {
                "grep": {**score(grep_defs, expected), "seconds": grep_seconds},
                "ast_name": {**score(ast_defs, expected), "seconds": ast_seconds},
                "scoped": {
                    **score({(s.path, s.line) for s in matches}, expected),
                    "seconds": exact_time,
                },
            },
        }
        if case["references"] is not None:
            truth = {tuple(item) for item in case["references"]}
            start = perf_counter()
            text_matches = {
                (path, i)
                for path, text in sources.items()
                for i, line in enumerate(text.splitlines(), 1)
                if re.search(rf"\b{re.escape(leaf)}\b", line) and (path, i) not in expected
            }
            elapsed = perf_counter() - start
            start = perf_counter()
            ast_matches = {
                (path, n.lineno)
                for path, tree in trees.items()
                for n in ast.walk(tree)
                if (isinstance(n, ast.Name) and n.id == leaf and isinstance(n.ctx, ast.Load))
                or (isinstance(n, ast.Attribute) and n.attr == leaf and isinstance(n.ctx, ast.Load))
                or (isinstance(n, ast.alias) and n.name == leaf)
            }
            ast_elapsed = perf_counter() - start
            start = perf_counter()
            edges = view.find_references(matches[0].id)
            reference_seconds = perf_counter() - start
            record["references"] = {
                "grep": {**score(text_matches, truth), "seconds": elapsed},
                "ast_name": {**score(ast_matches, truth), "seconds": ast_elapsed},
                "scoped": {
                    **score(
                        {(e.path, e.line) for e in edges if e.confidence == Confidence.RESOLVED},
                        truth,
                    ),
                    "seconds": reference_seconds,
                },
            }
        data[query] = record
    all_calls = [
        e for part in view.snapshot.edges.values() for e in part if e.kind == EdgeType.CALLS
    ]
    return {
        "queries": data,
        "call_unresolved_rate": sum(e.target is None for e in all_calls) / len(all_calls),
        "call_edge_count": len(all_calls),
    }


def measure_index(engine: RepoGuard, base: str, target: str, repeats: int) -> dict:
    result = {}
    reference = engine.indexer.index(target, mode="full", persist=False)
    for mode in ("full", "file", "dependency"):
        timings = []
        for _ in range(repeats):
            start = perf_counter()
            sample = engine.indexer.index(target, base=base, mode=mode, persist=False)
            timings.append(perf_counter() - start)
        start = perf_counter()
        query = View(sample).find_definition("click.formatting.measure_table")
        cold_query = perf_counter() - start
        tracemalloc.start()
        measured = engine.indexer.index(target, base=base, mode=mode, persist=False)
        peak_bytes = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        assert measured.edges == sample.edges
        expected = View(reference).find_definition("click.formatting.measure_table")
        matches = {
            "files": sample.files == reference.files,
            "symbols": sample.symbols == reference.symbols,
            "edges": sample.edges == reference.edges,
            "footprints": sample.footprints == reference.footprints,
            "query": query == expected,
            "version": sample.version == reference.version,
        }
        if not all(matches.values()):
            raise AssertionError(f"{mode} index differs from full rebuild")
        result[mode] = {
            "seconds": timings,
            "median_seconds": median(timings),
            "peak_traced_bytes": peak_bytes,
            "parsed_files": len(sample.metadata["parsed_files"]),
            "resolved_files": len(sample.metadata["resolved_files"]),
            "cold_definition_seconds": cold_query,
            "consistency": matches,
        }
    return result


def git(root: Path, *args: str, data: bytes | None = None) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        input=data,
        capture_output=True,
        timeout=90,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", "replace"))
    return result.stdout.decode().strip()


def commit_variant(root: Path, base: str) -> str:
    git(root, "add", "--", ".")
    tree = git(root, "write-tree")
    env = {
        **os.environ,
        "GIT_AUTHOR_DATE": "2025-01-01T00:00:00Z",
        "GIT_COMMITTER_DATE": "2025-01-01T00:00:00Z",
    }
    return subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=RepoGuard benchmark",
            "-c",
            "user.email=benchmark@example.invalid",
            "commit-tree",
            tree,
            "-p",
            base,
            "-m",
            "Controlled RepoGuard benchmark change",
        ],
        env=env,
        capture_output=True,
        timeout=90,
        check=True,
        text=True,
    ).stdout.strip()


def variant(root: Path, base: str, edits: dict[str, str], patch: bytes | None = None) -> str:
    git(root, "checkout", "--detach", base)
    for path, value in edits.items():
        (root / path).write_bytes(value.encode())
    if patch:
        git(root, "apply", "--check", "-", data=patch)
        git(root, "apply", "-", data=patch)
    revision = commit_variant(root, base)
    git(root, "checkout", "--detach", revision)
    return revision


def brief(run: TestRun) -> dict:
    record = asdict(run)
    if run.coverage is not None:
        record["coverage"] = {
            "mapped_tests": len(run.coverage.tests),
            "tests_with_lines": sum(bool(record) for record in run.coverage.tests.values()),
            "limitations": run.coverage.limitations,
        }
    return record


def evaluate_tests(engine, old, new, inputs, image: str, baseline: TestRun, full: TestRun) -> dict:
    result = {}
    for mode in ("file", "static", "coverage", "hybrid"):
        selection = select(
            inputs, new, mode=mode, coverage=baseline.coverage, environment=baseline.environment
        )
        result[mode] = asdict(selection)
        if selection.run_all:
            run = run_tests(engine.repository, new.commit, image=image)
        elif selection.tests:
            run = run_tests(engine.repository, new.commit, image=image, nodeids=selection.tests)
        else:
            run = None
        collected = set(run.collected) if run else set()
        failures = set(full.failures)
        observed = set(run.failures) if run else set()
        result[mode]["run"] = brief(run) if run else {"status": "no_tests_selected", "seconds": 0}
        result[mode]["metrics"] = {
            "failing_test_recall": len(observed & failures) / len(failures) if failures else None,
            "selection_ratio": len(collected) / len(full.collected) if full.collected else None,
            "missed_failures": sorted(failures - observed),
            "speedup": full.seconds / run.seconds if run and run.seconds else None,
            "fallback": selection.run_all,
        }
    return result


def evaluate_impact(old, new, files, truth: set[str]) -> dict:
    results = {}
    modified = [change.new_path for change in files if change.new_path]
    for mode, kinds in (
        ("modified", set()),
        ("import", IMPORTS),
        ("call", CALLS),
        ("hybrid", None),
    ):
        report = analyze(old, new, files, **({"kinds": kinds} if kinds is not None else {}))
        ordered = list(
            dict.fromkeys(modified + [finding.symbol.path for finding in report.impacts])
        )
        results[mode] = {
            **score(set(ordered), truth),
            "ranked_paths": ordered,
            "recall_at_10": len(set(ordered[:10]) & truth) / len(truth),
        }
    return results


def evaluate_rename(root, engine, snap, sources, manifest, output, image):
    import libcst as cst

    query = manifest["query"]
    previous = query.rsplit(".", 1)[-1]
    target = View(snap).find_definition(query)[0]
    name = manifest["new_name"]
    expected = {tuple(location) for location in manifest["edited_lines"]}

    class BlindRename(cst.CSTTransformer):
        def leave_Name(self, original_node, updated_node):
            return (
                updated_node.with_changes(value=name)
                if original_node.value == previous
                else updated_node
            )

    records = {}
    for mode in ("text", "libcst", "verified"):
        start = perf_counter()
        patch = None
        if mode == "verified":
            outcome = plan(engine.repository, snap, target.id, name)
            records[mode] = {"checks": outcome.checks, "blockers": outcome.blockers}
            if not outcome.patch:
                continue
            patch = outcome.patch.encode()
            (output / "click-iter-rows.patch").write_bytes(patch)
            edits = {}
        elif mode == "text":
            edits = {
                path: text.replace(previous, name)
                for path, text in sources.items()
                if previous in text
            }
        else:
            edits = {
                path: cst.parse_module(text).visit(BlindRename()).code
                for path, text in sources.items()
                if re.search(rf"\b{re.escape(previous)}\b", text)
            }
        revision = variant(root, snap.commit, edits, patch)
        differences = engine.repository.changes(snap.commit, revision, with_lines=True)
        changed = {
            (f.old_path, line)
            for f in differences
            for begin, end in f.old_ranges
            for line in range(begin, end + 1)
        }
        validation = run_tests(engine.repository, revision, image=image)
        records.setdefault(mode, {}).update(
            {
                **score(changed, expected),
                "commit": revision,
                "success": changed == expected and validation.status == "passed",
                "validation_seconds": validation.seconds,
                "total_seconds": perf_counter() - start,
                "run": brief(validation),
            }
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", type=Path)
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    parser.add_argument("--work", type=Path, default=Path(".benchmark"))
    parser.add_argument("--image", default="repoguard-runner:0.1")
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    args.work.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    base, target = manifest["base"], manifest["target"]
    root = args.work.resolve() / "click-benchmark-work"
    root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=root) as temp:
        checkout = Path(temp) / "checkout"
        git(
            args.repository.resolve(),
            "clone",
            "--no-hardlinks",
            "--no-checkout",
            str(args.repository.resolve()),
            str(checkout),
        )
        database = Path(temp) / "index.sqlite"
        engine = RepoGuard(checkout, database)
        engine.index(base)
        new = engine.index(target, base=base).snapshot
        sources = snapshot_sources(engine.repository, new)
        metrics = {
            "repository": manifest["repository"],
            "base": base,
            "target": target,
            "environment": {
                "python": sys.version,
                "platform": platform.platform(),
                "processor": platform.processor(),
                "logical_cpus": os.cpu_count(),
                "parser_threads": engine.indexer.workers,
            },
            "snapshot": new.metadata,
            "A_navigation": navigation(View(new), sources, manifest),
            "B_release_incremental": measure_index(engine, base, target, args.repeats),
        }
        dump(args.output / "click-static.json", metrics)
        release = engine.analyze_change_impact(base, target)
        (args.output / "click-release-impact.md").write_text(markdown(release), encoding="utf-8")
        baseline = run_tests(engine.repository, target, image=args.image, collect_coverage=True)
        if baseline.status != "passed":
            dump(args.output / "click-dynamic.json", {"baseline": brief(baseline)})
            raise RuntimeError(f"baseline {baseline.status}: {baseline.output}")
        mutation = manifest["mutation"]
        source = sources[mutation["path"]]
        if source.count(mutation["line"]) != 1:
            raise ValueError("mutation anchor must match a single line on the pinned snapshot")
        mutant = variant(
            checkout,
            target,
            {
                mutation["path"]: source.replace(mutation["line"], mutation["regression"]),
            },
        )
        bad = engine.index(mutant, base=target).snapshot
        full = run_tests(engine.repository, mutant, image=args.image)
        if full.status != "failed" or not full.failures:
            dump(
                args.output / "click-dynamic.json",
                {"baseline": brief(baseline), "mutant": brief(full)},
            )
            raise RuntimeError(f"fault did not produce an independent failure set: {full.output}")
        report = engine.analyze_change_impact(target, mutant)
        test_metrics = evaluate_tests(engine, new, bad, report, args.image, baseline, full)
        comparison = set(manifest["manual_impact"]) | {
            node.split("::", 1)[0] for node in full.failures
        }
        control_commit = variant(
            checkout,
            target,
            {
                mutation["path"]: source.replace(mutation["line"], mutation["control"]),
            },
        )
        control = run_tests(engine.repository, control_commit, image=args.image)
        dynamic = {
            "baseline": brief(baseline),
            "independent_full_mutant": brief(full),
            "B_controlled_incremental": measure_index(engine, target, mutant, args.repeats),
            "C_impact": evaluate_impact(new, bad, report.files, comparison),
            "D_test_selection": test_metrics,
            "E_refactoring": evaluate_rename(
                checkout, engine, new, sources, manifest["rename"], args.output, args.image
            ),
            "mutation": {
                "attempts": 2,
                "killed": int(full.status == "failed"),
                "survived": int(control.status == "passed"),
                "control": brief(control),
            },
        }
        dump(args.output / "click-dynamic.json", dynamic)
        if baseline.coverage:
            raw = json.dumps(asdict(baseline.coverage), ensure_ascii=True).encode()
            (args.output / "click-baseline-coverage.json.gz").write_bytes(
                gzip.compress(raw, mtime=0)
            )
        (args.output / "click-mutant-impact.md").write_text(markdown(report), encoding="utf-8")
    print("Wrote Click benchmark artifacts")


if __name__ == "__main__":
    main()
