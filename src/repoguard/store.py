"""SQLite 事务快照与语法事实编解码。"""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .model import Binding, Confidence, Edge, EdgeType, File, Scope, Snapshot, Symbol, Unit, Usage

SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshot (
    version TEXT PRIMARY KEY,
    repository_id TEXT NOT NULL,
    commit_id TEXT NOT NULL,
    options TEXT NOT NULL,
    metadata TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS indexed_file (
    version TEXT NOT NULL REFERENCES snapshot(version),
    path TEXT NOT NULL,
    inventory TEXT NOT NULL,
    unit TEXT,
    footprint TEXT NOT NULL,
    PRIMARY KEY (version, path)
);
CREATE TABLE IF NOT EXISTS edge (
    version TEXT NOT NULL,
    path TEXT NOT NULL,
    ordinal INTEGER NOT NULL,
    source TEXT NOT NULL,
    target TEXT,
    kind TEXT NOT NULL,
    line INTEGER NOT NULL,
    column_number INTEGER NOT NULL,
    confidence TEXT NOT NULL,
    method TEXT NOT NULL,
    expression TEXT NOT NULL,
    FOREIGN KEY(version, path) REFERENCES indexed_file(version, path),
    PRIMARY KEY(version, path, ordinal)
);
CREATE INDEX IF NOT EXISTS edge_source ON edge(version, source, kind);
CREATE INDEX IF NOT EXISTS edge_target ON edge(version, target, kind);
"""


def serialize(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=False)


def decode_unit(raw: str) -> Unit:
    """把数据库中的 JSON 恢复成 Unit 和各级数据记录。调用方只读已经发布的版本。"""
    payload = json.loads(raw)
    for scope in payload["scopes"].values():
        scope["bindings"] = {
            name: [Binding(**b) for b in bindings] for name, bindings in scope["bindings"].items()
        }
    return Unit(
        payload["path"],
        payload["module"],
        payload["root_scope"],
        {sid: Symbol(**s) for sid, s in payload["symbols"].items()},
        {sid: Scope(**s) for sid, s in payload["scopes"].items()},
        [Usage(**usage) for usage in payload["usages"]],
    )


class Store:
    """用稳定版本键隔离 SQLite 中的提交快照、文件和边。"""

    def __init__(self, database: str | Path) -> None:
        self.database = Path(database)
        if str(self.database) == ":memory:":
            raise ValueError("provide a file-backed database")
        self.database.parent.mkdir(parents=True, exist_ok=True)
        with closing(self.connect()) as connection:
            connection.executescript(SCHEMA)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database, timeout=30)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def save(self, snapshot: Snapshot) -> bool:
        """在同一个 BEGIN IMMEDIATE 事务写入快照、文件和边。版本已存在时返回 False，由 Indexer 读取获胜快照。

        事务失败时 SQLite 回滚。写入时间与当前版本的文件、语法事实和边数量成正比。
        """
        with closing(self.connect()) as connection, connection:
            connection.execute("BEGIN IMMEDIATE")
            receipt = connection.execute(
                "INSERT OR IGNORE INTO snapshot VALUES (?, ?, ?, ?, ?)",
                (
                    snapshot.version,
                    snapshot.repository_id,
                    snapshot.commit,
                    snapshot.options,
                    serialize(snapshot.metadata),
                ),
            )
            if receipt.rowcount == 0:
                return False
            connection.executemany(
                "INSERT INTO indexed_file VALUES (?, ?, ?, ?, ?)",
                (
                    (
                        snapshot.version,
                        path,
                        serialize(asdict(file)),
                        serialize(asdict(snapshot.units[path])) if path in snapshot.units else None,
                        serialize(sorted(snapshot.footprints.get(path, ()))),
                    )
                    for path, file in snapshot.files.items()
                ),
            )
            connection.executemany(
                "INSERT INTO edge VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    (
                        snapshot.version,
                        path,
                        index,
                        e.source,
                        e.target,
                        e.kind,
                        e.line,
                        e.column,
                        e.confidence,
                        e.method,
                        e.expression,
                    )
                    for path, edges in snapshot.edges.items()
                    for index, e in enumerate(edges)
                ),
            )
        return True

    def load(self, version: str) -> Snapshot | None:
        """在同一个读取事务恢复特定版本的元数据、文件和边，并重建数据记录。不存在的版本返回 None。

        读取与内存开销随整个快照增长，是目前服务和增量路径的成本来源。
        """
        with closing(self.connect()) as connection:
            connection.execute("BEGIN")
            row = connection.execute(
                "SELECT repository_id, commit_id, options, metadata FROM snapshot WHERE version=?",
                (version,),
            ).fetchone()
            if row is None:
                return None
            repository, commit, options, metadata = row
            snapshot = Snapshot(
                version, repository, commit, options, {}, {}, {}, {}, json.loads(metadata)
            )
            for path, inventory, unit, footprint in connection.execute(
                "SELECT path, inventory, unit, footprint FROM indexed_file WHERE version=? "
                "ORDER BY path",
                (version,),
            ):
                snapshot.files[path] = File(**json.loads(inventory))
                if unit is not None:
                    snapshot.units[path] = decode_unit(unit)
                    snapshot.footprints[path] = set(json.loads(footprint))
                    snapshot.edges[path] = []
            for (
                path,
                source,
                target,
                kind,
                line,
                column,
                confidence,
                method,
                expr,
            ) in connection.execute(
                "SELECT path, source, target, kind, line, column_number, confidence, method, "
                "expression FROM edge WHERE version=? ORDER BY path, ordinal",
                (version,),
            ):
                snapshot.edges[path].append(
                    Edge(
                        source,
                        target,
                        EdgeType(kind),
                        path,
                        line,
                        column,
                        Confidence(confidence),
                        method,
                        expr,
                    )
                )
            return snapshot
