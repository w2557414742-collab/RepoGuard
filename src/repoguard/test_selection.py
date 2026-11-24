"""结合 Git 变更、静态影响与 Coverage.py 证据选择 pytest 用例。"""

from __future__ import annotations

from dataclasses import dataclass, field

from .impact import ImpactReport
from .model import Confidence, Edge, EdgeType, Snapshot, Symbol
from .resolution import test_nodeid


@dataclass(frozen=True, slots=True)
class CoverageMap:
    """按提交、运行环境和 pytest nodeid 保存覆盖路径与执行行，并记录归因局限。"""

    commit: str
    environment: str
    complete: bool
    tests: dict[str, dict[str, list[int]]]
    limitations: list[str] = field(default_factory=list)

    def evidence_edges(self, base: Snapshot, environment: str) -> list[Edge]:
        """确认基线提交和环境标识后，将覆盖行映射到窄的符号范围并生成 COVERS 边。

        映射缓存以路径分组，行范围展开的成本取决于符号跨度。参数化 nodeid 映射到静态来源定义。
        """
        if (
            not self.complete
            or self.commit != base.commit
            or not environment
            or self.environment != environment
        ):
            return []
        tests = {test_nodeid(s): s for s in base.symbols.values() if s.kind == "test"}
        owners: dict[str, dict[int, Symbol]] = {}
        result = []
        for nodeid, data in self.tests.items():
            test = tests.get(nodeid.split("[", 1)[0])
            if test is None:
                continue
            for path, lines in data.items():
                unit = base.units.get(path)
                if unit is None:
                    continue
                if path not in owners:
                    index = {}
                    symbols = [
                        s for s in unit.symbols.values() if s.kind not in {"parameter", "variable"}
                    ]
                    for symbol in sorted(
                        symbols, key=lambda s: (s.line - s.end_line, s.kind != "module")
                    ):
                        for line in range(symbol.line, symbol.end_line + 1):
                            index[line] = symbol
                    owners[path] = index
                seen: set[str] = set()
                for line in lines:
                    symbol = owners[path].get(line)
                    if symbol is None or symbol.id in seen or symbol.id == test.id:
                        continue
                    seen.add(symbol.id)
                    result.append(
                        Edge(
                            test.id,
                            symbol.id,
                            EdgeType.COVERS,
                            test.path,
                            test.line,
                            test.column,
                            Confidence.RESOLVED,
                            "coverage-context",
                            f"{nodeid} covered {path}:{line}",
                        )
                    )
        return result


@dataclass(frozen=True, slots=True)
class Selection:
    """选择模式、候选用例及理由，以及要求执行全量套件的标记。"""

    mode: str
    run_all: bool
    tests: list[str]
    evidence: dict[str, list[str]]
    reasons: list[str]


def select(
    report: ImpactReport,
    snapshot: Snapshot,
    *,
    mode: str = "hybrid",
    coverage: CoverageMap | None = None,
    environment: str = "",
) -> Selection:
    """按 file、static、coverage 或 hybrid 生成用例与可追溯依据。

    coverage 校验基线、环境和采集完整性；hybrid 额外检查配置、动态关系和覆盖局限。run_all 由调用者或运行器执行。
    动态部分按实际映射路径与行范围匹配，成本取决于覆盖条目和变更区间。
    """
    if mode not in {"file", "static", "coverage", "hybrid"}:
        raise ValueError("unknown test selection mode")
    if report.target != snapshot.commit:
        raise ValueError("impact report and test inventory target differ")
    paths = {change.new_path for change in report.files if change.new_path}
    changed_lines = {
        change.old_path: change.old_ranges for change in report.files if change.old_path
    }
    impacted = {finding.symbol.path for finding in report.impacts}
    impacted_ids = {finding.symbol.id for finding in report.impacts}
    tests = [symbol for symbol in snapshot.symbols.values() if symbol.kind == "test"]
    reasons = set(report.fallback_reasons) if mode == "hybrid" else set()
    evidence: dict[str, set[str]] = {}

    def add(nodeid: str, criterion: str) -> None:
        evidence.setdefault(nodeid, set()).add(criterion)

    if mode in {"file", "static", "hybrid"}:
        for test in tests:
            if test.path in paths:
                add(test_nodeid(test), "modified test file")
            if mode in {"static", "hybrid"} and (test.id in impacted_ids or test.path in impacted):
                add(test_nodeid(test), "static reverse dependency")
    if mode in {"coverage", "hybrid"}:
        if coverage is None:
            reasons.add("coverage is unavailable")
        elif coverage.commit != report.base:
            reasons.add("coverage does not match the base commit")
        elif not environment or coverage.environment != environment:
            reasons.add("coverage environment differs or was unspecified")
        elif not coverage.complete:
            reasons.add("coverage session did not complete")
        else:
            if coverage.limitations and mode == "hybrid":
                reasons.update(coverage.limitations)
            for nodeid, covered in coverage.tests.items():
                file = nodeid.split("::", 1)[0]
                if file not in snapshot.units:
                    continue
                for path, lines in covered.items():
                    ranges = changed_lines.get(path, ())
                    if any(start <= line <= end for line in lines for start, end in ranges):
                        add(nodeid, f"coverage intersects removed or modified lines in {path}")
                    elif path in impacted or path in changed_lines:
                        add(nodeid, f"coverage intersects an affected module {path}")
    # If a base parametrized ID was selected, prefer the current static parent selector.
    for nodeid in list(evidence):
        parent = nodeid.split("[", 1)[0]
        if parent != nodeid and parent in evidence:
            evidence[parent].update(evidence.pop(nodeid))
    if mode == "hybrid" and report.files and not evidence:
        reasons.add("no test could be associated with the change")
    return Selection(
        mode,
        bool(reasons),
        sorted(evidence),
        {key: sorted(value) for key, value in sorted(evidence.items())},
        sorted(reasons),
    )
