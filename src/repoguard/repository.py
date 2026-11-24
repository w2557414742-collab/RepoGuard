"""只读 Git 对象读取与版本差异。为索引和影响分析提供同一提交的文件视图。"""

from __future__ import annotations

import difflib
import os
import re
import subprocess
from collections.abc import Iterable, Iterator
from pathlib import Path, PurePosixPath

from .model import File, FileChange, identity

OBJECT_ID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
IGNORED = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "site-packages",
        "__pycache__",
        ".tox",
        ".nox",
        "vendor",
        "vendored",
        "build",
        "dist",
        "generated",
        ".mypy_cache",
        ".ruff_cache",
        ".pytest_cache",
        ".eggs",
    }
)
GENERATED_SUFFIXES = ("_pb2.py", "_pb2_grpc.py")


class RepositoryError(RuntimeError):
    pass


def safe_relative(path: str) -> bool:
    """检查 Git 路径是否能作为相对路径使用。拒绝空组件、上跳、控制字符和 Windows 分隔符。"""
    parts = path.split("/")
    return all(
        part and part not in {".", ".."} and not any(c in "\\:" or ord(c) < 32 for c in part)
        for part in parts
    )


def module_name(path: str, roots: tuple[str, ...]) -> str:
    """按最长匹配源码根把 .py 路径转换为点分模块名，包的 __init__.py 映射到包名。"""
    relative = path
    for root in sorted(roots, key=len, reverse=True):
        prefix = root.rstrip("/") + "/"
        if root != "." and path.startswith(prefix):
            relative = path[len(prefix) :]
            break
    parts = list(PurePosixPath(relative).with_suffix("").parts)
    if len(parts) > 1 and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


