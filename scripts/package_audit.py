"""只读统计工作区、候选提交和 Git 历史的逻辑大小。"""

from __future__ import annotations

import hashlib
import os
import stat
import subprocess
from collections import defaultdict
from pathlib import Path

from generate_source_guide import ROOT, git_paths

REPORT = ROOT / "PACKAGE_AUDIT.md"


def git(*args: str, data: bytes | None = None) -> bytes:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        input=data,
        capture_output=True,
        check=True,
    ).stdout


def inventory() -> tuple[dict[str, int], dict[str, int], list[str]]:
    """遍历普通本地文件，汇总逻辑字节数并记录跳过的路径。"""
    files: dict[str, int] = {}
    folders: dict[str, int] = {}
    skipped: list[str] = []
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)

    def walk(path: Path) -> int:
        total = 0
        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    absolute = Path(entry.path)
                    relative = absolute.relative_to(ROOT).as_posix()
                    if absolute == REPORT:
                        continue
                    try:
                        info = entry.stat(follow_symlinks=False)
                        if entry.is_symlink() or getattr(info, "st_file_attributes", 0) & reparse:
                            skipped.append(relative)
                        elif stat.S_ISDIR(info.st_mode):
                            total += walk(absolute)
                        elif stat.S_ISREG(info.st_mode):
                            files[relative] = info.st_size
                            total += info.st_size
                    except OSError:
                        skipped.append(relative)
        except OSError:
            skipped.append(path.relative_to(ROOT).as_posix())
        folders[path.relative_to(ROOT).as_posix()] = total
        return total

    walk(ROOT)
    return files, folders, sorted(skipped)


def duplicates(files: dict[str, int]) -> tuple[list[tuple[int, list[str]]], int]:
    """先按大小和前缀筛选，再对候选做完整 SHA-256 比较。"""
    sized: dict[int, list[str]] = defaultdict(list)
    for path, size in files.items():
        if size:
            sized[size].append(path)
    groups: list[tuple[int, list[str]]] = []
    skipped = 0
    for size, paths in sized.items():
        if len(paths) < 2:
            continue
        prefix: dict[bytes, list[str]] = defaultdict(list)
        for path in paths:
            try:
                with (ROOT / path).open("rb") as stream:
                    prefix[stream.read(1024)].append(path)
            except OSError:
                skipped += 1
        for candidates in prefix.values():
            if len(candidates) < 2:
                continue
            full: dict[str, list[str]] = defaultdict(list)
            for path in candidates:
                try:
                    with (ROOT / path).open("rb") as stream:
                        full[hashlib.file_digest(stream, "sha256").hexdigest()].append(path)
                except OSError:
                    skipped += 1
            groups.extend((size, sorted(paths)) for paths in full.values() if len(paths) > 1)
    return sorted(groups, key=lambda group: (-group[0] * (len(group[1]) - 1), group[1])), skipped


def history_blobs() -> list[tuple[int, str, str]]:
    """用对象 ID 查询本地 refs 可达 blob 的未压缩大小。"""
    records = git("rev-list", "--objects", "--all").decode("utf-8").splitlines()
    named = dict(line.split(" ", 1) for line in records if " " in line)
    if not named:
        return []
    rows = (
        git(
            "cat-file",
            "--batch-check=%(objectname) %(objecttype) %(objectsize)",
            data=("\n".join(named) + "\n").encode(),
        )
        .decode()
        .splitlines()
    )
    return sorted(
        (
            (int(size), oid, named[oid])
            for oid, kind, size in (row.split(" ") for row in rows)
            if kind == "blob"
        ),
        reverse=True,
    )


def ranked(values: dict[str, int]) -> list[tuple[str, int]]:
    return sorted(values.items(), key=lambda item: (-item[1], item[0]))


def amount(size: int) -> str:
    return f"{size:,} B ({size / 1_048_576:.2f} MiB)"


