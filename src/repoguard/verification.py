"""在内存中验证统一补丁的路径、上下文、语法和静态结构。"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, replace

from .impact import is_public
from .model import Confidence, EdgeType, File, Snapshot
from .parser import parse
from .repository import Repository, safe_relative
from .resolution import Catalog, Resolver

HUNK = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


@dataclass(frozen=True, slots=True)
class PatchValidation:
    """独立补丁预检的状态、诊断、公开接口差异和新增未解析调用。"""

    commit: str
    files: list[str]
    checks: dict[str, str]
    diagnostics: list[str]
    public_api_changes: list[str]
    new_unresolved_calls: int


def path_header(line: bytes, label: bytes) -> str | None:
    """仅解析统一差异中的可接受根路径或 /dev/null。非法路径产生 ValueError。"""
    if not line.startswith(label):
        raise ValueError("expected a unified diff file header")
    name = line[len(label) :].rstrip(b"\r\n").removesuffix(b"\t").decode("utf-8", "strict")
    if name == "/dev/null":
        return None
    prefix = "a/" if label == b"--- " else "b/"
    if not name.startswith(prefix) or not safe_relative(name[2:]) or not name.endswith(".py"):
        raise ValueError("diff paths must be safe repository-relative Python files")
    return name[2:]


def lf_lines(raw: bytes) -> list[bytes]:
    items = raw.split(b"\n")
    return [part + b"\n" for part in items[:-1]] + ([items[-1]] if items[-1] else [])


def apply_hunks(before: bytes, hunks: list[tuple[re.Match[bytes], list[bytes]]]) -> bytes:
    """按旧侧上下文和目标坐标顺序应用变更块，输出内存字节。重叠、计数或上下文不匹配时报错。"""
    original = lf_lines(before)
    cursor = 0
    output = []
    for header, rows in hunks:
        old_line, old_count, new_line, new_count = header.groups()
        remove, add = (
            int(old_count if old_count is not None else 1),
            int(new_count if new_count is not None else 1),
        )
        start = int(old_line) - int(remove != 0)
        if not cursor <= start <= len(original):
            raise ValueError("hunks overlap or point outside the committed file")
        output.extend(original[cursor:start])
        if len(output) != int(new_line) - int(add != 0):
            raise ValueError("target hunk coordinates are inconsistent")
        cursor = start
        for row in rows:
            action, content = row[:1], row[1:]
            if action in {b" ", b"-"}:
                if cursor >= len(original) or original[cursor] != content:
                    raise ValueError("hunk context differs from the selected commit")
                cursor += 1
                remove -= 1
            if action in {b" ", b"+"}:
                output.append(content)
                add -= 1
        if remove or add:
            raise ValueError("hunk counts do not match the diff payload")
    output.extend(original[cursor:])
    return b"".join(output)


def patch_entries(patch: str) -> list[tuple[str | None, str | None, list]]:
    """读取受限大小的统一 diff，按头和 hunk 解析双侧 Python 路径，校验声明跨度和缺换行标记。"""
    raw = patch.encode()
    if not raw or len(raw) > 2 * 1024 * 1024:
        raise ValueError("provide a unified Python diff of 1 byte–2 MiB")
    entries = []
    lines = lf_lines(raw)
    cursor = 0
    while cursor < len(lines):
        if lines[cursor].startswith(b"diff --git "):
            cursor += 1
            while cursor < len(lines) and lines[cursor].startswith(
                (
                    b"index ",
                    b"new file mode 100644",
                    b"deleted file mode 100644",
                )
            ):
                cursor += 1
        if cursor + 1 >= len(lines):
            raise ValueError("incomplete unified diff header")
        old = path_header(lines[cursor], b"--- ")
        new = path_header(lines[cursor + 1], b"+++ ")
        if not (old or new) or (old and new and old != new):
            raise ValueError("represent moves as one deletion and one addition")
        cursor += 2
        hunks = []
        while cursor < len(lines) and (match := HUNK.match(lines[cursor])):
            cursor += 1
            old_count, new_count = int(match.group(2) or 1), int(match.group(4) or 1)
            rows: list[bytes] = []
            while old_count > 0 or new_count > 0:
                if cursor >= len(lines) or lines[cursor][:1] not in {b"+", b"-", b" "}:
                    raise ValueError("truncated unified diff hunk")
                row = lines[cursor]
                old_count -= row[:1] != b"+"
                new_count -= row[:1] != b"-"
                if old_count < 0 or new_count < 0:
                    raise ValueError("hunk row exceeds declared span")
                cursor += 1
                if (
                    cursor < len(lines)
                    and lines[cursor].rstrip(b"\r\n") == b"\\ No newline at end of file"
                ):
                    row = row.removesuffix(b"\n")
                    cursor += 1
                rows.append(row)
            hunks.append((match, rows))
        if not hunks:
            raise ValueError("file entry has no textual hunks")
        entries.append((old, new, hunks))
    return entries


def validate_patch(repo: Repository, snapshot: Snapshot, patch: str) -> PatchValidation:
    """在固定提交的 blob 上匹配补丁并重解析改动文件。对照公开签名与新增未解析调用，返回状态与诊断。

    调用方负责审批及隔离执行回归。额外开销随补丁、受影响文件与重建的语义关系增长。
    """
    if repo.id != snapshot.repository_id:
        raise ValueError("patch validation requires the matching repository")
    units = dict(snapshot.units)
    roots = tuple(json.loads(snapshot.options)[2]["roots"])
    diagnostics = []
    changed: set[str] = set()
    for old, new, hunks in patch_entries(patch):
        path = new or old
        if path in changed:
            raise ValueError("patch contains duplicate file entries")
        changed.add(path)
        entry = snapshot.files.get(path)
        if old and (
            entry is None or entry.mode not in {"100644", "100755"} or entry.size > 2_000_000
        ):
            raise ValueError(f"{path} is missing or outside patch validation limits")
        if old is None and entry is not None:
            raise ValueError(f"{path} already exists in the base commit")
        source = next(repo.blobs([entry])) if old else b""
        content = apply_hunks(source, hunks)
        if new is None:
            if content:
                raise ValueError("deletion does not remove the entire file")
            units.pop(path, None)
            continue
        record = (
            replace(entry, size=len(content))
            if entry
            else File(path, "", len(content), "100644", "pending")
        )
        parsed, unit = parse(record, content, repo.id, roots)
        if not unit:
            diagnostics.append(f"{path}: {parsed.detail}")
        else:
            units[path] = unit
    checks = {
        "context": "passed",
        "syntax": "failed" if diagnostics else "passed",
        "reference_review": "not_run",
        "type_check": "not_run",
        "tests": "not_run",
    }
    if diagnostics:
        return PatchValidation(snapshot.commit, sorted(changed), checks, diagnostics, [], 0)
    old_contracts = {
        s.qualified_name: s.signature for s in snapshot.symbols.values() if is_public(s)
    }
    new_contracts = {
        s.qualified_name: s.signature
        for unit in units.values()
        for s in unit.symbols.values()
        if is_public(s)
    }
    api = sorted(name for name in old_contracts if old_contracts[name] != new_contracts.get(name))
    catalog = Catalog(units)
    edges = [edge for unit in units.values() for edge in Resolver(catalog).resolve(unit)[0]]

    def unresolved(part):
        return Counter(
            (edge.path, edge.expression)
            for edge in part
            if edge.kind == EdgeType.CALLS and edge.confidence == Confidence.UNRESOLVED
        )

    before = unresolved(e for group in snapshot.edges.values() for e in group)
    missing = sum((unresolved(edges) - before).values())
    checks["reference_review"] = "review_required" if missing else "no_new_unresolved_calls"
    return PatchValidation(snapshot.commit, sorted(changed), checks, diagnostics, api, missing)
