# 代码嵌入规划

未来规划 · NOT_IMPLEMENTED。

## 学习目标与原理

设计未来嵌入接口及独立评测。 把代码或符号描述映射到固定维度向量，可捕获不重复关键词的语义近邻。

## 源码、函数与调用

本版 Search.hybrid 以精确、词法和图为输入。未来嵌入可提供第四个排名。 [hybrid · src/repoguard/retrieval.py:86](../../src/repoguard/retrieval.py#L86-L109)

- [第 94 行](../../src/repoguard/retrieval.py#L94) 中的 `lexical = self.bm25(query)`。当前搜索的词法分支。
- [第 98 行](../../src/repoguard/retrieval.py#L98) 中的 `combined = reciprocal_rank((exact, ranked, evidence))`。未来插件可在这个排名融合边界接入。

## 数据结构、复杂度与选型

未来索引项关联模型版本、快照、符号或 chunk 与持久化向量。 推理随模型和长度变化，密集向量空间典型 O(N·d)。 先从许可明确、可复现的小型模型和公开标签对照开始。

## Debug 与对应验证

在 `hybrid` 下断点，观察 `lexical、ranked、combined`。[test_reciprocal_rank_ignores_duplicate_results](../../tests/integration/test_index_and_impact.py#L192)

## 独立练习

用三组手造向量证明 cosine 与 TF 排序可给出不同结果。

## 面试追问

换模型时如何使旧索引失效并避免版本混合？

## 验收标准

能给出模型、维度、规范化和持久化的契约，评测报告标记 NOT_RUN。
