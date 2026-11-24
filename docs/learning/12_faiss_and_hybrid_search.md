# FAISS 规划与现有混合查询

混合检索 VERIFIED · FAISS NOT_IMPLEMENTED。

## 学习目标与原理

理解当前 RRF 与图扩展，规划向量索引对照。 RRF 融合名次，避免各分值单位不同。FAISS 属于未来候选召回策略。

## 源码、函数与调用

View.search_symbols 调 Search.hybrid。图扩展附加位置证据。 [hybrid · src/repoguard/retrieval.py:86](../../src/repoguard/retrieval.py#L86-L109)

- [第 96 行](../../src/repoguard/retrieval.py#L96) 中的 `expanded = graph.walk(exact[:5] or ranked[:3], depth=2, max_nodes=100) if graph else {}`。从精确或波次词法命中选种子进行有界扩展。
- [第 98 行](../../src/repoguard/retrieval.py#L98) 中的 `combined = reciprocal_rank((exact, ranked, evidence))`。合并精确、词法和图候选。

## 数据结构、复杂度与选型

当前使用候选 symbol ID、图路径和融合分值。 当前有词法排序与受限 BFS。未来平面向量查询约 O(N·d)。 向量后端要验证 recall@k、更新和模型版本一致性。

## Debug 与对应验证

在 `hybrid` 下断点，观察 `exact、evidence、combined`。[test_reciprocal_rank_ignores_duplicate_results](../../tests/integration/test_index_and_impact.py#L192)

## 独立练习

构造三个外部排名，比较 RRF 冲突；写出向量碰撞和冷启动评测。

## 面试追问

FAISS 索引何时应重建，何时能增量更新？

## 验收标准

准确描述当前三路排序和未来向量索引的插入位置。
