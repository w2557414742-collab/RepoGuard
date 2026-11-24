from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

from hypothesis import given
from hypothesis import strategies as st

from repoguard.architecture import Rule, compare
from repoguard.graph import CodeGraph
from repoguard.impact import analyze
from repoguard.indexer import IndexOptions
from repoguard.model import Confidence, EdgeType
from repoguard.sdk import RepoGuard
from repoguard.test_selection import CoverageMap, select


def one(view, name):
    matches = view.find_definition(name)
    assert len(matches) == 1
    return matches[0]


def test_reference_resolution_and_graph(history, tmp_path):
    repo, base, _ = history
    view = RepoGuard(repo.root, tmp_path / "db").index(base)
    verify = one(view, "app.core.verify")
    assert len(view.find_definition("verify")) == 3
    assert {(e.path, e.line, e.confidence) for e in view.get_callers(verify.id)} == {
        ("src/app/service.py", 4, Confidence.RESOLVED),
    }
    assert {(e.path, e.line) for e in view.find_references(verify.id)} == {
        ("src/app/__init__.py", 1),
        ("src/app/service.py", 1),
        ("src/app/service.py", 4),
    }
    base_method = one(view, "app.base.Base.run")
    assert any(e.confidence == Confidence.POSSIBLE for e in view.get_callers(base_method.id))
    child = one(view, "app.child.Child.run")
    assert view.graph.shortest_path(child.id, base_method.id, (EdgeType.OVERRIDES,))
    assert any(
        {view.graph.symbols[s].module for s in group} == {"app.cycle_a", "app.cycle_b"}
        for group in view.graph.cycles()
    )
    assert view.get_dependency_graph(verify.id, limit=1, reverse=True)["truncated"]
    assert view.search_symbols("app.core.verify")[0].symbol == verify


def test_incremental_matches_full_and_resolves_former_miss(history, tmp_path):
    repo, base, target = history
    engine = RepoGuard(repo.root, tmp_path / "db")
    initial = engine.index(base).snapshot
    new = engine.index(target, base=base).snapshot
    rebuilt = engine.indexer.index(target, persist=False, mode="full")
    assert new.files == rebuilt.files
    assert new.symbols == rebuilt.symbols
    assert new.edges == rebuilt.edges
    assert new.footprints == rebuilt.footprints
    assert engine.view(target).snapshot.edges == new.edges
    assert engine.view(base).snapshot.edges == initial.edges
    assert set(new.metadata["parsed_files"]) == {
        "src/app/core.py",
        "src/app/descendant.py",
        "src/app/future.py",
    }
    assert "src/app/missing.py" in new.metadata["resolved_files"]
    assert "src/app/unused.py" not in new.metadata["resolved_files"]
    assert {item["status"] for item in new.metadata["git_changes"]} == {"A", "D", "M", "R"}
    assert "src/app/child.py" not in new.units
    later = one(engine.view(target), "app.future.later")
    assert engine.view(target).get_callers(later.id)[0].path == "src/app/missing.py"


def test_impact_evidence_and_hybrid_fallback(history, tmp_path):
    repo, base, target = history
    engine = RepoGuard(repo.root, tmp_path / "db")
    old = engine.index(base).snapshot
    new = engine.index(target, base=base).snapshot
    report = engine.analyze_change_impact(base, target)
    assert any(
        c.kind == "signature" and c.public_api and c.before.qualified_name == "app.core.verify"
        for c in report.changes
    )
    test = next(f for f in report.impacts if f.symbol.name == "test_handle")
    assert test.evidence[-1].path == "tests/test_service.py"
    assert test.evidence[0].target == test.seed
    assert next(
        change for change in report.files if change.new_path == "src/app/core.py"
    ).new_ranges
    assert select(report, new, mode="hybrid").run_all
    assert "tests/test_service.py::test_handle" in select(report, new, mode="static").tests
    coverage = CoverageMap(
        old.commit,
        "container-id",
        True,
        {
            "tests/test_service.py::test_handle[x]": {"src/app/core.py": [2]},
        },
    )
    edges = coverage.evidence_edges(old, "container-id")
    assert len(edges) == 1 and edges[0].kind == EdgeType.COVERS
    assert edges[0].expression.endswith("src/app/core.py:2")
    assert coverage.evidence_edges(old, "different") == []
    assert select(
        report, new, mode="coverage", coverage=coverage, environment="container-id"
    ).tests == ["tests/test_service.py::test_handle[x]"]
    assert select(report, new, mode="coverage", coverage=coverage, environment="different").run_all
    clean = replace(report, fallback_reasons=[])
    assert not select(
        clean, new, mode="hybrid", coverage=coverage, environment="container-id"
    ).run_all
    rules = [
        Rule("new", kind="new_dependency"),
        Rule("cycles", kind="cycles"),
        Rule("no-other", "app.service", "app.other"),
    ]
    diff = compare(old, new, rules)
    assert any(violation.rule == "no-other" for violation in diff["resolved"])
    assert any(violation.rule == "cycles" for violation in diff["existing"])
    assert all(violation.evidence for group in diff.values() for violation in group)


