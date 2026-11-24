"""符号元数据的精确、BM25 与图融合检索。"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from .graph import CodeGraph
from .model import Edge, Symbol


def tokens(text: str) -> list[str]:
    separated = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    return [token.casefold() for token in re.findall(r"[^\W_]+", separated)]


def reciprocal_rank(rankings: Iterable[Iterable[str]], k: int = 60) -> dict[str, float]:
    """按每个排名列表的倒数位置融合候选分数，单列表重复 ID 只贡献一次。k 必须大于零。"""
    if k <= 0:
        raise ValueError("k must be positive")
    scores: dict[str, float] = defaultdict(float)
    for ranking in rankings:
        for position, sid in enumerate(dict.fromkeys(ranking), 1):
            scores[sid] += 1 / (k + position)
    return dict(scores)


@dataclass(frozen=True, slots=True)
class Hit:
    """检索命中记录，含来源方法、融合得分、符号和可选图证据。"""

    symbol: Symbol
    score: float
    method: str
    evidence: tuple[Edge, ...] = ()


class Search:
    """为符号名称、签名和种类建立词项倒排表及文档长度统计。"""

    def __init__(self, symbols: dict[str, Symbol]) -> None:
        self.symbols = symbols
        self.postings: dict[str, dict[str, int]] = defaultdict(dict)
        self.lengths: dict[str, int] = {}
        for sid, s in symbols.items():
            words = tokens(f"{s.name} {s.qualified_name} {s.signature} {s.kind}")
            self.lengths[sid] = len(words)
            for word, count in Counter(words).items():
                self.postings[word][sid] = count
        self.average = sum(self.lengths.values()) / len(self.lengths) if self.lengths else 1

    def exact(self, query: str) -> list[Symbol]:
        """按 ID、限定名或短名扫描候选并稳定排序。短名可能返回多个符号。"""
        return sorted(
            (
                symbol
                for symbol in self.symbols.values()
                if query in {symbol.id, symbol.qualified_name, symbol.name}
            ),
            key=lambda s: (
                query != s.id,
                query != s.qualified_name,
                s.qualified_name,
                s.path,
                s.line,
            ),
        )

    def bm25(self, query: str) -> dict[str, float]:
        """遍历查询词对应倒排表，累加逆文档频率和长度归一化词频得分。

        时间受匹配 posting 长度支配，临时分数字典空间为候选数。
        """
        scores: dict[str, float] = defaultdict(float)
        for term in dict.fromkeys(tokens(query)):
            posting = self.postings.get(term, {})
            idf = math.log1p((len(self.symbols) - len(posting) + 0.5) / (len(posting) + 0.5))
            for sid, count in posting.items():
                normalizer = 1.2 * (0.25 + 0.75 * self.lengths[sid] / max(self.average, 1))
                scores[sid] += idf * (count * 2.2) / (count + normalizer)
        return dict(scores)

    def hybrid(self, query: str, limit: int = 20, graph: CodeGraph | None = None) -> list[Hit]:
        """合并精确、BM25 和可选图扩展，用 RRF 排序并限制返回数量。

        图分支从前几个检索候选进行有界 BFS，命中附带依赖证据。目前采用符号元数据索引。
        """
        if not 1 <= limit <= 200:
            raise ValueError("limit must be 1–200")
        exact = [s.id for s in self.exact(query)]
        lexical = self.bm25(query)
        ranked = sorted(lexical, key=lambda sid: (-lexical[sid], sid))
        expanded = graph.walk(exact[:5] or ranked[:3], depth=2, max_nodes=100) if graph else {}
        evidence = {sid: chain for sid, chain in expanded.items() if chain and sid in self.symbols}
        combined = reciprocal_rank((exact, ranked, evidence))
        return [
            Hit(
                self.symbols[sid],
                combined[sid],
                "exact" if sid in exact else "bm25" if sid in lexical else "graph",
                evidence.get(sid, ()),
            )
            for sid in sorted(combined, key=lambda sid: (sid not in exact, -combined[sid], sid))[
                :limit
            ]
        ]
