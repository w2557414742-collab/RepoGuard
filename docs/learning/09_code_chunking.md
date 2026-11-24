# 代码分块规划与现有符号文档

未来规划 · NOT_IMPLEMENTED。

## 学习目标与原理

区分符号元数据检索文档与正文片段。 现有候选由符号名称、限定名、签名和种类组成。独立正文切块和重叠窗口属于规划。

## 源码、函数与调用

View.searcher 由快照构造 Search，BM25 使用当前词项表。 [__init__ · src/repoguard/retrieval.py:44](../../src/repoguard/retrieval.py#L44-L53)

- [第 49 行](../../src/repoguard/retrieval.py#L49) 中的 `words = tokens(f"{s.name} {s.qualified_name} {s.signature} {s.kind}")`。当前文档通过符号字段形成。
- [第 52 行](../../src/repoguard/retrieval.py#L52) 中的 `self.postings[word][sid] = count`。候选 ID 是符号 ID，当前没有 chunk 标识。

## 数据结构、复杂度与选型

postings 和 lengths 以符号 ID 为键。未来 chunk 应记录稳定锚点与原始坐标。 现有构建与词项总数成正比；未来切块总量取决于重叠比例。 未来优先沿语法定义边界，并保留文件与版本出处。

## Debug 与对应验证

在 `__init__` 下断点，观察 `words、lengths、Counter`。[test_reference_resolution_and_graph](../../tests/integration/test_index_and_impact.py#L22)

## 独立练习

用虚构短模块设计按函数边界切块，在课程练习目录运行。

## 面试追问

变更三行代码时如何保留未变分块的缓存？

## 验收标准

能指出当前索引没有正文向量，并定义分块的文件回链格式。
