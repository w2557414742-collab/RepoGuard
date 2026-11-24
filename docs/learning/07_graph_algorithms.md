# 图遍历与强连通分量

## 前置知识

掌握有向多重图、BFS 和 SCC。

## 模块职责、输入与输出

CodeGraph 将 Snapshot 投影到多重有向图，walk 输出到目标的证据路径，cycles 输出模块循环。 [源码](../../src/repoguard/graph.py)。

## 算法、数据结构与成本

访问映射限制环上的重复。构图 O(V+E)，路径缓存上界 O(V·深度)。边过滤和邻接排序影响查询成本。

## 验证、工程边界与练习

限制节点预算为 1，再增加深度观察循环模块。核对 shortest_path 中每条边的方向。 [测试或实测证据](../../tests/integration/test_index_and_impact.py)。

## 面试题

最短跳数与最高风险路径的定义有什么差别？
