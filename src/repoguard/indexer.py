"""组织 Git 清单、并行语法解析、链接和快照原子发布。"""

from __future__ import annotations

import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from functools import partial
from itertools import islice
from time import perf_counter

from .model import File, Snapshot, Unit, identity
from .parser import parse
from .repository import Repository, module_name, safe_relative
from .resolution import Catalog, Resolver, module_prefixes, mutation_key, mutations
from .store import Store, serialize

INDEX_FORMAT = "3"


@dataclass(frozen=True, slots=True)
class IndexOptions:
    """规定源码根和单个文件字节上限，参与缓存版本键。"""

    roots: tuple[str, ...] = ("src", ".")
    max_file_bytes: int = 1_000_000

    def __post_init__(self) -> None:
        if not self.roots or any(root != "." and not safe_relative(root) for root in self.roots):
            raise ValueError("source roots must be repository-relative")
        if not 0 < self.max_file_bytes <= 16 * 1024 * 1024:
            raise ValueError("max_file_bytes must be between 1 byte and 16 MiB")

    @property
    def key(self) -> str:
        """序列化索引格式、解释器版本和分析选项。任一变化会生成不同的快照版本。"""
        return serialize([INDEX_FORMAT, list(sys.version_info[:3]), asdict(self)])


DEFAULT_OPTIONS = IndexOptions()