def test_tracked_source_from_commit_and_diagnostics(repository, tmp_path):
    repository.write("good.py", "def valid(): return 1\n")
    repository.write("bad.py", "def broken")
    repository.write("binary.py", b"\x00something")
    repository.write("large.py", "a" * 130)
    repository.write("vendor/thing.py", "raise RuntimeError('never imported')")
    repository.write(".gitignore", "private.py\n")
    repository.write("private.py", "raise RuntimeError('ignored')")
    rev = repository.commit()
    repository.write("good.py", "raise AssertionError('worktree differs')")
    view = RepoGuard(
        repository.root, tmp_path / "db", options=IndexOptions(max_file_bytes=100)
    ).index(rev)
    assert one(view, "good.valid").line == 1
    assert "private.py" not in view.snapshot.files
    assert {f["status"] for f in view.snapshot.metadata["diagnostics"]} == {
        "parse_error",
        "binary",
        "too_large",
        "excluded",
    }


def test_graph_walk_bounds(history, tmp_path):
    repo, base, target = history
    engine = RepoGuard(repo.root, tmp_path / "db")
    old, new = engine.index(base), engine.index(target, base=base)
    graph = CodeGraph(new.snapshot)
    node = one(new, "app.cycle_a").id
    assert len(graph.walk([node], depth=0)) == 1
    assert len(graph.walk([node], depth=10, max_nodes=2)) == 2
    changes = engine.repository.changes(base, target)
    assert (
        "impact traversal reached its node budget"
        in analyze(
            old.snapshot,
            new.snapshot,
            changes,
            max_nodes=1,
        ).fallback_reasons
    )


def test_runtime_binding_changes_invalidate_dependent_confidence(repository, tmp_path):
    repository.write("core.py", "def choose(): return 1\n")
    repository.write("caller.py", "from core import choose\nchoose()\n")
    base = repository.commit()
    engine = RepoGuard(repository.root, tmp_path / "db")
    before = engine.index(base)
    symbol = one(before, "core.choose")
    assert before.get_callers(symbol.id)[0].confidence == Confidence.RESOLVED
    repository.write("patcher.py", "import core\ncore.choose = lambda: 2\n")
    target = repository.commit()
    after = engine.index(target, base=base)
    assert after.get_callers(symbol.id)[0].confidence == Confidence.POSSIBLE
    assert "caller.py" in after.snapshot.metadata["resolved_files"]
    assert after.snapshot.edges == engine.indexer.index(target, mode="full", persist=False).edges


def test_concurrent_publication_keeps_one_complete_snapshot(history, tmp_path):
    repo, base, target = history
    engine = RepoGuard(repo.root, tmp_path / "db")
    engine.index(base)
    with ThreadPoolExecutor(max_workers=2) as pool:
        snapshots = list(pool.map(lambda _: engine.index(target, base=base).snapshot, range(2)))
    first, second = snapshots
    assert first.edges == second.edges == engine.view(target).snapshot.edges
    assert first.metadata == second.metadata


@given(st.lists(st.text(alphabet="abc", min_size=1, max_size=2), min_size=1, max_size=10))
def test_reciprocal_rank_ignores_duplicate_results(order):
    from repoguard.retrieval import reciprocal_rank

    deduped = list(dict.fromkeys(order))
    scored = reciprocal_rank([order])
    assert list(scored) == deduped
    assert sorted(scored, key=scored.get, reverse=True) == deduped


@given(st.floats(min_value=0, max_value=5), st.floats(min_value=0, max_value=1))
def test_possible_edge_never_increases_risk(score, weight):
    from repoguard.impact import risk_step

    assert 0 <= risk_step(score, weight, True) <= risk_step(score, weight, False) <= score