def main() -> None:
    """生成发布留档。只写报告，第三方克隆和历史数据保留原样。"""
    files, folders, skipped = inventory()
    candidate = {path: files[path] for path in git_paths() if path in files}
    tracked = {path for path in git("ls-files", "-z").decode().split("\0") if path}
    similarities, hash_skips = duplicates(files)
    history = history_blobs()
    report = [
        "# 体积与发布内容审计",
        "",
        (
            "按普通文件逻辑字节数统计当前工作区，包括 Git、环境、缓存和实验克隆。"
            "忽略重解析点、访问失败项及本报告自身。硬链接按路径计数。候选清单使用 Git 的跟踪和忽略规则。"
        ),
        "",
        f"- 本地合计 {amount(folders['.'])}，文件 {len(files):,}。",
        f"- Git 已跟踪 {len(tracked):,} 个路径，现有文件 {amount(sum(files.get(p, 0) for p in tracked))}。",
        f"- 可提交内容 {len(candidate):,} 个文件，{amount(sum(candidate.values()))}，本报告另计。",
        (
            f"- 本地 refs 可达 blob {len(history):,} 个，其中 ≥1 MiB 的对象 "
            f"{sum(size >= 1_048_576 for size, *_ in history):,} 个。"
        ),
        f"- 跳过路径 {len(skipped):,}，重复计算额外不可读文件 {hash_skips:,}。",
        (
            f"- 内容完全相同的重复组 {len(similarities):,}，按每组保留一份估算冗余 "
            f"{amount(sum(size * (len(paths) - 1) for size, paths in similarities))}。"
        ),
        "",
        "## 一级目录",
        "",
        "| 目录 | 本地大小 |",
        "|---|---:|",
    ]
    report.extend(
        f"| `{path}` | {amount(size)} |"
        for path, size in ranked(folders)
        if path != "." and "/" not in path
    )
    for title, selected in (
        ("最大的 30 个文件", ranked(files)[:30]),
        ("最大的 20 个目录", [(p, n) for p, n in ranked(folders) if p != "."][:20]),
        ("最大的 10 个可提交文件", ranked(candidate)[:10]),
    ):
        report.extend(["", f"## {title}", "", "| 路径 | 大小 |", "|---|---:|"])
        report.extend(f"| `{path}` | {amount(size)} |" for path, size in selected)
    report.extend(["", "## Git 历史大型对象", ""])
    large = [(size, oid, path) for size, oid, path in history if size >= 1_048_576]
    report.extend(f"- `{oid}` · `{path}` · {amount(size)}" for size, oid, path in large[:30])
    if not large:
        report.append("本次检查的可达 Git 历史中未发现 ≥1 MiB 的 blob。")
    report.extend(["", "## 重复组样例", ""])
    for size, paths in similarities[:8]:
        shown = "、".join(f"`{path}`" for path in paths[:3])
        report.append(f"- {amount(size)} × {len(paths)}，{shown}。")
    report.extend(
        [
            "",
            "## 发布清单与生成边界",
            "",
            "| 类别 | 文件与处理 |",
            "|---|---|",
            "| 自有源码与文档 | 保留 src、tests、scripts、infra、configs、前端源码及 npm 锁文件。SQLite schema 随 store.py 发布。 |",
            "| 必要实验材料 | 保留公开 Click 提交、人工标注、基准驱动、运行摘要、压缩覆盖行映射和上游许可。 |",
            "| 外部代码与依赖 | Click 公共克隆、其 Git 对象、venv、node_modules 和缓存保留本地，由清单重新生成。 |",
            "| 本地生成物 | SQLite 数据库、构建包、开发缓存和重复实验运行留在忽略目录。 |",
            "| 预留可再生工件 | Tree-sitter 语法缓存、FAISS、向量、权重、图导出、Docker 归档和卷备份有忽略规则。相关功能状态见 PROJECT_STATUS.md。 |",
            "",
            (
                "用 `python scripts/package_audit.py` 重新生成。发布前核对 "
                "`git ls-files -ci --exclude-standard`，若发现已跟踪的忽略项，确认后才仅从索引移除。"
            ),
            "",
        ]
    )
    REPORT.write_text("\n".join(report), encoding="utf-8", newline="\n")
    print(
        f"Audited {len(files):,} files, {len(candidate):,} release candidates, {len(history):,} Git blobs"
    )


if __name__ == "__main__":
    main()