class Indexer:
    """合并 Git 对象、缓存语法事实和依赖失效，协调存储层发布索引。"""

    def __init__(
        self,
        repository: Repository,
        store: Store,
        options: IndexOptions = DEFAULT_OPTIONS,
        workers: int = 4,
    ) -> None:
        if not 1 <= workers <= 32:
            raise ValueError("workers must be between 1 and 32")
        self.repo, self.store, self.options, self.workers = repository, store, options, workers

    def version(self, commit: str) -> str:
        return identity(self.repo.id, commit, self.options.key)

    def load(self, revision: str = "HEAD") -> Snapshot | None:
        return self.store.load(self.version(self.repo.commit(revision)))

    def index(
        self,
        target: str = "HEAD",
        *,
        base: str | None = None,
        persist: bool = True,
        mode: str = "dependency",
    ) -> Snapshot:
        """按目标提交构建 Snapshot，可选使用基线提交。full 全量处理，file 复用文件事实，dependency 还复用未失效的链接。

        先枚举清单并比较对象 ID，再批量解析必要文件、计算依赖足迹的交集，最后由 Store 原子发布。
        文件枚举是 O(F)，其余受重解析字节、解析边和基线反序列化支配。并发写入接收已发布版本。存储当前读取和写入整版。
        """
        if mode not in {"dependency", "file", "full"}:
            raise ValueError("mode must be dependency, file, or full")
        start = perf_counter()
        commit = self.repo.commit(target)
        version = self.version(commit)
        if persist and (cached := self.store.load(version)):
            return cached
        previous = self.index(base) if base is not None and mode != "full" else None
        files = self.repo.inventory(commit, self.options.max_file_bytes)
        units: dict[str, Unit] = {}
        reparsed: list[File] = []
        reused: set[str] = set()
        for path, current in files.items():
            if current.status != "pending":
                continue
            old = previous.files.get(path) if previous else None
            if old is not None and old.oid == current.oid and old.mode == current.mode:
                files[path] = old
                if previous and path in previous.units:
                    units[path] = previous.units[path]
                    reused.add(path)
            else:
                reparsed.append(current)
        entries = iter(zip(reparsed, self.repo.blobs(reparsed), strict=True))
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            parse_entry = partial(_parse_entry, repo=self.repo.id, roots=self.options.roots)
            while batch := list(islice(entries, 2 * self.workers)):
                for file, unit in executor.map(parse_entry, batch):
                    files[file.path] = file
                    if unit is not None:
                        units[file.path] = unit
        units = dict(sorted(units.items()))
        catalog = Catalog(units)
        changed_paths = self._changed_paths(files, previous)
        changed_modules = self._changed_modules(changed_paths, units, previous, catalog)
        edges, footprints = {}, {}
        resolved_paths = []
        for path, unit in units.items():
            if (
                mode == "dependency"
                and previous
                and path in reused
                and not previous.footprints[path] & changed_modules
            ):
                edges[path] = previous.edges[path]
                footprints[path] = previous.footprints[path]
            else:
                edges[path], footprints[path] = Resolver(catalog).resolve(unit)
                resolved_paths.append(path)
        invalidated_paths = changed_paths | set(resolved_paths)
        invalidated_symbols = (
            sorted(
                {
                    sid
                    for path in invalidated_paths
                    for scope in (previous.units if previous else {}, units)
                    if path in scope
                    for sid in scope[path].symbols
                }
            )
            if previous
            else []
        )
        git_changes = self.repo.changes(previous.commit, commit) if previous else []
        metadata = {
            "index_version": version,
            "repository_id": self.repo.id,
            "base_commit": previous.commit if previous else None,
            "target_commit": commit,
            "strategy": mode if previous else "full",
            "file_status": dict(sorted(Counter(file.status for file in files.values()).items())),
            "file_count": len(files),
            "python_lines": sum(file.lines for file in files.values()),
            "symbols": sum(len(unit.symbols) for unit in units.values()),
            "edges": sum(len(items) for items in edges.values()),
            "edge_confidence": dict(Counter(e.confidence for part in edges.values() for e in part)),
            "test_symbols": sum(
                s.kind == "test" for u in units.values() for s in u.symbols.values()
            ),
            "updated_files": sorted(changed_paths),
            "parsed_files": [file.path for file in reparsed],
            "resolved_files": resolved_paths,
            "invalidated_symbols": invalidated_symbols,
            "updated_edges": sum(len(edges[path]) for path in resolved_paths),
            "removed_edge_count": sum(
                len(previous.edges.get(path, ())) for path in invalidated_paths
            )
            if previous
            else 0,
            "git_changes": [
                {
                    "status": change.status,
                    "old_path": change.old_path,
                    "new_path": change.new_path,
                    "old_ranges": [list(span) for span in change.old_ranges],
                    "new_ranges": [list(span) for span in change.new_ranges],
                }
                for change in git_changes
            ],
            "diagnostics": [
                asdict(file)
                for file in files.values()
                if file.status not in {"indexed", "unsupported"}
            ],
            "compute_seconds": perf_counter() - start,
        }
        snapshot = Snapshot(
            version,
            self.repo.id,
            commit,
            self.options.key,
            files,
            units,
            edges,
            footprints,
            metadata,
        )
        if persist and not self.store.save(snapshot):
            published = self.store.load(version)
            if published is None:
                raise RuntimeError("published snapshot disappeared")
            return published
        return snapshot

    @staticmethod
    def _changed_paths(files: dict[str, File], previous: Snapshot | None) -> set[str]:
        """比较双侧文件清单，保留新增、删除、对象变化及处理状态变动的路径。"""
        if previous is None:
            return set(files)
        return {
            path
            for path in files.keys() | previous.files.keys()
            if files.get(path) != previous.files.get(path)
        }

    def _changed_modules(
        self,
        paths: set[str],
        units: dict[str, Unit],
        previous: Snapshot | None,
        catalog: Catalog,
    ) -> set[str]:
        """用两版模块、命名空间和动态成员集合计算失效键。旧链接探测到的空模块也可能与新键匹配。"""
        if not previous:
            return set(catalog.modules) | catalog.namespaces
        changed = {
            module_name(path, self.options.roots)
            for path in paths
            if path in units or path in previous.units
        }
        old_namespaces = {
            prefix
            for unit in previous.units.values()
            for prefix in module_prefixes(unit.module) - {unit.module}
        }
        changed_members = {
            mutation_key(name)
            for name in (mutations(previous.units.values()) ^ catalog.mutated_members)
        }
        return changed | (old_namespaces ^ catalog.namespaces) | changed_members


def _parse_entry(
    entry: tuple[File, bytes],
    *,
    repo: str,
    roots: tuple[str, ...],
) -> tuple[File, Unit | None]:
    return parse(*entry, repo, roots)
