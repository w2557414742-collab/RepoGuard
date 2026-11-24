"""分析、存储与传输共享的数据记录。模型层不依赖 CLI、Web 或 MCP。"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def identity(*parts: str) -> str:
    """用 NUL 分隔的身份组件形成确定性摘要，供仓库、符号与提交快照共同标识。"""
    return digest("\0".join(parts).encode())[:32]


class Confidence(StrEnum):
    RESOLVED = "RESOLVED"
    POSSIBLE = "POSSIBLE"
    UNRESOLVED = "UNRESOLVED"


class EdgeType(StrEnum):
    DEFINES = "DEFINES"
    CONTAINS = "CONTAINS"
    IMPORTS = "IMPORTS"
    CALLS = "CALLS"
    REFERENCES = "REFERENCES"
    INHERITS = "INHERITS"
    OVERRIDES = "OVERRIDES"
    DEPENDS_ON = "DEPENDS_ON"
    COVERS = "COVERS"


@dataclass(frozen=True, slots=True)
class File:
    """保存 Git 文件的路径、对象 ID、大小、状态和分析诊断。"""

    path: str
    oid: str
    size: int
    mode: str
    status: str
    detail: str = ""
    content_hash: str = ""
    encoding: str = ""
    lines: int = 0


@dataclass(frozen=True, slots=True)
class Symbol:
    """符号定义的稳定 ID、作用域、父符号、位置、签名和内容摘要。"""

    id: str
    repository_id: str
    module: str
    name: str
    qualified_name: str
    kind: str
    scope_id: str
    path: str
    line: int
    end_line: int
    column: int
    signature: str
    parent: str | None
    content_hash: str
    language: str = "python"
    intrinsically_uncertain: bool = False


@dataclass(frozen=True, slots=True)
class Binding:
    """记录名字能绑定到的定义或导入位置，包含出现时间与条件分支标记。"""

    kind: str
    line: int
    column: int = 0
    target: str = ""
    module: str = ""
    name: str = ""
    conditional: bool = False
    available_line: int = 0
    available_column: int = 0


@dataclass(slots=True)
class Scope:
    """词法作用域记录，包含父作用域、所有者、名字绑定表与 global/nonlocal 声明。"""

    id: str
    kind: str
    parent: str | None
    owner: str
    bindings: dict[str, list[Binding]] = field(default_factory=dict)
    globals: list[str] = field(default_factory=list)
    nonlocals: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class Usage:
    """第一遍遍历采集的引用事实。解析器随后决定边的目标和可信度。"""

    scope: str
    owner: str
    kind: str
    text: str
    line: int
    column: int
    module: str = ""
    name: str = ""


@dataclass(slots=True)
class Unit:
    """单个 Python 文件的语法事实缓存，包含模块、符号、作用域及引用。"""

    path: str
    module: str
    root_scope: str
    symbols: dict[str, Symbol]
    scopes: dict[str, Scope]
    usages: list[Usage]


@dataclass(frozen=True, slots=True)
class Edge:
    """跨快照可序列化的有向边证据。target 为空时保留源码位置和不确定性。"""

    source: str
    target: str | None
    kind: EdgeType
    path: str
    line: int
    column: int
    confidence: Confidence
    method: str
    expression: str = ""


@dataclass(slots=True)
class Snapshot:
    """一个 Git 提交和一组选项的文件清单、语法事实、关系、探测集合与收据。"""

    version: str
    repository_id: str
    commit: str
    options: str
    files: dict[str, File]
    units: dict[str, Unit]
    edges: dict[str, list[Edge]]
    footprints: dict[str, set[str]]
    metadata: dict[str, object]

    @property
    def symbols(self) -> dict[str, Symbol]:
        """按符号 ID 汇总各文件的符号。每次访问都创建字典，时间与额外空间均为 O(S)。"""
        return {sid: s for unit in self.units.values() for sid, s in unit.symbols.items()}


@dataclass(frozen=True, slots=True)
class FileChange:
    """两个 Git 树之间的文件状态、双侧路径和双侧行闭区间。"""

    status: str
    old_path: str | None
    new_path: str | None
    old_ranges: tuple[tuple[int, int], ...] = ()
    new_ranges: tuple[tuple[int, int], ...] = ()