class Repository:
    """在受限 Git 环境中读取固定仓库，仓库身份从规范化本地路径派生。"""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve(strict=True)
        self._env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        self._env.update(
            GIT_NO_REPLACE_OBJECTS="1",
            GIT_TERMINAL_PROMPT="0",
            GIT_NO_LAZY_FETCH="1",
            GIT_OPTIONAL_LOCKS="0",
        )
        if (
            self.git("rev-parse", "--is-bare-repository").strip() != b"true"
            and self.git("rev-parse", "--show-prefix").strip()
        ):
            raise RepositoryError("provide the repository root")
        self.id = identity("repository", os.path.normcase(str(self.root)))

    def git(self, *args: str, data: bytes | None = None) -> bytes:
        """以参数数组执行 git -C，返回标准输出字节。Git 非零退出时报 RepositoryError，超时由 subprocess 上报。调用层负责修订和路径验证。"""
        result = subprocess.run(
            ["git", "-c", "core.fsmonitor=false", "-C", str(self.root), *args],
            env=self._env,
            input=data,
            capture_output=True,
            timeout=120,
            check=False,
        )
        if result.returncode:
            raise RepositoryError(result.stderr.decode("utf-8", "replace").strip())
        return result.stdout

    def commit(self, revision: str) -> str:
        """把 revision 解析为经过验证的完整提交对象 ID，供全部树、blob 和差异查询使用。"""
        oid = self.git("rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}")
        value = oid.decode("ascii").strip()
        if not OBJECT_ID.fullmatch(value):
            raise RepositoryError("Git returned an invalid commit ID")
        return value

    def inventory(self, commit: str, max_bytes: int) -> dict[str, File]:
        """读取提交的 NUL 分隔 Git 树，返回按路径索引的文件状态与 blob ID。扫描成本与树条目数和路径总长成正比。链接、子模块、超限文件及无效路径保留跳过诊断。"""
        commit = self.commit(commit)
        files: dict[str, File] = {}
        for record in self.git("ls-tree", "-r", "-l", "-z", commit).split(b"\0"):
            if not record:
                continue
            header, raw_path = record.split(b"\t", 1)
            mode, kind, oid, size = header.decode("ascii").split()
            path = raw_path.decode("utf-8", "surrogateescape")
            length = int(size) if size != "-" else 0
            status = "pending"
            if not safe_relative(path) or any(0xDC80 <= ord(c) <= 0xDCFF for c in path):
                path = raw_path.decode("utf-8", "backslashreplace")
                status = "unsafe_path"
            elif kind != "blob" or mode not in {"100644", "100755"}:
                status = "non_regular"
            elif set(path.split("/")) & IGNORED or path.endswith(GENERATED_SUFFIXES):
                status = "excluded"
            elif not path.endswith(".py"):
                status = "unsupported"
            elif length > max_bytes:
                status = "too_large"
            files[path] = File(path, oid, length, mode, status)
        return files

    def blobs(self, files: Iterable[File], batch_size: int = 4 * 1024 * 1024) -> Iterator[bytes]:
        """按总字节预算打包 blob 请求，保持输入顺序。批响应由 _batch 验证对象 ID、类型和长度。空间由单批字节与调用方保留的对象共同决定。"""
        batch: list[File] = []
        size = 0
        for file in files:
            if batch and size + file.size >= batch_size:
                yield from self._batch(batch)
                batch, size = [], 0
            batch.append(file)
            size += file.size
        if batch:
            yield from self._batch(batch)

    def _batch(self, files: list[File]) -> Iterator[bytes]:
        """用 cat-file --batch 读取原始 blob。响应头或预期长度不符会中止该批，避免数据错配。"""
        if any(not OBJECT_ID.fullmatch(file.oid) for file in files):
            raise RepositoryError("invalid blob ID")
        data = "\n".join(file.oid for file in files).encode("ascii") + b"\n"
        raw = self.git("cat-file", "--batch", data=data)
        offset = 0
        for file in files:
            end = raw.find(b"\n", offset)
            expected = f"{file.oid} blob {file.size}".encode("ascii")
            if end < 0 or raw[offset:end] != expected:
                raise RepositoryError(f"unexpected blob header for {file.path}")
            start, stop = end + 1, end + 1 + file.size
            if raw[stop : stop + 1] != b"\n":
                raise RepositoryError(f"truncated blob for {file.path}")
            yield raw[start:stop]
            offset = stop + 1

    def changes(
        self,
        base: str,
        target: str,
        *,
        with_lines: bool = False,
        max_bytes: int = 1_000_000,
    ) -> list[FileChange]:
        """比较两个提交，返回 Git 增删改和重命名记录。with_lines 开启时映射双方的一基闭区间。Git 的重命名结果是相似度判定，行映射受计算预算限制。"""
        base, target = self.commit(base), self.commit(target)
        raw = self.git(
            "diff-tree", "--no-commit-id", "-r", "-M", "--name-status", "-z", base, target
        )
        fields = iter(raw.removesuffix(b"\0").split(b"\0")) if raw else iter(())
        changes: list[FileChange] = []
        for tag in fields:
            first = next(fields).decode("utf-8", "backslashreplace")
            kind = tag[:1].decode("ascii")
            if kind in {"R", "C"}:
                second = next(fields).decode("utf-8", "backslashreplace")
                changes.append(FileChange(kind, first, second))
            else:
                changes.append(
                    FileChange(kind, first if kind != "A" else None, first if kind != "D" else None)
                )
        if not with_lines or not changes:
            return changes
        old, new = self.inventory(base, max_bytes), self.inventory(target, max_bytes)
        return [self._changed_lines(change, old, new, max_bytes) for change in changes]

    def _changed_lines(
        self,
        change: FileChange,
        base: dict[str, File],
        target: dict[str, File],
        max_bytes: int,
    ) -> FileChange:
        """用 SequenceMatcher 为文本生成双方的变更范围。大文件、二进制或非普通文件保留文件级结果，行数乘积过大时用整文件范围保守近似。"""
        left = base.get(change.old_path or "")
        right = target.get(change.new_path or "")
        entries = [file for file in (left, right) if file is not None]
        if left and right and left.oid == right.oid:
            return change
        if any(file.size > max_bytes or file.mode not in {"100644", "100755"} for file in entries):
            return change
        blobs = iter(self.blobs(entries))
        a = next(blobs).splitlines() if left else []
        b = next(blobs).splitlines() if right else []
        if any(b"\0" in line for line in (*a, *b)):
            return change
        # Bound worst-case SequenceMatcher work on adversarial repetitive input.
        if len(a) * len(b) > 4_000_000:
            return FileChange(
                change.status,
                change.old_path,
                change.new_path,
                ((1, len(a)),) if a else (),
                ((1, len(b)),) if b else (),
            )
        edits = difflib.SequenceMatcher(a=a, b=b, autojunk=True).get_opcodes()
        return FileChange(
            change.status,
            change.old_path,
            change.new_path,
            tuple((i + 1, j) for tag, i, j, _, _ in edits if tag != "equal" and i != j),
            tuple((i + 1, j) for tag, _, _, i, j in edits if tag != "equal" and i != j),
        )
