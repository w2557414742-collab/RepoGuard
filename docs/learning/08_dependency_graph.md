# 依赖多重图与循环

基于实际源码。

## 学习目标与原理

知道如何从边表获得模块依赖和 SCC。 多重图保留同一节点之间的多个源码证据，SCC 在筛选后的有向图上计算。

## 源码、函数与调用

CodeGraph 投影 Snapshot，架构与影响流程查询 cycles。 [cycles · src/repoguard/graph.py:139](../../src/repoguard/graph.py#L139-L151)

- [第 142 行](../../src/repoguard/graph.py#L142) 中的 `graph = nx.DiGraph(`。只投影指定关系的边。
- [第 149 行](../../src/repoguard/graph.py#L149) 中的 `for component in nx.strongly_connected_components(graph)`。为相互可达的节点计算分量。

## 数据结构、复杂度与选型

NetworkX MultiDiGraph 和强连通分量集合。 构图 O(V+E)，SCC 核心 O(V+E)，结果排序附加开销。 复用 NetworkX 的图算法，源码证据仍来自 Edge。

## Debug 与对应验证

在 `cycles` 下断点，观察 `kinds、graph、component`。[test_reference_resolution_and_graph](../../tests/integration/test_index_and_impact.py#L22)

## 独立练习

添加两模块相互引用，切换 DEPENDS_ON 与 CALLS 对比结果。

## 面试追问

双向可达意味着任意一条有向边一定是循环吗？

## 验收标准

给出环的分量和两侧真实依赖证据。
