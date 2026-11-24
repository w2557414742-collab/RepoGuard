# BFS、DFS 和 PageRank 对照

基于实际源码。

## 学习目标与原理

能区分最短跳数、有向环和全局重要度。 BFS 使用 FIFO 队列，DFS 常用于深度路径、时间戳和环分析。PageRank 通过迭代传播全局评分。

## 源码、函数与调用

影响与检索直接使用 walk。SCC 由 NetworkX 完成，生产检索暂无 PageRank。 [walk · src/repoguard/graph.py:79](../../src/repoguard/graph.py#L79-L124)

- [第 98 行](../../src/repoguard/graph.py#L98) 中的 `queue = deque(walked)`。初始化多源 FIFO。
- [第 101 行](../../src/repoguard/graph.py#L101) 中的 `node = queue.popleft()`。每次从队首取一层节点。
- [第 122 行](../../src/repoguard/graph.py#L122) 中的 `walked[target] = (*walked[node], edge)`。按首次到达保存已有路径及当前边。

## 数据结构、复杂度与选型

walked 保存首次证据路径，通过图的邻接边扩展。 BFS 本体 O(V+E)，额外有邻边排序及 O(V·D) 路径缓存。 有界 BFS 便于给出一致的证据链。

## Debug 与对应验证

在 `walk` 下断点，观察 `queue、node、walked`。[test_graph_walk_bounds](../../tests/integration/test_index_and_impact.py#L144)

## 独立练习

在六节点有环图中分别计算 BFS 和 DFS 访问次序，再设计 PageRank 比较实验。

## 面试追问

高 PageRank 节点和离种子最近的节点为什么会不同？

## 验收标准

列出两个 traversal 的结果、邻接方向和截断原因。
