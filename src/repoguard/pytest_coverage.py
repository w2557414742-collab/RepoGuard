"""Pytest hooks for dynamic contexts and independent failure reporting."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from coverage import Coverage

_coverage: Coverage | None = None
_failures: set[str] = set()
_collected: list[str] = []
_collection_failed = False


def pytest_sessionstart(session: pytest.Session) -> None:
    """初始化测试会话计数；请求覆盖时创建仅针对仓库根的 Coverage 对象。"""
    global _coverage, _collection_failed
    _failures.clear()
    _collected.clear()
    _collection_failed = False
    if os.environ.get("REPOGUARD_COLLECT_COVERAGE") == "1":
        _coverage = Coverage(
            config_file=False,
            data_file=None,
            include=[str(session.config.rootpath / "*")],
        )
        _coverage.start()


def pytest_collection_finish(session: pytest.Session) -> None:
    _collected.extend(item.nodeid for item in session.items)


def pytest_collectreport(report: pytest.CollectReport) -> None:
    global _collection_failed
    _collection_failed |= report.failed


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_protocol(item: pytest.Item, nextitem: pytest.Item | None):
    """在完整 pytest 用例协议周围切换 Coverage 上下文，nodeid 包括参数，覆盖 setup 到 teardown。"""
    if _coverage is not None:
        _coverage.switch_context(item.nodeid)
    try:
        return (yield)
    finally:
        if _coverage is not None:
            _coverage.switch_context("")


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.failed:
        _failures.add(report.nodeid)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """把 Coverage 的行上下文汇总为用例映射，并记录未归因行、失败用例和采集完整性。"""
    global _coverage
    mapping: dict[str, dict[str, list[int]]] = {node: {} for node in _collected}
    unassigned = False
    if _coverage is not None:
        _coverage.stop()
        data = _coverage.get_data()
        root = session.config.rootpath.resolve()
        for filename in data.measured_files():
            try:
                relative = Path(filename).resolve().relative_to(root).as_posix()
            except ValueError:
                continue
            for line, contexts in data.contexts_by_lineno(filename).items():
                for context in contexts:
                    if context in mapping:
                        mapping[context].setdefault(relative, []).append(line)
                    elif not context:
                        unassigned = True
        _coverage = None
    payload = {
        "collected": _collected,
        "failures": sorted(_failures),
        "complete": int(exitstatus) in {0, 1} and not _collection_failed and bool(_collected),
        "tests": mapping,
        "limitations": (
            ["import or collection code ran outside a test context"] if unassigned else []
        ),
    }
    if destination := os.environ.get("REPOGUARD_PYTEST_RESULT"):
        Path(destination).write_text(json.dumps(payload), encoding="utf-8")
